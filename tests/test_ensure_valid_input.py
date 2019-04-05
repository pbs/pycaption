from __future__ import unicode_literals
import unittest

from pycaption import DFXPReader, SAMIReader, SCCReader, SRTReader, WebVTTReader

from pycaption.exceptions import InvalidInputError

class ReaderTestCase(unittest.TestCase):

    def test_dfxp_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            DFXPReader().read(b'')

    def test_sami_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            SAMIReader().read(b'')

    def test_scc_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            SCCReader().read(b'')

    def test_srt_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            SRTReader().read(b'')

    def test_webvtt_reader_only_supports_unicode_input(self):
        with self.assertRaises(InvalidInputError):
            WebVTTReader().read(b'')
