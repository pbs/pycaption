import re

from pycaption import SCCReader, SCCWriter, SRTReader, WebVTTReader


class TestSCCWriterTimestampFormatting:
    def test_ndf_timestamp_uses_colons(self):
        assert SCCWriter._format_timestamp_ndf(0) == "00:00:00:00"
        assert ";" not in SCCWriter._format_timestamp_ndf(1_000_000)

    def test_ndf_known_values(self):
        assert SCCWriter._format_timestamp_ndf(0) == "00:00:00:00"
        # 1 second of real time at 29.97fps NDF
        # 1_000_000 us * 1000/1001 = 999.000999 coded seconds → 29 frames
        assert SCCWriter._format_timestamp_ndf(1_000_000) == "00:00:00:29"
        # 60 seconds real → 59.94 coded seconds → 59s + 28 frames
        assert SCCWriter._format_timestamp_ndf(60_000_000) == "00:00:59:28"

    def test_df_timestamp_uses_semicolons(self):
        result = SCCWriter._format_timestamp_df(1_000_000)
        assert ";" in result

    def test_df_known_values(self):
        assert SCCWriter._format_timestamp_df(0) == "00:00:00;00"
        # 10 minutes of real time should map to exactly 10:00;00 in DF
        ten_minutes_us = 10 * 60 * 1_000_000
        assert SCCWriter._format_timestamp_df(ten_minutes_us) == "00:10:00;00"

    def test_df_frame_skip_at_minute_boundary(self):
        # Real frame 1800 is the first frame of minute 1 in DF.
        # Minute 0 has 1800 frames (0..1799), no drops.
        # Minute 1 starts at real frame 1800, displayed as 00:01:00;02
        # (frames ;00 and ;01 are dropped at non-10th minutes).
        us_for_frame_1800 = round(1800 * 1001 / 1000 / 30 * 1_000_000)
        result = SCCWriter._format_timestamp_df(us_for_frame_1800)
        assert result == "00:01:00;02"

    def test_df_no_frame_skip_at_10_minute_boundary(self):
        # At 10-minute boundaries, no frames are dropped
        twenty_minutes_us = 20 * 60 * 1_000_000
        result = SCCWriter._format_timestamp_df(twenty_minutes_us)
        assert result == "00:20:00;00"


class TestSCCWriterDropFrameFlag:
    def _make_simple_captions(self):
        srt = (
            "1\n"
            "00:00:01,000 --> 00:00:03,000\n"
            "Hello world\n\n"
            "2\n"
            "00:00:05,000 --> 00:00:07,000\n"
            "Second line\n"
        )
        return SRTReader().read(srt)

    def test_drop_frame_false_is_default(self):
        writer = SCCWriter()
        assert writer.drop_frame is False

    def test_drop_frame_false_uses_colons(self):
        captions = self._make_simple_captions()
        output = SCCWriter(drop_frame=False).write(captions)
        timestamps = re.findall(r"\d{2}:\d{2}:\d{2}[:;]\d{2}", output)
        for ts in timestamps:
            assert ";" not in ts

    def test_drop_frame_true_uses_semicolons(self):
        captions = self._make_simple_captions()
        output = SCCWriter(drop_frame=True).write(captions)
        timestamps = re.findall(r"\d{2}:\d{2}:\d{2}[:;]\d{2}", output)
        assert len(timestamps) > 0
        for ts in timestamps:
            assert ";" in ts

    def test_drop_frame_false_preserves_existing_behavior(self):
        captions = self._make_simple_captions()
        output_default = SCCWriter().write(captions)
        output_explicit = SCCWriter(drop_frame=False).write(captions)
        assert output_default == output_explicit


