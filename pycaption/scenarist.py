import os
import tempfile
import zipfile
from collections import OrderedDict
from datetime import timedelta
from io import BytesIO

from PIL import Image, ImageFont, ImageDraw
import arabic_reshaper
from bidi.algorithm import get_display
from fontTools.ttLib import TTFont
from langcodes import Language, tag_distance

from pycaption.base import BaseWriter, CaptionSet, Caption, CaptionNode
from pycaption.geometry import UnitEnum, Size


def get_sst_pixel_display_params(video_width, video_height):
    py0 = 2
    py1 = video_height - 1

    dx0 = 0
    dy0 = 2

    dx1 = video_width - 1
    dy1 = video_height - 1

    return py0, py1, dy0, dy1, dx0, dx1


HEADER = """st_format 2
SubTitle\tFace_Painting
Tape_Type\t{tape_type}
Display_Start\tnon_forced
Pixel_Area\t({py0} {py1})
Display_Area\t({dx0} {dy0} {dx1} {dy1})
Color\t{color}
Contrast\t{contrast}
BG\t({bg_red} {bg_green} {bg_blue} = = =)
PA\t({pa_red} {pa_green} {pa_blue} = = =)
E1\t({e1_red} {e1_green} {e1_blue} = = =)
E2\t({e2_red} {e2_green} {e2_blue} = = =)
directory\tC:\\
Base_Time\t00:00:00:00
################################################
SP_NUMBER START END FILE_NAME
"""

a = """
0001 01:00:30:12 01:00:35:08 eng0001.tif
0002 01:00:35:13 01:00:40:07 eng0002.tif
0003 01:00:41:17 01:00:44:08 eng0003.tif
0004 01:00:44:13 01:00:48:02 eng0004.tif

"""


def zipit(path, arch, mode='w'):
    archive = zipfile.ZipFile(arch, mode, zipfile.ZIP_DEFLATED)
    if os.path.isdir(path):
        if not path.endswith('tmp'):
            _zippy(path, path, archive)
    else:
        _, name = os.path.split(path)
        archive.write(path, name)
    archive.close()


def _zippy(base_path, path, archive):
    paths = os.listdir(path)
    for p in paths:
        p = os.path.join(path, p)
        if os.path.isdir(p):
            _zippy(base_path, p, archive)
        else:
            archive.write(p, os.path.relpath(p, base_path))


