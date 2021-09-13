from pycaption import MicroDVDReader, MicroDVDWriter, SAMIReader

from tests.mixins import MicroDVDTestingMixIn


class TestMicroDVDtoMicroDVD(MicroDVDTestingMixIn):
    def test_microdvd_to_microdvd_conversion(self, sample_microdvd):
        caption_set = MicroDVDReader().read(sample_microdvd)
        results = MicroDVDWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_microdvd_equals(sample_microdvd, results)


class TestSAMItoMicroDVD(MicroDVDTestingMixIn):
    def test_sami_to_micro_dvd_conversion(self, sample_microdvd_2, sample_sami):
        caption_set = SAMIReader().read(sample_sami)
        results = MicroDVDWriter().write(caption_set)

        assert isinstance(results, str)
        self.assert_microdvd_equals(sample_microdvd_2, results)
