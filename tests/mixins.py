import re

import pytest
from bs4 import BeautifulSoup

from pycaption.exceptions import InvalidInputError


class ReaderTestingMixIn:
    """
    Provide test case capabilities for asserting common Reader functionalities.
    """

    def assert_positive_answer_for_detection(self, matching_sample):
        assert self.reader.detect(matching_sample) is True

    def assert_negative_answer_for_detection(self, different_sample):
        assert self.reader.detect(different_sample) is False

    def test_reader_only_supports_unicode_input(self):
        with pytest.raises(InvalidInputError) as exc_info:
            self.reader.read(b'')
        assert exc_info.value.args[0] == 'The content is not a unicode string.'


class WebVTTTestingMixIn:
    """
    Provide specialized test case capabilities for asserting on WebVTT content.
    """

    def _extract_webvtt_captions(self, content):
        return tuple(line.strip() for line in content.splitlines())

    def assert_webvtt_equals(self, first, second):
        """
        Assert that two WebVTT contents are equal.
        """
        first_items = self._extract_webvtt_captions(first)
        second_items = self._extract_webvtt_captions(second)

        assert first_items == second_items


class SRTTestingMixIn:
    """
    Provide specialized test case capabilities for asserting on SRT content.
    """

    def _extract_srt_captions(self, content):
        return tuple(line.strip() for line in content.splitlines())

    def assert_srt_equals(self, first, second):
        """
        Assert that two SRT contents are equal.
        """
        first_items = self._extract_srt_captions(first)
        second_items = self._extract_srt_captions(second)

        assert first_items == second_items


class CaptionSetTestingMixIn:
    def assert_captionset_almost_equals(self, first, second,
                                        tolerance_microseconds):
        """
        Assert that two caption sets have equal text except for newlines,
        and differences in timing that are less than tolerance_microseconds.
        """

        captions_1 = first.get_captions(list(first.get_languages())[0])
        captions_2 = second.get_captions(list(first.get_languages())[0])

        def get_text_for_caption(caption):
            text = caption.get_text()
            text = re.sub(r'\s+', ' ', text)

            return text

        text_1 = [get_text_for_caption(caption) for caption in captions_1]
        text_2 = [get_text_for_caption(caption) for caption in captions_2]

        def close_enough(ts1, ts2):
            return abs(ts1 - ts2) < tolerance_microseconds

        start_differences = [
            (caption_1.start, caption_2.start)
            for caption_1, caption_2 in zip(captions_1, captions_2)
            if not close_enough(caption_1.start, caption_2.start)
        ]

        end_differences = [
            (caption_1.end, caption_2.end)
            for caption_1, caption_2 in zip(captions_1, captions_2)
            if not close_enough(caption_1.end, caption_2.end)
        ]

        assert text_1 == text_2
        assert start_differences == []
        assert end_differences == []


class DFXPTestingMixIn:
    """
    Provide specialized test case capabilities for asserting on DFXP content.
    """

    def _remove_styling(self, soup):
        for style in soup('styling'):
            style.clear()

        for paragraph in soup('p'):
            if 'style' in paragraph.attrs:
                del paragraph.attrs['style']

    def _remove_spans(self, soup):
        for span in soup('span'):
            span.unwrap()

    def _trim_text(self, soup):
        for paragraph in soup('p'):
            paragraph.string = paragraph.text.strip()

    def assert_dfxp_equals(self, first, second,
                           ignore_styling=False,
                           ignore_spans=False):
        first_soup = BeautifulSoup(first, 'lxml')
        second_soup = BeautifulSoup(second, 'lxml')

        if ignore_styling:
            self._remove_styling(first_soup)
            self._remove_styling(second_soup)

        if ignore_spans:
            self._remove_spans(first_soup)
            self._remove_spans(second_soup)

        self._trim_text(first_soup)
        self._trim_text(second_soup)

        assert first_soup == second_soup


class SAMITestingMixIn:
    """
    Provide specialized test case capabilities for asserting on SAMI content.
    """

    def _extract_sami_captions(self, soup):
        return tuple(
            (caption.attrs['start'], caption.p.text.strip())
            for caption in soup.select('sync')
        )

    def assert_sami_captions_equal(self, first, second):
        first_soup = BeautifulSoup(first, 'lxml')
        second_soup = BeautifulSoup(second, 'lxml')

        first_items = self._extract_sami_captions(first_soup)
        second_items = self._extract_sami_captions(second_soup)

        assert first_items == second_items


class MicroDVDTestingMixIn:
    """
    Provide specialized test case capabilities for asserting on MicroDVD content.
    """  # noqa

    def _extract_micro_dvd_captions(self, content):
        return tuple(line.strip() for line in content.splitlines())

    def assert_microdvd_equals(self, first, second):
        """
        Assert that two MicroDVD contents are equal.
        """
        first_items = self._extract_micro_dvd_captions(first)
        second_items = self._extract_micro_dvd_captions(second)

        assert first_items == second_items
