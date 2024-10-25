import codecs
import struct

import logging

import unicodedata
from io import BytesIO

from pycaption.base import BaseReader, Caption, CaptionNode, CaptionSet, CaptionList

lang_code = {
    b"00": "und",
    b"16": "smi",
    b"01": "sq",
    b"17": "la",
    b"02": "br",
    b"18": "lv",
    b"03": "ca",
    b"19": "lb",
    b"04": "hr",
    b"1A": "lt",
    b"05": "cy",
    b"1B": "hu",
    b"06": "cs",
    b"1C": "mt",
    b"07": "da",
    b"1D": "nl",
    b"08": "de",
    b"1E": "no",
    b"09": "en",
    b"1F": "oc",
    b"0A": "es",
    b"20": "pl",
    b"0B": "eo",
    b"21": "po",
    b"0C": "et",
    b"22": "ro",
    b"0D": "eu",
    b"23": "rm",
    b"0E": "fo",
    b"24": "sr",
    b"0F": "fr",
    b"25": "sk",
    b"10": "fy",
    b"26": "sl",
    b"11": "ga",
    b"27": "fi",
    b"12": "gd",
    b"28": "sv",
    b"13": "gl",
    b"29": "sl",
    b"14": "is",
    b"2A": "nl",
    b"15": "it",
    b"2B": "wa",
    b"7F": "am",
    b"69": "ja",
    b"53": "sn",
    b"7E": "ar",
    b"68": "kn",
    b"52": "si",
    b"7D": "hy",
    b"67": "kk",
    b"51": "so",
    b"7C": "as",
    b"66": "km",
    b"50": "srn",
    b"7B": "az",
    b"65": "ko",
    b"4F": "sw",
    b"7A": "bm",
    b"64": "lo",
    b"4E": "tg",
    b"79": "be",
    b"63": "mk",
    b"4D": "ta",
    b"78": "bn",
    b"62": "mg",
    b"4C": "tt",
    b"77": "bg",
    b"61": "zsm",
    b"4B": "te",
    b"76": "my",
    b"60": "mo",
    b"4A": "th",
    b"75": "cmn-Hant",
    b"5F": "mr",
    b"49": "uk",
    b"74": "cv",
    b"5E": "nd",
    b"48": "ur",
    b"73": "prs",
    b"5D": "ne",
    b"47": "uz",
    b"72": "ff",
    b"5C": "ory",
    b"46": "vi",
    b"71": "ka",
    b"5B": "pap",
    b"45": "zu",
    b"70": "grk",
    b"5A": "fa",
    b"6F": "gu",
    b"59": "pa",
    b"6E": "gug",
    b"58": "ps",
    b"6D": "ha",
    b"57": "qu",
    b"6C": "he",
    b"56": "ru",
    b"6B": "hi",
    b"55": "rue",
    b"6A": "id",
    b"54": "sh",
}