class ScenaristDVDWriter(BaseWriter):
    VALID_POSITION = ['top', 'bottom', 'source']

    paColor = (255, 255, 255)  # letter body
    e1Color = (190, 190, 190)  # antialiasing color
    e2Color = (0, 0, 0)  # border color
    bgColor = (0, 255, 0)  # background color

    palette = [paColor, e1Color, e2Color, bgColor]

    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette([*paColor, *e1Color, *e2Color, *bgColor] + [0, 0, 0] * 252)

    font_langs = {
        Language.get('en'): {'fontfile': f"{os.path.dirname(__file__)}/NotoSansDisplay-Regular-Note-Math.ttf",
                             'align': 'left'},
        Language.get('ru'): {'fontfile': f"{os.path.dirname(__file__)}/NotoSansDisplay-Regular-Note-Math.ttf",
                             'align': 'left'},
        Language.get('ar'): {'fontfile': f"{os.path.dirname(__file__)}/NotoSansDisplay-RegularAndArabic.ttf", 'align': 'right'},
        Language.get('ja-JP'): {'fontfile': f"{os.path.dirname(__file__)}/NotoSansCJKjp-Regular.otf", 'align': 'left'},
        Language.get('zh-TW'): {'fontfile': f"{os.path.dirname(__file__)}/NotoSansCJKtc-Regular.otf", 'align': 'left'},
        Language.get('zh-CN'): {'fontfile': f"{os.path.dirname(__file__)}/NotoSansCJKsc-Regular.otf", 'align': 'left'},
        Language.get('ko-KR'): {'fontfile': f"{os.path.dirname(__file__)}/NotoSansCJKkr-Regular.otf", 'align': 'left'},
    }

    def __init__(self, relativize=True, video_width=720, video_height=480, fit_to_screen=True, tape_type='NON_DROP',
                 frame_rate=25, compat=False):
        super().__init__(relativize, video_width, video_height, fit_to_screen)
        self.tape_type = tape_type
        self.frame_rate = frame_rate

        if compat:
            self.color = '(1 2 3 4)'
            self.contrast = '(15 15 15 0)'
        else:
            self.color = '(0 1 2 3)'
            self.contrast = '(7 7 7 7)'

    def get_characters(self, captions):
        all_characters = []
        for caption_list in captions:
            for caption in caption_list:
                all_characters.extend([char for char in caption.get_text() if char and char.strip()])
        unique_characters = list(set(all_characters))
        return unique_characters

    def get_characters_with_captions(self, captions):  # -> dict[str, list[int]]:
        chars_with_captions = {}
        for caption_list in captions:
            for caption in caption_list:
                current_caption_chars = [char for char in caption.get_text() if char and char.strip()]
                for char in current_caption_chars:
                    if char not in chars_with_captions:
                        chars_with_captions[char] = []
                    chars_with_captions[char].append(caption)
        return chars_with_captions

    def get_missing_glyphs(self, font, characters):
        ttf_font = TTFont(font)
        glyphs = {c: self._has_glyph(ttf_font, c) for c in characters}

        missing_glyphs = {k: v for k, v in glyphs.items() if not v}

        return missing_glyphs

    @staticmethod
    def _has_glyph(fnt, glyph):
        NOT_ACTUAL_GLYPHS = [
            '\u202A',  # Left-to-Right Embedding (LRE)
            '\u202B',  # Right-to-Left Embedding (RLE)
            '\u202C',  # Pop Directional Formatting (PDF)
            '\u202D',  # Left-to-Right Override (LRO)
            '\u202E',  # Right-to-Left Override (RLO)
            '\u200E',  # Left-to-Right Mark (LRM)
            '\u200F'  # Right-to-Left Mark (RLM)
        ]

        if glyph in NOT_ACTUAL_GLYPHS:
            return True

        for table in fnt['cmap'].tables:
            if ord(glyph) in table.cmap.keys():
                return True

        return False

    def get_missing_glyphs_with_timestamps(
            self, font, characters_with_timestamps  # : dict[str, list[int]]
    ):  # -> dict[str, list[int]]:
        ttf_font = TTFont(font)

        missing_glyphs_with_timestamps = {}
        for glyph, timestamps in characters_with_timestamps.items():
            is_glyph_in_font = self._has_glyph(ttf_font, glyph)
            if not is_glyph_in_font:
                missing_glyphs_with_timestamps[glyph] = timestamps

        return missing_glyphs_with_timestamps

    @staticmethod
    def group_captions_by_start_time(caps):
        # group captions that have the same start time
        caps_start_time = OrderedDict()
        for i, cap in enumerate(caps):
            if cap.start not in caps_start_time:
                caps_start_time[cap.start] = [cap]
            else:
                caps_start_time[cap.start].append(cap)

        # order by start timestamp
        caps_start_time = OrderedDict(sorted(caps_start_time.items(), key=lambda item: item[0]))
        return caps_start_time

    def check_overlapping_subs(self, captions_by_start_time):
        caps_final = []
        overlapping = []
        for start_time, caps_list in captions_by_start_time.items():
            if len(caps_list) == 1:
                caps_final.append(caps_list)
            else:
                end_times = list(set([c.end for c in caps_list]))
                if len(end_times) != 1:
                    overlapping.append(caps_list)
                else:
                    caps_final.append(caps_list)
        return caps_final, overlapping

    def get_distances(self, lang, font_langs):
        requested_lang = Language.get(lang)
        distances = [
            (tag_distance(requested_lang, l), fnt)
            for l, fnt in font_langs.items()
            if tag_distance(requested_lang, l) < 100
        ]
        if not distances:
            return distances

        distances.sort(key=lambda l: l[0])
        return distances

    def write(
            self,
            caption_set: CaptionSet,
            position='bottom',
            avoid_same_next_start_prev_end=False,
            tiff_compression='tiff_deflate',
    ):
        if tiff_compression not in ['tiff_deflate', 'raw']:
            raise ValueError('Unknown tiff_compression. Supported: {}'.format('tiff_deflate, raw'))

        position = position.lower().strip()
        if position not in ScenaristDVDWriter.VALID_POSITION:
            raise ValueError('Unknown position. Supported: {}'.format(','.join(ScenaristDVDWriter.VALID_POSITION)))

        lang = caption_set.get_languages().pop()
        caps = caption_set.get_captions(lang)

        # group captions that have the same start time
        caps_start_time = self.group_captions_by_start_time(caps)

        # check if captions with the same start time also have the same end time
        # fail if different end times are found - this is not (yet?) supported
        caps_final, overlapping = self.check_overlapping_subs(caps_start_time)
        if overlapping:
            raise ValueError('Unsupported subtitles - overlapping subtitles with different end times found')

        if avoid_same_next_start_prev_end:
            min_diff = (1 / self.frame_rate) * 1000000
            for i, caps_list in enumerate(caps_final):
                if i == 0:
                    continue

                prev_end_time = caps_final[i - 1][0].end
                current_start_time = caps_list[0].start

                if (current_start_time == prev_end_time) or ((current_start_time - prev_end_time) < min_diff):
                    for c in caps_list:
                        c.start = min(c.start + min_diff, c.end)

        distances = self.get_distances(lang, self.font_langs)
        if not distances:
            raise ValueError('Cannot find appropriate font for selected language')

        fnt = distances[0][1]['fontfile']
        align = distances[0][1]['align']
        missing_glyphs = self.get_missing_glyphs(fnt, self.get_characters(caps_final))

        if missing_glyphs:
            raise ValueError(f'Selected font was missing glyphs: {" ".join(missing_glyphs.keys())}')

        font_size = 30
        if self.video_width < 500:
            font_size = 16

        print(font_size)

        fnt = ImageFont.truetype(fnt, font_size)

        buf = BytesIO()
        with tempfile.TemporaryDirectory() as tmpDir:
            with open(tmpDir + '/subtitles.sst', 'w+') as sst:
                index = 1
                py0, py1, dy0, dy1, dx0, dx1 = get_sst_pixel_display_params(self.video_width, self.video_height)
                sst.write(HEADER.format(
                    py0=py0, py1=py1,
                    dx0=dx0, dy0=dy0, dx1=dx1, dy1=dy1,
                    bg_red=self.bgColor[0], bg_green=self.bgColor[1], bg_blue=self.bgColor[2],
                    pa_red=self.paColor[0], pa_green=self.paColor[1], pa_blue=self.paColor[2],
                    e1_red=self.e1Color[0], e1_green=self.e1Color[1], e1_blue=self.e1Color[2],
                    e2_red=self.e2Color[0], e2_green=self.e2Color[1], e2_blue=self.e2Color[2],
                    tape_type=self.tape_type, color=self.color, contrast=self.contrast
                ))

                for i, cap_list in enumerate(caps_final):
                    sst.write("%04d %s %s subtitle%04d.tif\n" % (
                        index,
                        self.format_ts(cap_list[0].start),
                        self.format_ts(cap_list[0].end),
                        index
                    ))

                    img = Image.new('RGB', (self.video_width, self.video_height), self.bgColor)
                    draw = ImageDraw.Draw(img)
                    self.printLine(draw, cap_list, fnt, position, align)

                    # quantize the image to our palette
                    img_quant = img.quantize(palette=self.palette_image, dither=0)
                    img_quant.save(tmpDir + '/subtitle%04d.tif' % index, compression=tiff_compression)

                    index = index + 1
            zipit(tmpDir, buf)
        buf.seek(0)
        return buf.read()

    def format_ts(self, value):
        datetime_value = timedelta(seconds=(int(value / 1000000)))
        str_value = str(datetime_value)[:11]

        # make sure all numbers are padded with 0 to two places
        str_value = ':'.join([n.zfill(2) for n in str_value.split(':')])

        str_value = str_value + ':%02d' % (int((int(value / 1000) % 1000) / int(1000 / self.frame_rate)))
        return str_value

    def printLine(self, draw: ImageDraw, caption_list: Caption, fnt: ImageFont, position: str = 'bottom', align: str = 'left'):
        for caption in caption_list:
            text = caption.get_text()
            l, t, r, b = draw.textbbox((0, 0), text, font=fnt, align=align)

            x = None
            y = None

            # if position is specified as source, get the layout info
            # fall back to "bottom" position if we can't get it
            if position == 'source':
                try:
                    x_ = caption.layout_info.origin.x
                    y_ = caption.layout_info.origin.y

                    if isinstance(x_, Size) \
                            and isinstance(y_, Size) \
                            and x_.unit == UnitEnum.PERCENT \
                            and y_.unit == UnitEnum.PERCENT:
                        x = self.video_width * (x_.value / 100)
                        y = self.video_height * (y_.value / 100)

                        # make sure the text doesn't go out of the screen
                        box_rightmost_edge = x + r
                        if box_rightmost_edge > self.video_width:
                            x = float(self.video_width) - float(r) - float(10)

                        # padding for readability
                        if y_.value > 70:
                            y = y - 10
                    else:
                        position = 'bottom'
                except:
                    position = 'bottom'

            if position != 'source':
                x = self.video_width / 2 - r / 2
                if position == 'bottom':
                    y = self.video_height - b - 10  # padding for readability
                elif position == 'top':
                    y = 10
                else:
                    raise ValueError('Unknown "position": {}'.format(position))

            borderColor = self.e2Color
            fontColor = self.paColor
            for adj in range(2):
                # move right
                draw.text((x - adj, y), text, font=fnt, fill=borderColor, align=align)
                # move left
                draw.text((x + adj, y), text, font=fnt, fill=borderColor, align=align)
                # move up
                draw.text((x, y + adj), text, font=fnt, fill=borderColor, align=align)
                # move down
                draw.text((x, y - adj), text, font=fnt, fill=borderColor, align=align)
                # diagnal left up
                draw.text((x - adj, y + adj), text, font=fnt, fill=borderColor, align=align)
                # diagnal right up
                draw.text((x + adj, y + adj), text, font=fnt, fill=borderColor, align=align)
                # diagnal left down
                draw.text((x - adj, y - adj), text, font=fnt, fill=borderColor, align=align)
                # diagnal right down
                draw.text((x + adj, y - adj), text, font=fnt, fill=borderColor, align=align)

            draw.text((x, y), text, font=fnt, fill=fontColor, align=align)
