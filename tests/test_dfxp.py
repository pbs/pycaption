import unittest

from pycaption import DFXPReader, CaptionReadNoCaptions
from pycaption.exceptions import CaptionReadSyntaxError

from .samples import SAMPLE_DFXP, SAMPLE_DFXP_EMPTY, SAMPLE_DFXP_SYNTAX_ERROR


class DFXPReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP.decode(u'utf-8')))

    def test_caption_length(self):
        captions = DFXPReader().read(SAMPLE_DFXP.decode(u'utf-8'))
        self.assertEquals(8, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = DFXPReader().read(SAMPLE_DFXP.decode(u'utf-8'))
        paragraph = captions.get_captions(u"en-US")[2]

        self.assertEquals(17000000, paragraph.start)
        self.assertEquals(18752000, paragraph.end)

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            DFXPReader().read, SAMPLE_DFXP_EMPTY.decode(u'utf-8'))

    def test_invalid_markup_is_properly_handled(self):
        captions = DFXPReader().read(SAMPLE_DFXP_SYNTAX_ERROR.decode(u'utf-8'))
        self.assertEquals(2, len(captions.get_captions(u"en-US")))

    def test_caption_error_for_invalid_positioning_values(self):
        invalid_value_dfxp = (
            SAMPLE_DFXP_INVALID_POSITIONING_VALUE_TEMPLATE
            .format(origin=u"px 5px")
        )
        self.assertRaises(
            CaptionReadSyntaxError, DFXPReader().read,
            invalid_value_dfxp
        )

    def test_caption_error_for_invalid_or_unsupported_positioning_units(self):
        invalid_dfxp = (
            SAMPLE_DFXP_INVALID_POSITIONING_VALUE_TEMPLATE
            .format(origin=u"6foo 7bar")
        )

        self.assertRaises(
            CaptionReadSyntaxError, DFXPReader().read,
            invalid_dfxp
        )

SAMPLE_DFXP_INVALID_POSITIONING_VALUE_TEMPLATE = u"""\
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml" xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <layout>
   <region tts:origin="{origin}" xml:id="bottom"/>
  </layout>
 </head>
 <body>
  <div region="bottom" xml:lang="en-US">
   <p begin="00:00:09.209" end="00:00:12.312" region="bottom">
    ( clock ticking )
   </p>
  </div>
 </body>
</tt>"""