import unittest
from os.path import join, dirname, abspath

from pycaption.stl.ebu_stl_reader import STLReader


class SRTtoWebVTTTestCase(unittest.TestCase):
    directory = join(dirname(abspath(__file__)))
    def test_stl(self):
        stl = STLReader()
        content = open(join(self.directory, "ebu1991", "test.stl"), "rb").read()
        self.assertTrue(stl.detect(content))
        captions = stl.read(content)

        self.assertEqual(len(captions.get_captions("de")), 494)
