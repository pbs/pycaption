import unittest

from pycaption import DFXPReader, CaptionReadNoCaptions

from .samples import SAMPLE_DFXP, SAMPLE_DFXP_EMPTY, SAMPLE_DFXP_SYNTAX_ERROR, SAMPLE_DFXP_TIME_FORMATS


class DFXPReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP.decode(u'utf-8')))

    def test_caption_length(self):
        captions = DFXPReader().read(SAMPLE_DFXP.decode(u'utf-8'))
        self.assertEquals(8, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = DFXPReader().read(SAMPLE_DFXP_TIME_FORMATS.decode(u'utf-8'))
        paragraph = captions.get_captions(u"en-US")[0]

        # Start is expressed in fraction seconds 01:02:03.530530
        # End time is expressed with frames 01:02:03:15.9
        self.assertEquals(3723530530, paragraph.start)
        self.assertEquals(3723530530, paragraph.end)

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            DFXPReader().read, SAMPLE_DFXP_EMPTY.decode(u'utf-8'))

    def test_invalid_markup_is_properly_handled(self):
        captions = DFXPReader().read(SAMPLE_DFXP_SYNTAX_ERROR.decode(u'utf-8'))
        self.assertEquals(2, len(captions.get_captions(u"en-US")))
