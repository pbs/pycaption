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
