import unittest

from pycaption import DFXPReader, SAMIReader, SCCReader, SRTReader, WebVTTReader

from pycaption.exceptions import InvalidInputError

class ReaderTestCase(unittest.TestCase):

    def test_dfxp_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            DFXPReader().read('')

    def test_sami_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            SAMIReader().read('')

    def test_scc_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            SCCReader().read('')

    def test_srt_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            SRTReader().read('')

    def test_webvtt_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            WebVTTReader().read('')