class TestSCCWriterTimestampOrdering:
    def test_timestamps_monotonically_increasing_ndf(self):
        vtt_input = (
            "WEBVTT\n\n"
            "0\n00:00:01.529 --> 00:00:03.640\n"
            "When it comes to finding the one,\n\n"
            "1\n00:00:03.730 --> 00:00:07.239\n"
            "I always say that if they can love you at your messiest,\n\n"
            "2\n00:00:07.570 --> 00:00:09.319\n"
            "calm you at your moodiest,\n\n"
            "3\n00:00:09.529 --> 00:00:11.680\n"
            "and laugh with you at your quirkiest,\n\n"
            "4\n00:00:11.930 --> 00:00:13.760\n"
            "you've probably found your person.\n"
        )
        captions = WebVTTReader().read(vtt_input)
        output = SCCWriter(drop_frame=False).write(captions)
        timestamps = re.findall(r"(\d{2}:\d{2}:\d{2}:\d{2})", output)
        for i in range(1, len(timestamps)):
            assert (
                timestamps[i] >= timestamps[i - 1]
            ), f"NDF timestamps out of order: {timestamps[i - 1]} > {timestamps[i]}"

    def test_timestamps_monotonically_increasing_df(self):
        vtt_input = (
            "WEBVTT\n\n"
            "0\n00:00:01.529 --> 00:00:03.640\n"
            "When it comes to finding the one,\n\n"
            "1\n00:00:03.730 --> 00:00:07.239\n"
            "I always say that if they can love you at your messiest,\n\n"
            "2\n00:00:07.570 --> 00:00:09.319\n"
            "calm you at your moodiest,\n\n"
            "3\n00:00:09.529 --> 00:00:11.680\n"
            "and laugh with you at your quirkiest,\n\n"
            "4\n00:00:11.930 --> 00:00:13.760\n"
            "you've probably found your person.\n"
        )
        captions = WebVTTReader().read(vtt_input)
        output = SCCWriter(drop_frame=True).write(captions)
        timestamps = re.findall(r"(\d{2}:\d{2}:\d{2};\d{2})", output)
        for i in range(1, len(timestamps)):
            assert (
                timestamps[i] >= timestamps[i - 1]
            ), f"DF timestamps out of order: {timestamps[i - 1]} > {timestamps[i]}"

    def test_rapid_short_captions_stay_ordered(self):
        """Short text followed by long text should not cause timestamp inversion."""
        vtt_input = (
            "WEBVTT\n\n"
            "0\n00:00:02.200 --> 00:00:02.359\nyou know,\n\n"
            "1\n00:00:02.400 --> 00:00:03.760\n"
            "the way he kind of looked at me.\n\n"
            "2\n00:00:04.700 --> 00:00:05.169\nAnd I said,\n\n"
            "3\n00:00:05.210 --> 00:00:05.520\noh\n"
        )
        captions = WebVTTReader().read(vtt_input)
        for df in (True, False):
            output = SCCWriter(drop_frame=df).write(captions)
            sep = ";" if df else ":"
            pattern = r"\d{2}:\d{2}:\d{2}" + re.escape(sep) + r"\d{2}"
            timestamps = re.findall(pattern, output)
            for i in range(1, len(timestamps)):
                assert (
                    timestamps[i] >= timestamps[i - 1]
                ), f"drop_frame={df}: {timestamps[i - 1]} > {timestamps[i]}"


class TestSCCWriterFirstCueBackshift:
    def test_first_cue_start_is_shifted_back(self):
        srt = "1\n" "00:00:10,000 --> 00:00:12,000\n" "Hello world\n"
        captions = SRTReader().read(srt)
        output = SCCWriter(drop_frame=False).write(captions)
        timestamps = re.findall(r"(\d{2}:\d{2}:\d{2}:\d{2})", output)
        # The first timestamp should be earlier than 00:00:09:29
        # (10s real time -> ~9:29 NDF, minus backshift)
        assert timestamps[0] < "00:00:09:29"

    def test_first_cue_at_zero_does_not_go_negative(self):
        srt = "1\n" "00:00:00,100 --> 00:00:02,000\n" "Hello\n"
        captions = SRTReader().read(srt)
        output = SCCWriter(drop_frame=False).write(captions)
        timestamps = re.findall(r"(\d{2}:\d{2}:\d{2}:\d{2})", output)
        assert timestamps[0] == "00:00:00:00"


