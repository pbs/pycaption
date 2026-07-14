import math
import textwrap
from copy import deepcopy

from pycaption.base import BaseWriter, CaptionNode
from pycaption.geometry import HorizontalAlignmentEnum, UnitEnum

from .constants import (
    CHARACTER_TO_CODE,
    HEADER,
    MICROSECONDS_PER_CODEWORD,
    MID_ROW_ITALIC,
    MID_ROW_ITALIC_UNDERLINE,
    MID_ROW_PLAIN,
    MID_ROW_UNDERLINE,
    PAC_HIGH_BYTE_BY_ROW,
    PAC_LOW_BYTE_BY_ROW_RESTRICTED,
    SPECIAL_OR_EXTENDED_CHAR_TO_CODE,
    TAB_OFFSET_CODES,
    WRITER_PAC_CODES,
)

SCC_TOKENS_PER_CAPTION_MAX = 80

_SCC_PREFIX = ["94ae", "94ae", "9420", "9420"]
_SCC_SUFFIX = ["942c", "942c", "942f", "942f"]
_SCC_OVERHEAD = len(_SCC_PREFIX) + len(_SCC_SUFFIX)


class SCCWriter(BaseWriter):
    def __init__(self, *args, drop_frame=False, **kw):
        super().__init__(*args, **kw)
        self.drop_frame = drop_frame

    def write(self, caption_set):
        """Convert a CaptionSet to SCC format string.

        Runs a 4-pass pipeline: encode captions to hex codes, adjust timing
        to account for buffer write time, deduplicate timestamps, then
        serialize to the final SCC text.
        """
        output = HEADER + "\n\n"

        if caption_set.is_empty():
            return output

        caption_set = deepcopy(caption_set)

        lang = list(caption_set.get_languages())[0]
        captions = caption_set.get_captions(lang)

        codes = self._compute_caption_codes(captions)
        codes = self._adjust_timing(codes)
        codes = self._deduplicate_timestamps(codes)
        output += self._render_output(codes)

        return output

    def _compute_caption_codes(self, captions):
        """Encode each caption's text, positioning, and styling into SCC hex
        code sequences. Returns a list of (code, start, end) tuples."""
        return [
            (self._text_to_code(caption), caption.start, caption.end)
            for caption in captions
        ]

    def _adjust_timing(self, codes):
        """Shift each cue's start time earlier to account for pop-on buffer
        write time. SCC decoders need time to receive all code words before
        displaying; this backshift ensures the caption appears on screen at
        the intended moment. Also suppresses the previous cue's clear-screen
        command (sets end=None) when two cues would overlap in the stream."""
        for index, (code, start, end) in enumerate(codes):
            code_words = len(code.split()) + _SCC_OVERHEAD
            code_time_microseconds = code_words * MICROSECONDS_PER_CODEWORD
            code_start = max(0, start - code_time_microseconds)

            if index == 0:
                codes[index] = (code, code_start, end)
                continue

            previous_code, previous_start, previous_end = codes[index - 1]
            if code_start <= previous_start + MICROSECONDS_PER_CODEWORD:
                prev_words = len(previous_code.split()) + _SCC_OVERHEAD
                code_start = max(
                    code_start,
                    previous_start + prev_words * MICROSECONDS_PER_CODEWORD,
                )
                codes[index] = (code, code_start, end)
                codes[index - 1] = (previous_code, previous_start, None)
            else:
                if (
                    previous_end is not None
                    and previous_end + 3 * MICROSECONDS_PER_CODEWORD >= code_start
                ):
                    codes[index - 1] = (previous_code, previous_start, None)
                codes[index] = (code, code_start, end)

        return codes

    def _deduplicate_timestamps(self, codes):
        """Ensure monotonically increasing frame values across cues.
        If two cues would land on the same frame, nudge the later one
        forward by one codeword duration until it occupies a unique frame."""
        last_emitted_frame = -1
        for index, (code, start, end) in enumerate(codes):
            cur_frame = self._microseconds_to_frame(start)
            if cur_frame <= last_emitted_frame:
                while self._microseconds_to_frame(start) <= last_emitted_frame:
                    start += MICROSECONDS_PER_CODEWORD
                codes[index] = (code, start, end)
            last_emitted_frame = self._microseconds_to_frame(start)
        return codes

    def _render_output(self, codes):
        """Serialize encoded cues to SCC text lines. Each cue is wrapped with
        the standard prefix (ENM + RCL) and suffix (EDM + EOC). Cues exceeding
        SCC_TOKENS_PER_CAPTION_MAX are split across multiple timestamp lines."""
        output = ""
        max_payload = SCC_TOKENS_PER_CAPTION_MAX - _SCC_OVERHEAD

        for code, start, end in codes:
            code_tokens = code.split()
            if len(code_tokens) + _SCC_OVERHEAD <= SCC_TOKENS_PER_CAPTION_MAX:
                output += f"{self._format_timestamp(start)}\t"
                output += "94ae 94ae 9420 9420 "
                output += code
                output += "942c 942c 942f 942f\n\n"
            else:
                offset = 0
                while offset < len(code_tokens):
                    chunk = code_tokens[offset : offset + max_payload]
                    line = _SCC_PREFIX + chunk + _SCC_SUFFIX
                    output += (
                        f"{self._format_timestamp(start)}\t" + " ".join(line) + "\n\n"
                    )
                    offset += max_payload
                    if offset < len(code_tokens):
                        start += MICROSECONDS_PER_CODEWORD

            if end is not None:
                output += f"{self._format_timestamp(end)}\t942c 942c\n\n"

        return output

    @staticmethod
    def _maybe_align(code):
        """Pad the code string to a word boundary with a no-op byte (0x80).
        SCC is word-based (4 hex chars = 2 bytes per word); control codes
        must start at a word boundary."""
        if len(code) % 5 == 2:
            code += "80 "
        return code

    @staticmethod
    def _maybe_space(code):
        """Append a space separator after a complete 4-char hex word."""
        if len(code) % 5 == 4:
            code += " "
        return code

    def _print_character(self, code, char):
        """Encode a single character and append it to the code string.
        Looks up the character in the standard table first, then
        special/extended characters. Falls back to the pound sign (£)
        for unmapped characters. Aligns to word boundary before emitting
        4-byte special/extended character codes."""
        try:
            char_code = CHARACTER_TO_CODE[char]
        except KeyError:
            try:
                char_code = SPECIAL_OR_EXTENDED_CHAR_TO_CODE[char]
            except KeyError:
                char_code = "91b6"

        if len(char_code) == 2:
            return code + char_code
        elif len(char_code) == 4:
            return self._maybe_align(code) + char_code
        else:
            return code

    def _emit_command(self, code, command):
        """Emit a CEA-608 control code, double-struck per spec requirements.
        Aligns to word boundary first, then writes the command twice."""
        code = self._maybe_align(code)
        code += f"{command} {command} "
        return code

    @staticmethod
    def _compute_scc_row(caption, num_lines, line_index):
        """Map a caption's vertical position to a CEA-608 row (1-15).
        If layout info has a Y percentage, maps 0%->row 1 through
        100%->row 15. Multi-line captions (up to 4 lines per CEA-608
        convention) stack downward from the base row, clamped at row 15.
        Without layout info, uses bottom-up placement from row 15."""
        layout = caption.layout_info
        if layout and layout.origin and layout.origin.y:
            y = layout.origin.y
            if y.unit == UnitEnum.PERCENT:
                base_row = max(1, min(15, round(y.value / 100.0 * 14) + 1))
            else:
                base_row = 15
            row = base_row + line_index
            return min(row, 15)
        return max(1, min(15, 16 - num_lines + line_index))

    @staticmethod
    def _compute_scc_indent(caption, line_text):
        """Map horizontal alignment to a CEA-608 column position.
        Returns (base_col, tab_offset) where base_col is a multiple of 4
        (the PAC grid) and tab_offset is 0-3 for fine positioning via
        Tab Offset commands. Left-aligned or unspecified returns (0, 0)."""
        layout = caption.layout_info
        if not layout or not layout.alignment:
            return 0, 0

        h_align = layout.alignment.horizontal
        text_len = len(line_text)

        if h_align == HorizontalAlignmentEnum.CENTER:
            raw_col = max(0, (32 - text_len) // 2)
        elif h_align in (HorizontalAlignmentEnum.RIGHT, HorizontalAlignmentEnum.END):
            raw_col = max(0, 32 - text_len)
        else:
            return 0, 0

        base_col = (raw_col // 4) * 4
        tab_offset = raw_col - base_col
        return min(base_col, 28), tab_offset

    @staticmethod
    def _get_pac_code(row, col, italic=False, underline=False):
        """Look up the PAC (Preamble Address Code) for the given row, column,
        and style. At column 0 all four style combinations are available;
        at columns 4-28 only plain and underline exist in CEA-608.
        Falls back to the basic row PAC if no exact match is found."""
        if col == 0:
            if italic and underline:
                style = "italic_underline"
            elif italic:
                style = "italic"
            elif underline:
                style = "underline"
            else:
                style = "plain"
        else:
            style = "underline" if underline else "plain"

        code = WRITER_PAC_CODES.get((row, col, style))
        if code:
            return code
        return PAC_HIGH_BYTE_BY_ROW[row] + PAC_LOW_BYTE_BY_ROW_RESTRICTED[row]

    @staticmethod
    def _get_mid_row_code(italic, underline):
        """Return the mid-row style code for the given style combination.
        Mid-row codes change text styling mid-line (after the PAC has already
        set the initial style for the line start)."""
        if italic and underline:
            return MID_ROW_ITALIC_UNDERLINE
        elif italic:
            return MID_ROW_ITALIC
        elif underline:
            return MID_ROW_UNDERLINE
        else:
            return MID_ROW_PLAIN

    def _text_to_code(self, caption):
        """Convert a caption's nodes into a complete SCC hex code string.
        Walks the node tree to extract styled text segments, wraps long lines
        at the 32-character SCC limit, then emits PAC positioning, tab offsets,
        mid-row style codes, and encoded characters for each output line."""
        nodes = caption.nodes
        styled_lines = self._build_styled_lines(nodes)
        wrapped_lines = self._wrap_styled_lines(styled_lines)

        code = ""
        num_lines = len(wrapped_lines)

        for line_index, segments in enumerate(wrapped_lines):
            line_text = "".join(text for text, _, _ in segments)
            row = self._compute_scc_row(caption, num_lines, line_index)
            col, tab_offset = self._compute_scc_indent(caption, line_text)

            initial_italic, initial_underline = self._get_line_initial_style(segments)
            pac_code = self._get_pac_code(row, col, initial_italic, initial_underline)
            code = self._maybe_align(code)
            code += f"{pac_code} {pac_code} "

            if tab_offset > 0:
                tab_code = TAB_OFFSET_CODES.get(tab_offset)
                if tab_code:
                    code = self._maybe_align(code)
                    code += f"{tab_code} {tab_code} "

            if col > 0 and initial_italic:
                code = self._emit_command(code, MID_ROW_ITALIC)

            code = self._emit_styled_segments(
                code, segments, initial_italic, initial_underline
            )
            code = self._maybe_align(code)

        return code

    @staticmethod
    def _wrap_styled_lines(styled_lines, max_width=32):
        """Break lines exceeding max_width while preserving per-character
        style metadata. Uses textwrap.fill to determine break points on the
        plain text, then slices the styled segments at matching boundaries.
        Skips whitespace consumed at wrap points (textwrap eats the space
        where it breaks)."""
        result = []
        for segments in styled_lines:
            line_text = "".join(text for text, _, _ in segments)
            if len(line_text) <= max_width:
                result.append(segments)
                continue
            wrapped = textwrap.fill(line_text, max_width).split("\n")
            global_offset = 0
            for wrap_line in wrapped:
                while (
                    global_offset < len(line_text) and line_text[global_offset] == " "
                ):
                    if (
                        line_text[global_offset : global_offset + len(wrap_line)]
                        == wrap_line
                    ):
                        break
                    global_offset += 1
                wrap_segments = SCCWriter._slice_segments(
                    segments, global_offset, len(wrap_line)
                )
                global_offset += len(wrap_line)
                if wrap_segments:
                    result.append(wrap_segments)
        return result

    @staticmethod
    def _slice_segments(segments, start_offset, length):
        """Extract a substring of the given length starting at start_offset
        from a list of styled segments. Each segment is a (text, italic,
        underline) tuple. Returns a new list of segments covering exactly
        the requested character range, preserving style on each slice."""
        result = []
        chars_needed = length
        seg_global_pos = 0

        for text, italic, underline in segments:
            seg_end_pos = seg_global_pos + len(text)
            if seg_end_pos <= start_offset:
                seg_global_pos = seg_end_pos
                continue
            start_in_seg = max(0, start_offset - seg_global_pos)
            available = len(text) - start_in_seg
            take = min(available, chars_needed)
            if take > 0:
                result.append(
                    (text[start_in_seg : start_in_seg + take], italic, underline)
                )
                chars_needed -= take
            if chars_needed <= 0:
                break
            seg_global_pos = seg_end_pos

        return result

    @staticmethod
    def _build_styled_lines(nodes):
        """Walk a caption's flat node list and produce a structured
        representation: a list of lines, where each line is a list of
        (text, italic, underline) tuples. Tracks style state by watching
        STYLE open/close nodes. Filters out empty lines."""
        lines = [[]]
        current_italic = False
        current_underline = False

        for node in nodes:
            if node.type_ == CaptionNode.BREAK:
                lines.append([])
            elif node.type_ == CaptionNode.STYLE:
                content = node.content
                if not isinstance(content, dict):
                    continue
                if node.start:
                    if content.get("italics"):
                        current_italic = True
                    if content.get("underline"):
                        current_underline = True
                else:
                    if content.get("italics"):
                        current_italic = False
                    if content.get("underline"):
                        current_underline = False
            elif node.type_ == CaptionNode.TEXT:
                if node.content:
                    lines[-1].append((node.content, current_italic, current_underline))

        return [line for line in lines if line]

    @staticmethod
    def _get_line_initial_style(segments):
        """Return the (italic, underline) style of the first segment in a line.
        Used to determine whether the PAC can carry the initial style directly
        (avoiding a separate mid-row code at column 0)."""
        if segments:
            _, italic, underline = segments[0]
            return italic, underline
        return False, False

    def _emit_styled_segments(self, code, segments, current_italic, current_underline):
        """Encode a line's styled segments into SCC hex, emitting mid-row
        codes at style transitions. Tracks the running style state and only
        emits a mid-row code when the style actually changes between segments."""
        for text, seg_italic, seg_underline in segments:
            if seg_italic != current_italic or seg_underline != current_underline:
                mid_row = self._get_mid_row_code(seg_italic, seg_underline)
                code = self._emit_command(code, mid_row)
                current_italic = seg_italic
                current_underline = seg_underline

            for char in text:
                code = self._print_character(code, char)
                code = self._maybe_space(code)

        return code

    def _format_timestamp(self, microseconds):
        """Format microseconds as an SCC timestamp string, using either
        drop-frame (semicolon separator) or non-drop-frame (colon separator)
        depending on the writer's configuration."""
        if self.drop_frame:
            return self._format_timestamp_df(microseconds)
        return self._format_timestamp_ndf(microseconds)

    def _microseconds_to_frame(self, microseconds):
        """Convert microseconds to a frame count for timestamp deduplication.
        Applies the 1000/1001 NTSC pulldown factor for both modes."""
        if self.drop_frame:
            return math.floor(microseconds * 30 / 1_000_000 * 1000 / 1001 + 1e-9)
        seconds_float = microseconds / 1_000_000.0 * 1000.0 / 1001.0
        return math.floor(seconds_float * 30)

    @staticmethod
    def _format_timestamp_ndf(microseconds):
        """Format as non-drop-frame timecode (HH:MM:SS:FF).
        Applies the 1000/1001 pulldown: 1 second of timecode = 1.001 real
        seconds. Frames are computed at 30fps within each second."""
        seconds_float = microseconds / 1_000_000.0
        seconds_float *= 1000.0 / 1001.0
        hours = math.floor(seconds_float / 3600)
        seconds_float -= hours * 3600
        minutes = math.floor(seconds_float / 60)
        seconds_float -= minutes * 60
        seconds = math.floor(seconds_float)
        seconds_float -= seconds
        frames = math.floor(seconds_float * 30)
        return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

    @staticmethod
    def _format_timestamp_df(microseconds):
        """Format as drop-frame timecode (HH:MM:SS;FF).
        Skips frames 0 and 1 at each minute boundary (except every 10th
        minute) to keep timecode in sync with wall-clock time at 29.97fps."""
        total_frames = math.floor(microseconds * 30 / 1_000_000 * 1000 / 1001 + 1e-9)
        fps = 30
        frames_per_10min = 17982  # 10*60*30 - 2*9
        d = total_frames // frames_per_10min
        m = total_frames % frames_per_10min
        if m < 2:
            tc_frames = total_frames + 18 * d
        else:
            tc_frames = total_frames + 18 * d + 2 * ((m - 2) // 1798)

        hours = tc_frames // (fps * 60 * 60)
        rem = tc_frames % (fps * 60 * 60)
        minutes = rem // (fps * 60)
        rem = rem % (fps * 60)
        seconds = rem // fps
        frames = rem % fps
        return f"{hours:02}:{minutes:02}:{seconds:02};{frames:02}"
