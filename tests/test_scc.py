import unittest

from pycaption import SCCReader, CaptionReadNoCaptions

from .samples import SAMPLE_SCC, SAMPLE_SCC_EMPTY

TOLERANCE_MICROSECONDS = 500 * 1000

class SCCReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SCCReader().detect(SAMPLE_SCC.decode(u'utf-8')))

    def test_caption_length(self):
        captions = SCCReader().read(SAMPLE_SCC.decode(u'utf-8'))

        self.assertEquals(7, len(captions.get_captions(u"en-US")))

    def test_proper_timestamps(self):
        captions = SCCReader().read(SAMPLE_SCC.decode(u'utf-8'))
        paragraph = captions.get_captions(u"en-US")[2]

        delta_start = abs(paragraph.start - 17000000)
        delta_end = abs(paragraph.end - 18752000)

        self.assertTrue(delta_start < TOLERANCE_MICROSECONDS)
        self.assertTrue(delta_end < TOLERANCE_MICROSECONDS)

    def test_empty_file(self):
        self.assertRaises(
            CaptionReadNoCaptions,
            SCCReader().read, SAMPLE_SCC_EMPTY.decode(u'utf-8'))

    def test_last_caption_zero_end_time_is_corrected(self):
        caption_set = SCCReader().read(SAMPLE_SCC_NO_EXPLICIT_END_TO_LAST_CAPTION)  # noqa

        last_caption = caption_set.get_captions('en-US')[-1]

        self.assertEqual(
            last_caption.end, last_caption.start + 4 * 1000 * 1000
        )


SAMPLE_SCC_NO_EXPLICIT_END_TO_LAST_CAPTION = u"""\
Scenarist_SCC V1.0

00:00:00;00	73e9 e329 942f

00:00:06;01	942c

00:24:55;14	9420 94ae 9470 97a2 a875 7062 e561 f420 f2ef e36b 206d 7573 e9e3 2980 942f
"""