class TestSCCWriterOverlappingCues:
    def test_overlapping_cues_suppress_clear_screen(self):
        """When cues are very close together, the clear-screen (942c) for
        the previous cue should be suppressed."""
        srt = (
            "1\n00:00:01,000 --> 00:00:01,900\nFirst\n\n"
            "2\n00:00:02,000 --> 00:00:03,000\nSecond\n"
        )
        captions = SRTReader().read(srt)
        output = SCCWriter(drop_frame=False).write(captions)
        # Count standalone 942c lines (clear-screen commands between captions)
        clear_lines = [
            line
            for line in output.split("\n")
            if line.strip().endswith("942c 942c") and "94ae" not in line
        ]
        # With tight cues, the first cue's clear should be suppressed
        # (only the last cue gets a clear-screen at its end time)
        assert len(clear_lines) <= 1


class TestSCCWriterSplitLongCaption:
    def test_split_caption_exceeding_80_tokens(self):
        """A caption that would exceed 80 SCC tokens should be split."""
        # Create a very long caption that will produce many code tokens
        long_text = "A" * 32 + "\n" + "B" * 32 + "\n" + "C" * 32 + "\n" + "D" * 32
        srt = "1\n" "00:00:05,000 --> 00:00:10,000\n" f"{long_text}\n"
        captions = SRTReader().read(srt)
        output = SCCWriter(drop_frame=False).write(captions)
        # Each output line (non-empty, non-header) should have <= 80 tokens
        for line in output.split("\n"):
            line = line.strip()
            if not line or line == "Scenarist_SCC V1.0":
                continue
            # Line format: "HH:MM:SS:FF\t<tokens>"
            parts = line.split("\t")
            if len(parts) == 2:
                tokens = parts[1].split()
                assert len(tokens) <= SCC_TOKENS_PER_CAPTION_MAX, (
                    f"Line has {len(tokens)} tokens, "
                    f"exceeds {SCC_TOKENS_PER_CAPTION_MAX}"
                )


class TestSCCWriterRoundTrip:
    def test_srt_to_scc_roundtrip_ndf(self):
        srt = (
            "1\n00:00:01,000 --> 00:00:03,000\nHello world\n\n"
            "2\n00:00:05,000 --> 00:00:07,000\nGoodbye world\n"
        )
        captions = SRTReader().read(srt)
        scc_output = SCCWriter(drop_frame=False).write(captions)
        # Should be readable by SCCReader
        result = SCCReader().read(scc_output)
        assert not result.is_empty()
        assert len(result.get_captions("en-US")) == 2

    def test_srt_to_scc_roundtrip_df(self):
        srt = (
            "1\n00:00:01,000 --> 00:00:03,000\nHello world\n\n"
            "2\n00:00:05,000 --> 00:00:07,000\nGoodbye world\n"
        )
        captions = SRTReader().read(srt)
        scc_output = SCCWriter(drop_frame=True).write(captions)
        # SCCReader already supports semicolon (DF) timestamps
        result = SCCReader().read(scc_output)
        assert not result.is_empty()
        assert len(result.get_captions("en-US")) == 2

    def test_webvtt_to_scc_roundtrip_df(self):
        vtt_input = (
            "WEBVTT\n\n"
            "0\n00:00:01.529 --> 00:00:03.640\n"
            "When it comes to finding the one,\n\n"
            "1\n00:00:03.730 --> 00:00:07.239\n"
            "I always say that if they can love you\n\n"
            "2\n00:00:07.570 --> 00:00:09.319\n"
            "calm you at your moodiest,\n"
        )
        captions = WebVTTReader().read(vtt_input)
        scc_output = SCCWriter(drop_frame=True).write(captions)
        result = SCCReader().read(scc_output)
        assert not result.is_empty()
        assert len(result.get_captions("en-US")) == 3


