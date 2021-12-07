import pytest

from pycaption import (
    WebVTTReader, WebVTTWriter, SAMIReader, DFXPReader,
    CaptionReadNoCaptions, CaptionReadError, CaptionReadSyntaxError,
)
from tests.mixins import ReaderTestingMixIn


class TestWebVTTReader(ReaderTestingMixIn):
    def setup_method(self):
        self.reader = WebVTTReader()

    def test_positive_answer_for_detection(self, sample_webvtt):
        super().assert_positive_answer_for_detection(sample_webvtt)

    @pytest.mark.parametrize('different_sample', [
        pytest.lazy_fixture('sample_dfxp'),
        pytest.lazy_fixture('sample_microdvd'),
        pytest.lazy_fixture('sample_sami'),
        pytest.lazy_fixture('sample_scc_pop_on'),
        pytest.lazy_fixture('sample_srt')
    ])
    def test_negative_answer_for_detection(self, different_sample):
        super().assert_negative_answer_for_detection(different_sample)

    def test_caption_length(self, sample_webvtt_2):
        captions = self.reader.read(sample_webvtt_2)

        assert len(captions.get_captions('en-US')) == 7

    def test_read_supports_multiple_languages(self, sample_webvtt):
        captions = self.reader.read(sample_webvtt, lang='es')

        assert captions.get_captions('es') is not None

    def test_proper_timestamps(self, sample_webvtt):
        captions = self.reader.read(sample_webvtt)
        cue = captions.get_captions('en-US')[2]

        assert cue.start == 17000000
        assert cue.end == 18752000

    def test_forward_time_shift(self, sample_webvtt):
        captions = WebVTTReader(time_shift_milliseconds=15).read(sample_webvtt)
        cue = captions.get_captions('en-US')[2]

        assert cue.start == 17015000
        assert cue.end == 18767000

    def test_backward_time_shift(self, sample_webvtt):
        captions = WebVTTReader(time_shift_milliseconds=-15).read(sample_webvtt)
        cue = captions.get_captions('en-US')[2]

        assert cue.start == 16985000
        assert cue.end == 18737000

    def test_webvtt_cue_components_removed_from_text(self):
        result = self.reader._remove_styles(
            "<c vIntro><b>Wikipedia</b> is a great adventure. <i>It may have "
            "its shortcomings</i>, but it is<u> the largest</u> collective "
            "knowledge construction endevour</c> <ruby>base text <rt>"
            "annotation</rt></ruby> <v Audry><b>Yes</b>, indeed!"
        )
        expected = (
            "Wikipedia is a great adventure. It may have "
            "its shortcomings, but it is the largest collective "
            "knowledge construction endevour base text annotation"
            " Audry: Yes, indeed!"
        )
        assert result == expected

    def test_empty_file(self, sample_webvtt_empty):
        with pytest.raises(CaptionReadNoCaptions):
            WebVTTReader().read(sample_webvtt_empty)

    def test_not_ignoring_timing_errors(self):
        # todo: same assert w/ different arguments -> this can be parametrized;
        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "\n" "00:00:20.000 --> 00:00:10.000\n" "foo bar baz")

        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "00:00:20.000 --> 00:00:10.000\n"
                "Start time is greater than end time.\n"
            )

        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "00:00:20.000 --> 00:00:30.000\n"
                "Start times should be consecutive.\n"
                "\n"
                "00:00:10.000 --> 00:00:20.000\n"
                "This cue starts before the previous one.\n"
            )

    def test_ignoring_timing_errors(self):
        # Even if timing errors are ignored, this has to raise an exception
        with pytest.raises(CaptionReadSyntaxError):
            WebVTTReader().read(
                "\nNOTE invalid cue stamp\n00:00:20.000 --> \nfoo bar baz\n")

        # And this too
        with pytest.raises(CaptionReadSyntaxError):
            WebVTTReader().read("\n00:00:20,000 --> 00:00:22,000\n"
                                "Note the comma instead of point.\n")

        # todo: at this point it can be split into 2 separate tests
        try:
            WebVTTReader().read(
                "\n"
                "00:00:20.000 --> 00:00:10.000\n"
                "Start time is greater than end time.\n"
            )
        except CaptionReadError:
            pytest.fail("Shouldn't raise CaptionReadError")

        try:
            WebVTTReader().read(
                "\n"
                "00:00:20.000 --> 00:00:30.000\n"
                "Start times should be consecutive.\n"
                "\n"
                "00:00:10.000 --> 00:00:20.000\n"
                "This cue starts before the previous one.\n"
            )
        except CaptionReadError:
            pytest.fail("Shouldn't raise CaptionReadError")

    def test_invalid_files(self):
        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "00:00:20.000 --> 00:00:10.000\n"
                "Start time is greater than end time.")

        with pytest.raises(CaptionReadError):
            WebVTTReader(ignore_timing_errors=False).read(
                "00:00:20.000 --> 00:00:30.000\n"
                "Start times should be consecutive.\n"
                "\n"
                "00:00:10.000 --> 00:00:20.000\n"
                "This cue starts before the previous one.\n"
            )

    def test_zero_start(self, sample_webvtt_last_cue_zero_start):
        captions = self.reader.read(sample_webvtt_last_cue_zero_start)
        cue = captions.get_captions('en-US')[0]

        assert cue.start == 0

    def test_webvtt_empty_cue(self, sample_webvtt_empty_cue):
        assert 1 == len(self.reader.read(
            sample_webvtt_empty_cue).get_captions('en-US'))


class TestWebVTTWriter:
    def setup_method(self):
        self.writer = WebVTTWriter()

    def test_double_br(self, sample_webvtt_double_br, sample_sami_double_br):
        caption_set = SAMIReader().read(sample_sami_double_br)
        results = WebVTTWriter().write(caption_set)

        assert sample_webvtt_double_br == results

    def test_break_node_positioning_is_ignored(
            self, webvtt_from_dfxp_with_conflicting_align,
            dfxp_style_region_align_conflict):
        caption_set = DFXPReader().read(dfxp_style_region_align_conflict)
        results = WebVTTWriter().write(caption_set)

        assert webvtt_from_dfxp_with_conflicting_align == results

    def test_lang_option(self, sample_webvtt_multi_lang_en,
                         sample_webvtt_multi_lang_de,
                         sample_sami_with_multi_lang):
        caption_set = SAMIReader().read(sample_sami_with_multi_lang)
        results = WebVTTWriter().write(caption_set, 'de-DE')

        assert sample_webvtt_multi_lang_de == results
        results = WebVTTWriter().write(caption_set, 'en-US')
        assert sample_webvtt_multi_lang_en == results
