import unittest

from pycaption import DFXPReader, CaptionReadNoCaptions

from .samples import SAMPLE_DFXP, SAMPLE_DFXP_EMPTY, SAMPLE_DFXP_SYNTAX_ERROR


class DFXPReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP.decode(u'utf-8')))

    def test_caption_length(self):
        captions = DFXPReader().read(SAMPLE_DFXP.decode(u'utf-8'))

        self.assertEquals(7, len(captions.get_captions(u"en-US")))

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