from pycaption.scc import SCC_TOKENS_PER_CAPTION_MAX  # noqa: E402
from pycaption.scc.constants import (  # noqa: E402
    MID_ROW_ITALIC,
    MID_ROW_ITALIC_UNDERLINE,
    MID_ROW_PLAIN,
    MID_ROW_UNDERLINE,
    WRITER_PAC_CODES,
)


class TestSCCWriterPositioning:
    def test_vtt_line_top_maps_to_row_1(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 line:0%\n" "Top of screen\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        pac_row_1 = WRITER_PAC_CODES[(1, 0, "plain")]
        assert pac_row_1 in output

    def test_vtt_line_bottom_maps_to_row_15(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 line:100%\n"
            "Bottom of screen\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        pac_row_15 = WRITER_PAC_CODES[(15, 0, "plain")]
        assert pac_row_15 in output

    def test_vtt_line_middle_maps_to_row_9(self):
        vtt = (
            "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 line:50%\n" "Middle of screen\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        pac_row_9 = WRITER_PAC_CODES[(9, 0, "plain")]
        assert pac_row_9 in output

    def test_vtt_no_position_defaults_to_bottom(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000\n" "Default position\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        pac_row_15 = WRITER_PAC_CODES[(15, 0, "plain")]
        assert pac_row_15 in output

    def test_vtt_align_left_indent_zero(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 align:left\n" "Left aligned\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        pac_col_0 = WRITER_PAC_CODES[(15, 0, "plain")]
        assert pac_col_0 in output

    def test_vtt_align_center_computes_indent(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 align:center\n" "Hi\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        # "Hi" is 2 chars, center = (32-2)//2 = 15, base_col=12, tab=3
        pac_col_12 = WRITER_PAC_CODES[(15, 12, "plain")]
        assert pac_col_12 in output

    def test_vtt_align_right_computes_indent(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000 align:right\n" "Hi\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        # "Hi" is 2 chars, right = 32-2 = 30 -> clamped to 28
        pac_col_28 = WRITER_PAC_CODES[(15, 28, "plain")]
        assert pac_col_28 in output


class TestSCCWriterStyles:
    def test_vtt_italic_emits_mid_row_code(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000\n" "Hello <i>world</i>\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert MID_ROW_ITALIC in output

    def test_vtt_underline_emits_mid_row_code(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000\n" "Hello <u>world</u>\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert MID_ROW_UNDERLINE in output

    def test_vtt_italic_underline_combined(self):
        vtt = (
            "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000\n" "Hello <i><u>world</u></i>\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert MID_ROW_ITALIC_UNDERLINE in output

    def test_vtt_italic_ends_with_plain_code(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000\n" "<i>hello</i> world\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert MID_ROW_PLAIN in output

    def test_vtt_bold_silently_dropped(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000\n" "<b>bold text</b>\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert MID_ROW_ITALIC not in output
        assert MID_ROW_UNDERLINE not in output
        # Still produces valid output with the text
        result = SCCReader().read(output)
        assert not result.is_empty()

    def test_vtt_class_span_silently_dropped(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "<c.yellow>colored text</c>\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert MID_ROW_ITALIC not in output
        result = SCCReader().read(output)
        assert not result.is_empty()

    def test_vtt_italic_at_line_start_uses_pac(self):
        vtt = "WEBVTT\n\n" "00:00:01.000 --> 00:00:03.000\n" "<i>all italic</i>\n"
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        pac_italic = WRITER_PAC_CODES[(15, 0, "italic")]
        assert pac_italic in output


class TestSCCWriterPositioningAndStylesCombined:
    def test_position_and_italic(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 line:0% align:left\n"
            "<i>top italic</i>\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        pac_row_1_italic = WRITER_PAC_CODES[(1, 0, "italic")]
        assert pac_row_1_italic in output

    def test_plain_text_roundtrip_unchanged(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000\n"
            "Hello world\n\n"
            "00:00:05.000 --> 00:00:07.000\n"
            "Second caption\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        result = SCCReader().read(output)
        assert not result.is_empty()
        caps = result.get_captions("en-US")
        assert len(caps) == 2
        assert "Hello world" in caps[0].get_text()
        assert "Second caption" in caps[1].get_text()

    def test_multiline_with_position(self):
        vtt = (
            "WEBVTT\n\n"
            "00:00:01.000 --> 00:00:03.000 line:20%\n"
            "Line one\nLine two\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        result = SCCReader().read(output)
        assert not result.is_empty()
        text = result.get_captions("en-US")[0].get_text()
        assert "Line one" in text
        assert "Line two" in text


class TestSCCWriterRollUp:
    def test_scroll_up_region_emits_roll_up_commands(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:scroll\n"
            "width:40%\n"
            "lines:3\n"
            "scroll:up\n\n"
            "00:00:01.000 --> 00:00:03.000 region:scroll\n"
            "First line\n\n"
            "00:00:03.000 --> 00:00:05.000 region:scroll\n"
            "Second line\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert "9426 9426" in output  # RU3
        assert "94ad 94ad" in output  # CR

    def test_scroll_up_uses_region_lines_for_depth(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:r2\n"
            "lines:2\n"
            "scroll:up\n\n"
            "00:00:01.000 --> 00:00:03.000 region:r2\n"
            "Text\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert "9425 9425" in output  # RU2

    def test_scroll_up_4_lines(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:r4\n"
            "lines:4\n"
            "scroll:up\n\n"
            "00:00:01.000 --> 00:00:03.000 region:r4\n"
            "Text\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert "94a7 94a7" in output  # RU4

    def test_mixed_scroll_and_pop_on(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:scroll\n"
            "lines:3\n"
            "scroll:up\n\n"
            "00:00:01.000 --> 00:00:03.000 region:scroll\n"
            "Roll-up text\n\n"
            "00:00:05.000 --> 00:00:07.000\n"
            "Pop-on text\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert "9426 9426" in output  # RU3 for scroll caption
        assert "9420 9420" in output  # RCL for pop-on caption

    def test_non_scroll_region_stays_pop_on(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:static\n"
            "width:40%\n"
            "lines:3\n\n"
            "00:00:01.000 --> 00:00:03.000 region:static\n"
            "No scroll\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        assert "9420 9420" in output  # Pop-on (RCL)
        assert "9426" not in output  # No roll-up

    def test_scroll_text_survives_roundtrip(self):
        vtt = (
            "WEBVTT\n\n"
            "REGION\n"
            "id:scroll\n"
            "lines:2\n"
            "scroll:up\n\n"
            "00:00:01.000 --> 00:00:03.000 region:scroll\n"
            "Hello world\n"
        )
        captions = WebVTTReader().read(vtt)
        output = SCCWriter().write(captions)
        result = SCCReader().read(output)
        assert not result.is_empty()
        text = result.get_captions("en-US")[0].get_text()
        assert "Hello world" in text


class TestSCCWriterPaintOn:
    def test_paint_on_emits_rdc_preamble(self):
        scc = (
            "Scenarist_SCC V1.0\n\n"
            "00:00:00;00\t9429 54e5 73f4\n\n"
            "00:00:04;00\t942c\n\n"
        )
        captions = SCCReader().read(scc)
        output = SCCWriter().write(captions)
        assert "9429 9429" in output
        assert "9420 9420" not in output

    def test_paint_on_text_survives_roundtrip(self):
        scc = (
            "Scenarist_SCC V1.0\n\n"
            "00:00:00;00\t9429 54e5 73f4\n\n"
            "00:00:04;00\t942c\n\n"
        )
        captions = SCCReader().read(scc)
        output = SCCWriter().write(captions)
        result = SCCReader().read(output)
        assert not result.is_empty()
        text = result.get_captions("en-US")[0].get_text()
        assert "Test" in text
