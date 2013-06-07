# -*- coding: utf-8 -*-
import unittest

from bs4 import BeautifulSoup

from pycaption import DFXPReader, DFXPWriter


SAMPLE_DFXP = """
<?xml version="1.0" encoding="utf-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
 <head>
  <styling>
   <style id="p" tts:color="#ffffff" tts:fontfamily="Arial"
          tts:fontsize="10pt" tts:textAlign="center"/>
  </styling>
 </head>
 <body>
  <div xml:lang="en-US">
   <p begin="00:00:02.268" end="00:00:05.000" style="p">
    ♫Every day, when you're<br/>
    walking down the street♫
   </p>
   <p begin="00:00:05.000" end="00:00:09.909" style="p">
    ♫Everybody that you meet<br/>
    has an original point of view♫
   </p>
   <p begin="00:00:09.909" end="00:00:11.578" style="p">
    (laughing)
   </p>
   <p begin="00:00:11.578" end="00:00:13.780" style="p">
    ♫And I say, hey♫<br/>
    Hey!
   </p>
  </div>
 </body>
</tt>
"""


class DFXPReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(DFXPReader().detect(SAMPLE_DFXP))

    def test_proper_pcc_format(self):
        captions = DFXPReader().read(SAMPLE_DFXP)

        self.assertEquals(set(["captions", "styles"]), set(captions.keys()))
        self.assertEquals(4, len(captions["captions"]["en-US"]))

    def test_proper_timestamps(self):
        captions = DFXPReader().read(SAMPLE_DFXP)
        paragraph = captions["captions"]["en-US"][2]

        self.assertEquals(9909000, paragraph[0])
        self.assertEquals(11578000, paragraph[1])


class DFXPWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = DFXPReader().read(SAMPLE_DFXP)

    def selfAssertXMLEquals(self, first, second):
        first_soup = BeautifulSoup(first)
        second_soup = BeautifulSoup(second)
        self.assertEquals(first_soup, second_soup)

    def test_write(self):
        results = DFXPWriter().write(self.captions)
        self.selfAssertXMLEquals(SAMPLE_DFXP, results)
