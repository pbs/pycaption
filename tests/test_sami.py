
# -*- coding: utf-8 -*-
import unittest

from bs4 import BeautifulSoup

from pycaption import SAMIReader, SAMIWriter


SAMPLE_SAMI = """
<SAMI><HEAD><TITLE>NOVA3213</TITLE><STYLE TYPE="text/css">
<!--
P { margin-left:  1pt;
    margin-right: 1pt;
    margin-bottom: 2pt;
    margin-top: 2pt;
    text-align: center;
    font-size: 10pt;
    font-family: Arial;
    font-weight: normal;
    font-style: normal;
    color: #ffffff; }

.ENCC {Name: English; lang: en-US; SAMI_Type: CC;}

--></STYLE></HEAD><BODY>
<SYNC start="9209"><P class="ENCC">
       ( clock ticking )
</P></SYNC>
<SYNC start="12312"><P class="ENCC">&nbsp;</P></SYNC>
<SYNC start="14848"><P class="ENCC">
              MAN:<br/>
         When we think<br/>
    of E equals m c-squared,
</P></SYNC>
<SYNC start="17350"><P class="ENCC">
we have this vision of Einstein
</P></SYNC>
<SYNC start="18752"><P class="ENCC">
     as an old, wrinkly man<br/>
        with white hair.
</P></SYNC>
<SYNC start="20887"><P class="ENCC">
             MAN 2:<br/>
    E equals m c-squared is<br/>
   not about an old Einstein.
</P></SYNC>
</BODY></SAMI>
"""


class SAMIReaderTestCase(unittest.TestCase):

    def test_detection(self):
        self.assertTrue(SAMIReader().detect(SAMPLE_SAMI))

    def test_proper_pcc_format(self):
        captions = SAMIReader().read(SAMPLE_SAMI)

        self.assertEquals(set(["captions", "styles"]), set(captions.keys()))
        self.assertEquals(5, len(captions["captions"]["en-US"]))

    def test_proper_timestamps(self):
        captions = SAMIReader().read(SAMPLE_SAMI)
        paragraph = captions["captions"]["en-US"][0]

        self.assertEquals(9209000, paragraph[0])
        self.assertEquals(12312000, paragraph[1])


class SAMIWriterTestCase(unittest.TestCase):

    def setUp(self):
        self.captions = SAMIReader().read(SAMPLE_SAMI)

    def selfAssertSAMIEquals(self, first, second):
        first_soup = BeautifulSoup(first)
        second_soup = BeautifulSoup(second)

        first_items = _extract_sami_captions(first_soup)
        second_items = _extract_sami_captions(second_soup)
        self.assertEquals(first_items, second_items)

    def test_write(self):
        results = SAMIWriter().write(self.captions)
        self.selfAssertSAMIEquals(SAMPLE_SAMI, results)


def _extract_sami_captions(soup):
    return tuple(
        (caption.attrs['start'], _normalize_caption_text(caption.p.text))
        for caption in soup.select('sync'))


def _normalize_caption_text(value):
    return value.strip().replace(' ', '')
