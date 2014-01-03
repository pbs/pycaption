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


class DFXPTestingMixIn(object):
    """
    Provide specialized test case capabilities for asserting on DFXP content.
    """

    def _remove_styling(self, soup):
        for style in soup('styling'):
            style.extract()

        for paragraph in soup('p'):
            if 'style' in paragraph.attrs:
                del paragraph.attrs['style']

    def _remove_spans(self, soup):
        for span in soup('span'):
            span.unwrap()

    def _trim_text(self, soup):
        for paragraph in soup('p'):
            paragraph.string = paragraph.text.strip()

    def assertDFXPEquals(self, first, second,
                         ignore_styling=False,
                         ignore_spans=False):
        first_soup = BeautifulSoup(first)
        second_soup = BeautifulSoup(second)

        if ignore_styling:
            self._remove_styling(first_soup)
            self._remove_styling(second_soup)

        if ignore_spans:
            self._remove_spans(first_soup)
            self._remove_spans(second_soup)

        self._trim_text(first_soup)
        self._trim_text(second_soup)

        self.assertEquals(first_soup, second_soup)


class SAMITestingMixIn(object):
    """
    Provide specialized test case capabilities for asserting on SAMI content.
    """

    def _extract_sami_captions(self, soup):
        return tuple(
            (caption.attrs['start'], caption.p.text.strip())
            for caption in soup.select('sync'))

    def assertSAMIEquals(self, first, second):
        first_soup = BeautifulSoup(first)
        second_soup = BeautifulSoup(second)

        first_items = self._extract_sami_captions(first_soup)
        second_items = self._extract_sami_captions(second_soup)
        self.assertEquals(first_items, second_items)
