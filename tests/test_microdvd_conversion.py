import unittest
import six

from pycaption import MicroDVDReader, MicroDVDWriter

from tests.samples.microdvd import SAMPLE_MICRODVD

from tests.mixins import MicroDVDTestingMixIn


class MicroDVDtoMicroDVDTestCase(unittest.TestCase, MicroDVDTestingMixIn):

    def test_microdvd_to_microdvd_conversion(self):
        caption_set = MicroDVDReader().read(SAMPLE_MICRODVD)
        results = MicroDVDWriter().write(caption_set)
        self.assertTrue(isinstance(results, six.text_type))
        self.assertMicroDVDEquals(SAMPLE_MICRODVD, results)
