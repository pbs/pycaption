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
