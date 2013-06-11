from bs4 import BeautifulSoup


class SRTTestingMixIn(object):
    """
    Provide specialized test case capabilities for asserting on SRT content.
    """

    def _extract_srt_captions(self, content):
        return tuple(line.strip() for line in content.splitlines())

    def assertSRTEquals(self, first, second):
        """
        Assert that two SRT contents are equal.
        """
        first_items = self._extract_srt_captions(first)
        second_items = self._extract_srt_captions(second)
        self.assertEquals(first_items, second_items)


class XMLTestingMixIn(object):
    """
    Provide specialized test case capabilities for asserting on XML content.
    """

    def assertXMLEquals(self, first, second):
        first_soup = BeautifulSoup(first)
        second_soup = BeautifulSoup(second)
        self.assertEquals(first_soup, second_soup)


class SAMITestingMixIn(object):
    """
    Provide specialized test case capabilities for asserting on SAMI content.
    """

    def _normalize_sami_caption_text(self, text):
        return text.strip().replace(' ', '-')

    def _extract_sami_captions(self, soup):
        return tuple(
            (caption.attrs['start'],
             self._normalize_sami_caption_text(caption.p.text))
            for caption in soup.select('sync'))

    def assertSAMIEquals(self, first, second):
        first_soup = BeautifulSoup(first)
        second_soup = BeautifulSoup(second)

        first_items = self._extract_sami_captions(first_soup)
        second_items = self._extract_sami_captions(second_soup)
        self.assertEquals(first_items, second_items)