class iso6937(codecs.Codec):
    identical = set(range(0x20, 0x7F))
    identical |= {
        0xA,
        0xA0,
        0xA1,
        0xA2,
        0xA3,
        0xA5,
        0xA7,
        0xAB,
        0xB0,
        0xB1,
        0xB2,
        0xB3,
        0xB5,
        0xB6,
        0xB7,
        0xBB,
        0xBC,
        0xBD,
        0xBE,
        0xBF,
    }
    direct_mapping = {
        0x8A: 0x000A,  # line break
        0xA8: 0x00A4,  # ¤
        0xA9: 0x2018,  # ‘
        0xAA: 0x201C,  # “
        0xAB: 0x00AB,  # «
        0xAC: 0x2190,  # ←
        0xAD: 0x2191,  # ↑
        0xAE: 0x2192,  # →
        0xAF: 0x2193,  # ↓
        0xB4: 0x00D7,  # ×
        0xB8: 0x00F7,  # ÷
        0xB9: 0x2019,  # ’
        0xBA: 0x201D,  # ”
        0xBC: 0x00BC,  # ¼
        0xBD: 0x00BD,  # ½
        0xBE: 0x00BE,  # ¾
        0xBF: 0x00BF,  # ¿
        0xD0: 0x2015,  # ―
        0xD1: 0x00B9,  # ¹
        0xD2: 0x00AE,  # ®
        0xD3: 0x00A9,  # ©
        0xD4: 0x2122,  # ™
        0xD5: 0x266A,  # ♪
        0xD6: 0x00AC,  # ¬
        0xD7: 0x00A6,  # ¦
        0xDC: 0x215B,  # ⅛
        0xDD: 0x215C,  # ⅜
        0xDE: 0x215D,  # ⅝
        0xDF: 0x215E,  # ⅞
        0xE0: 0x2126,  # Ohm Ω
        0xE1: 0x00C6,  # Æ
        0xE2: 0x0110,  # Đ
        0xE3: 0x00AA,  # ª
        0xE4: 0x0126,  # Ħ
        0xE6: 0x0132,  # Ĳ
        0xE7: 0x013F,  # Ŀ
        0xE8: 0x0141,  # Ł
        0xE9: 0x00D8,  # Ø
        0xEA: 0x0152,  # Œ
        0xEB: 0x00BA,  # º
        0xEC: 0x00DE,  # Þ
        0xED: 0x0166,  # Ŧ
        0xEE: 0x014A,  # Ŋ
        0xEF: 0x0149,  # ŉ
        0xF0: 0x0138,  # ĸ
        0xF1: 0x00E6,  # æ
        0xF2: 0x0111,  # đ
        0xF3: 0x00F0,  # ð
        0xF4: 0x0127,  # ħ
        0xF5: 0x0131,  # ı
        0xF6: 0x0133,  # ĳ
        0xF7: 0x0140,  # ŀ
        0xF8: 0x0142,  # ł
        0xF9: 0x00F8,  # ø
        0xFA: 0x0153,  # œ
        0xFB: 0x00DF,  # ß
        0xFC: 0x00FE,  # þ
        0xFD: 0x0167,  # ŧ
        0xFE: 0x014B,  # ŋ
        0xFF: 0x00AD,  # Soft hyphen
    }
    diacritic = {
        0xC1: 0x0300,  # grave accent
        0xC2: 0x0301,  # acute accent
        0xC3: 0x0302,  # circumflex
        0xC4: 0x0303,  # tilde
        0xC5: 0x0304,  # macron
        0xC6: 0x0306,  # breve
        0xC7: 0x0307,  # dot
        0xC8: 0x0308,  # umlaut
        0xCA: 0x030A,  # ring
        0xCB: 0x0327,  # cedilla
        0xCD: 0x030B,  # double acute accent
        0xCE: 0x0328,  # ogonek
        0xCF: 0x030C,  # caron
    }

    def decode(self, input, errors="strict"):
        output = ""
        state = None
        count = 0
        for char in input:
            # End of a subtitle text
            count += 1
            if not state and char in self.identical:
                output += chr(char)
            elif not state and char in self.direct_mapping:
                output += chr(self.direct_mapping[char])
            elif not state and char in self.diacritic:
                state = self.diacritic[char]
            elif state:
                combined = unicodedata.normalize("NFC", chr(char) + chr(state))
                if combined and len(combined) == 1:
                    output += combined
                state = None
        return output, len(input)

    def search(name):
        if name in ("iso6937", "iso_6937-2"):
            return codecs.CodecInfo(
                name="iso_6937-2",
                encode=iso6937().encode,
                decode=iso6937().decode,
            )

    def encode(self, input, errors="strict"):
        pass


codecs.register(iso6937.search)


