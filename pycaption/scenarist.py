import os
import tempfile
import zipfile
from collections import OrderedDict
from datetime import timedelta
from io import BytesIO

from PIL import Image, ImageFont, ImageDraw
from fontTools.ttLib import TTFont

from pycaption.base import BaseWriter, CaptionSet, Caption
from pycaption.geometry import UnitEnum, Size

HEADER = """st_format 2
SubTitle\tFace_Painting
Tape_Type\t{tape_type}
Display_Start\tnon_forced
Pixel_Area\t(2 479)
Display_Area\t(0 2 719 479)
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

    def get_font_with_all_glyphs_path(self, captions, font_paths):
        """
        Takes a list of captions and a list of font paths to search for fonts that include all glyphs that appear in
        the captions.
        @return: Font path or NoneType if no fonts are appropriate
        """
        def has_glyph(font, glyph):
            for table in font['cmap'].tables:
                if ord(glyph) in table.cmap.keys():
                    return True
            return False

        all_characters = []
        for caption_list in captions:
            for caption in caption_list:
                all_characters.extend([char for char in caption.get_text() if char and char.strip()])
        unique_characters = list(set(all_characters))

        chosen_font = None
        for font_candidate in font_paths:
            ttf_font = TTFont(font_candidate)
            glyphs = {c: has_glyph(ttf_font, c) for c in unique_characters}

            missing_glyphs = {k: v for k, v in glyphs.items() if not v}

            if not missing_glyphs:
                chosen_font = font_candidate
                break
        return chosen_font

    def write(self, caption_set: CaptionSet, position='bottom', avoid_same_next_start_prev_end=False):
        position = position.lower().strip()
        if position not in ScenaristDVDWriter.VALID_POSITION:
            raise ValueError('Unknown position. Supported: {}'.format(','.join(ScenaristDVDWriter.VALID_POSITION)))

        lang = caption_set.get_languages().pop()
        caps = caption_set.get_captions(lang)

        # group captions that have the same start time
        caps_start_time = OrderedDict()
        for i, cap in enumerate(caps):
            if cap.start not in caps_start_time:
                caps_start_time[cap.start] = [cap]
            else:
                caps_start_time[cap.start].append(cap)
        # order by start timestamp
        caps_start_time = OrderedDict(sorted(caps_start_time.items(), key=lambda item: item[0]))

        # check if captions with the same start time also have the same end time
        # fail if different end times are found - this is not (yet?) supported
        caps_final = []
        for start_time, caps_list in caps_start_time.items():
            if len(caps_list) == 1:
                caps_final.append(caps_list)
            else:
                end_times = list(set([c.end for c in caps_list]))
                if len(end_times) != 1:
                    raise ValueError('Unsupported subtitles - overlapping subtitles with different end times found')
                else:
                    caps_final.append(caps_list)

        if avoid_same_next_start_prev_end:
            for i, caps_list in enumerate(caps_final):
                if i == 0:
                    continue

                prev_end_time = caps_final[i-1][0].end
                current_start_time = caps_list[0].start

                if current_start_time == prev_end_time:
                    for c in caps_list:
                        c.start = min(c.start + ((1/self.frame_rate) * 1000000), c.end)

        # Determine if our fonts support all the glyphs in the source subtitle
        # Fonts are checked in the order in which they appear in the `font_paths` list.
        # The path to the  first font to include all the glyphs gets returned
        font_paths = [
            # I manually edited the TTF to include the note chars. See this issue for details:
            # https://github.com/googlefonts/noto-fonts/issues/1663
            f"{os.path.dirname(__file__)}/NotoSansDisplay-Regular-note.ttf",
            f"{os.path.dirname(__file__)}/NotoSansSC-Regular.otf",
        ]

        fnt = self.get_font_with_all_glyphs_path(caps_final, font_paths)
        if not fnt:
            raise ValueError('Cannot get font with all characters present)')
        fnt = ImageFont.truetype(fnt, 30)

        buf = BytesIO()
        with tempfile.TemporaryDirectory() as tmpDir:
            with open(tmpDir + '/subtitles.sst', 'w+') as sst:
                index = 1
                sst.write(HEADER.format(
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
                    self.printLine(draw, cap_list, fnt, position)

                    # quantize the image to our palette
                    img_quant = img.quantize(palette=self.palette_image, dither=0)
                    img_quant.save(tmpDir + '/subtitle%04d.tif' % index, compression="tiff_deflate")

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

    def printLine(self, draw: ImageDraw, caption_list: Caption, fnt: ImageFont, position: str = 'bottom'):
        for caption in caption_list:
            text = caption.get_text()
            l, t, r, b = draw.textbbox((0, 0), text, font=fnt)

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
                draw.text((x - adj, y), text, font=fnt, fill=borderColor)
                # move left
                draw.text((x + adj, y), text, font=fnt, fill=borderColor)
                # move up
                draw.text((x, y + adj), text, font=fnt, fill=borderColor)
                # move down
                draw.text((x, y - adj), text, font=fnt, fill=borderColor)
                # diagnal left up
                draw.text((x - adj, y + adj), text, font=fnt, fill=borderColor)
                # diagnal right up
                draw.text((x + adj, y + adj), text, font=fnt, fill=borderColor)
                # diagnal left down
                draw.text((x - adj, y - adj), text, font=fnt, fill=borderColor)
                # diagnal right down
                draw.text((x + adj, y - adj), text, font=fnt, fill=borderColor)

            draw.text((x, y), text, font=fnt, fill=fontColor)
