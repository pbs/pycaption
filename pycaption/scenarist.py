import os
import tempfile
import zipfile
from datetime import timedelta
from io import BytesIO

from PIL import Image, ImageFont, ImageDraw

from pycaption.base import BaseWriter, CaptionSet, Caption

HEADER = """st_format 2
SubTitle\tFace_Painting
Tape_Type\t{tape_type}
Display_Start\tnon_forced
Pixel_Area\t(2 479)
Display_Area\t(0 2 719 479)
Color\t(0 1 2 3)
Contrast\t(7 7 7 7)
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
    paColor = (255, 255, 255)  # letter body
    e1Color = (190, 190, 190)  # antialiasing color
    e2Color = (0, 0, 0)  # border color
    bgColor = (0, 255, 0)  # background color

    palette = [paColor, e1Color, e2Color, bgColor]

    palette_image = Image.new("P", (1, 1))
    palette_image.putpalette([*paColor, *e1Color, *e2Color, *bgColor] + [0, 0, 0] * 252)

    def __init__(self, relativize=True, video_width=720, video_height=480, fit_to_screen=True, tape_type='NON_DROP',
                 frame_rate=25):
        super().__init__(relativize, video_width, video_height, fit_to_screen)
        self.tape_type = tape_type
        self.frame_rate = frame_rate

    def write(self, caption_set: CaptionSet):
        lang = caption_set.get_languages().pop()
        caps = caption_set.get_captions(lang)

        buf = BytesIO()

        # https://github.com/googlefonts/noto-fonts/issues/1663
        fnt = ImageFont.truetype(os.path.dirname(__file__) + '/NotoSansDisplay-Regular.ttf', 30)

        with tempfile.TemporaryDirectory() as tmpDir:
            with open(tmpDir + '/subtitles.sst', 'w+') as sst:
                index = 1
                sst.write(HEADER.format(
                    bg_red=self.bgColor[0], bg_green=self.bgColor[1], bg_blue=self.bgColor[2],
                    pa_red=self.paColor[0], pa_green=self.paColor[1], pa_blue=self.paColor[2],
                    e1_red=self.e1Color[0], e1_green=self.e1Color[1], e1_blue=self.e1Color[2],
                    e2_red=self.e2Color[0], e2_green=self.e2Color[1], e2_blue=self.e2Color[2],
                    tape_type=self.tape_type,
                ))
                for cap in caps:
                    sst.write("%04d %s %s subtitle%04d.tif\n" % (
                        index,
                        self.format_ts(cap.start),
                        self.format_ts(cap.end),
                        index
                    ))

                    img = Image.new('RGB', (self.video_width, self.video_height), self.bgColor)
                    draw = ImageDraw.Draw(img)
                    self.printLine(draw, cap, fnt)

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
        if str_value.startswith('0:'):
            str_value = '0' + str_value
        str_value = str_value + ':%02d' % (int((int(value / 1000) % 1000) / int(1000 / self.frame_rate)))
        return str_value

    def printLine(self, draw: ImageDraw, caption: Caption, fnt: ImageFont):
        text = caption.get_text()

        txtWidth, txtHeight = draw.textsize(text, font=fnt)
        x = self.video_width / 2 - txtWidth / 2
        y = self.video_height - txtHeight - 10  # padding for readability

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