class STLReader(BaseReader):
    """A class that behaves like a file object and reads an STL file"""

    GSIfields = "CPN DFC DSC CCT LC OPT OET TPT TET TN TCD SLR CD RD RN TNB TNS TNG MNC MNR TCS TCP TCF TND DSN CO PUB EN ECD UDA".split(
        " "
    )
    TTIfields = "SGN SN EBN CS TCIh TCIm TCIs TCIf TCOh TCOm TCOs TCOf VP JC CF TF".split(" ")

    def detect(self, content):
        return content[3:11] == b"STL24.01" or content[3:11] == b"STL25.01" or content[3:11] == b"STL30.01"

    def read(self, content, language=None):
        self.file = BytesIO(content)
        self._readGSI()

        captions = CaptionList()
        try:
            while True:
                captions.append(self._readTTI())
        except StopIteration:
            pass
        if language:
            return CaptionSet({language: captions})
        else:
            return CaptionSet({lang_code.get(self.GSI["LC"], "und"): captions})

    def __bcdTimestampDecode(self, timestamp):
        # Special case for people that can't bother to read a spec
        if timestamp == b"________":
            return 0.0

        # BCD coded time with limited significant bits as per EBU Tech. 3097-E
        safe_bytes = map(
            lambda x: x[0] & x[1], zip((0x2, 0xF, 0x7, 0xF, 0x7, 0xF, 0x3, 0xF), struct.unpack("8B", timestamp))
        )
        return sum(
            map(lambda x: x[0] * x[1], zip((36000, 3600, 600, 60, 10, 1, 10.0 / self.fps, 1.0 / self.fps), safe_bytes))
        )

    def _readGSI(self):
        self.GSI = dict(
            zip(
                self.GSIfields,
                struct.unpack(
                    "3s8sc2s2s32s32s32s32s32s32s16s6s6s2s5s5s3s2s2s1s8s8s1s1s3s32s32s32s75x576s", self.file.read(1024)
                ),
            )
        )
        GSI = self.GSI
        logging.debug(GSI)
        # self.gsiCodePage = 'cp%s' % GSI['CPN']
        if GSI["DFC"] == b"STL24.01":
            self.fps = 24
        elif GSI["DFC"] == b"STL25.01":
            self.fps = 25
        elif GSI["DFC"] == b"STL30.01":
            self.fps = 30
        else:
            raise Exception("Invalid DFC")
        self.codePage = {
            b"00": "iso_6937-2",
            b"01": "iso-8859-5",
            b"02": "iso-8859-6",
            b"03": "iso-8859-7",
            b"04": "iso-8859-8",
        }[GSI["CCT"]]
        self.numberOfTTI = int(GSI["TNB"])
        if GSI["TCS"] == b"1":
            # BCD coded time with limited significant bits

            self.startTime = self.__bcdTimestampDecode(GSI["TCP"])
        else:
            self.startTime = 0.0
        logging.debug(self.__dict__)

    def __timecodeDecode(self, h, m, s, f):
        return 3600 * h + 60 * m + s + float(f) / self.fps

    def __parseFormatting(self, text, encoding):
        colorCodes = [
            "#000000",  # black
            "#ff0000",  # red
            "#00ff00",  # green
            "#ffff00",  # yellow
            "#0000ff",  # blue
            "#ff00ff",  # magenta
            "#00ffff",  # cyan
            "#ffffff",  # white
        ]
        currentColor = 7  # White is the default color

        first_line = True
        nodes = []

        buffer = b""

        def drain_buffer(buffer):
            nodes.append(CaptionNode.create_text(buffer.decode(encoding)))
            return b""

        for ochar in text:
            if ochar == 0x80:
                buffer = drain_buffer(buffer)
                nodes.append(CaptionNode.create_style(True, {"italics": True}))
            elif ochar == 0x81:
                buffer = drain_buffer(buffer)
                nodes.append(CaptionNode.create_style(False, {"italics": True}))
            elif ochar == 0x82:
                buffer = drain_buffer(buffer)
                nodes.append(CaptionNode.create_style(True, {"underline": True}))
            elif ochar == 0x83:
                buffer = drain_buffer(buffer)
                nodes.append(CaptionNode.create_style(False, {"underline": True}))
            elif ochar == 0xE:
                buffer = drain_buffer(buffer)
                nodes.append(CaptionNode.create_style(True, {"bold": True}))
            elif ochar == 0xC:
                buffer = drain_buffer(buffer)
                nodes.append(CaptionNode.create_style(False, {"bold": True}))
            elif ochar in (0, 1, 2, 3, 4, 5, 6, 7, 0x10, 0x11, 0x12, 0x13, 0x14, 0x15, 0x16, 0x17):
                color = ochar % 0x10
                if color != currentColor:
                    currentColor = color
                    buffer = drain_buffer(buffer)
                    nodes.append(CaptionNode.create_style(True, {"color": colorCodes[currentColor]}))
            elif ochar == 0x8A and first_line:
                buffer = drain_buffer(buffer)
                nodes.append(CaptionNode.create_break())
                first_line = False
            elif ochar == 0x8F:
                buffer = drain_buffer(buffer)
                break
            elif (ochar & 0x7F) >= 0x20:
                buffer += bytes(
                    [
                        ochar,
                    ]
                )

        return nodes

    def _readTTI(self):
        while True:
            tci = None
            tco = None
            nodes = []

            while True:
                data = self.file.read(128)
                if not data:
                    raise StopIteration()
                TTI = dict(zip(self.TTIfields, struct.unpack("<BHBBBBBBBBBBBBB112s", data)))
                logging.debug(TTI)
                # if comment skip
                if TTI["CF"]:
                    continue
                if not tci:
                    tci = self.__timecodeDecode(TTI["TCIh"], TTI["TCIm"], TTI["TCIs"], TTI["TCIf"]) - self.startTime
                    tco = self.__timecodeDecode(TTI["TCOh"], TTI["TCOm"], TTI["TCOs"], TTI["TCOf"]) - self.startTime
                text = TTI["TF"]
                nodes += self.__parseFormatting(text, self.codePage)

                if TTI["EBN"] == 255:
                    # skip empty subtitles and those before the start of the show
                    if len(nodes) > 0 and tci >= 0:
                        opennodes = []
                        for node in reversed(nodes):
                            if node.type_ == CaptionNode.STYLE:
                                styletype = node.content[next(iter(node.content.keys()))]
                                if node.start:
                                    opennodes.append(styletype)
                                else:
                                    if opennodes[-1] == styletype:
                                        opennodes.pop()
                                    else:
                                        raise Exception(
                                            "STL style overlapping no supported as it would result in something like <i>italic<b>bolditalic</i>bold</b>"
                                        )

                        for opennode in opennodes:
                            nodes.append(CaptionNode.create_style(False, {opennode: True}))
                        return Caption(tci * 1000000, tco * 1000000, nodes)
                    break

    def __iter__(self):
        return self

    def __next__(self):
        return self._readTTI()


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    content = open("chernobyl_004_spanish_latin_american_2997.stl", mode="rb").read()
    subs = STLReader().read(content)
    print(subs)
