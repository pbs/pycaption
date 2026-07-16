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

_ROLL_UP_COMMANDS = {2: "9425", 3: "9426", 4: "94a7"}
_CARRIAGE_RETURN = "94ad"
_RESUME_DIRECT_CAPTIONING = "9429"


def _update_style(node, italic, underline):
    """Update italic/underline state from a STYLE node."""
    content = node.content
    if not isinstance(content, dict):
        return italic, underline
    if node.start:
        italic = italic or bool(content.get("italics"))
        underline = underline or bool(content.get("underline"))
    else:
        if content.get("italics"):
            italic = False
        if content.get("underline"):
            underline = False
    return italic, underline


def _skip_consumed_spaces(line_text, offset, wrap_line):
    """Advance offset past spaces that textwrap consumed at a break point."""
    while offset < len(line_text) and line_text[offset] == " ":
        if line_text[offset : offset + len(wrap_line)] == wrap_line:
            break
        offset += 1
    return offset


class SCCWriter(BaseWriter):
    def __init__(self, *args, drop_frame=False, **kw):
        super().__init__(*args, **kw)
        self.drop_frame = drop_frame

    def write(self, caption_set):
        """Convert a CaptionSet to SCC format string.

        Captions are emitted in chronological order. Each caption's mode
        (pop-on, roll-up, paint-on) determines its CEA-608 preamble.
        """
        output = HEADER + "\n\n"

        if caption_set.is_empty():
            return output

        caption_set = deepcopy(caption_set)

        lang = list(caption_set.get_languages())[0]
        captions = caption_set.get_captions(lang)
        regions = caption_set.get_regions()
        scroll_regions = {
            rid for rid, settings in regions.items() if settings.get("scroll") == "up"
        }

        classified = self._classify_captions(captions, scroll_regions, regions)
        codes = self._encode_all(classified)
        codes = self._adjust_timing(codes)
        codes = self._deduplicate_timestamps(codes)
        output += self._render_mixed(codes)

        return output

    def _classify_captions(self, captions, scroll_regions, regions):
        """Assign a mode and depth to each caption, preserving input order."""
        result = []
        for caption in captions:
            mode = getattr(caption, "caption_mode", None)
            if mode == "roll_up":
                depth = getattr(caption, "roll_up_rows", None) or 3
                result.append((caption, "roll_up", depth))
            elif mode == "paint_on":
                result.append((caption, "paint_on", 0))
            else:
                region_id = self._get_caption_region_id(caption)
                if region_id and region_id in scroll_regions:
                    depth = int(regions[region_id].get("lines", "3"))
                    result.append((caption, "roll_up", depth))
                else:
                    result.append((caption, "pop_on", 0))
        return result

    def _encode_all(self, classified):
        """Encode all captions into (code, start, end, mode, depth) tuples."""
        return [
            (self._text_to_code(cap), cap.start, cap.end, mode, depth)
            for cap, mode, depth in classified
        ]

    @staticmethod
    def _get_caption_region_id(caption):
        """Extract region id from a caption's webvtt_positioning string."""
        layout = caption.layout_info
        if not layout or not layout.webvtt_positioning:
            return None
        for setting in layout.webvtt_positioning.split():
            if setting.startswith("region:"):
                return setting[7:]
        return None

    @staticmethod
    def _adjust_timing(codes):
        """Shift each cue's start time earlier to account for buffer write
        time. SCC decoders need time to receive all code words before
        displaying; this backshift ensures the caption appears on screen at
        the intended moment. Also suppresses the previous cue's clear-screen
        command (sets end=None) when two cues would overlap in the stream."""
        for index, (code, start, end, mode, depth) in enumerate(codes):
            code_words = len(code.split()) + _SCC_OVERHEAD
            code_time_microseconds = code_words * MICROSECONDS_PER_CODEWORD
            code_start = max(0, start - code_time_microseconds)

            if index == 0:
                codes[index] = (code, code_start, end, mode, depth)
                continue

            prev_code, prev_start, prev_end, prev_mode, prev_depth = codes[index - 1]
            if code_start <= prev_start + MICROSECONDS_PER_CODEWORD:
                prev_words = len(prev_code.split()) + _SCC_OVERHEAD
                code_start = max(
                    code_start,
                    prev_start + prev_words * MICROSECONDS_PER_CODEWORD,
                )
                codes[index] = (code, code_start, end, mode, depth)
                codes[index - 1] = (prev_code, prev_start, None, prev_mode, prev_depth)
            else:
                if (
                    prev_end is not None
                    and prev_end + 3 * MICROSECONDS_PER_CODEWORD >= code_start
                ):
                    codes[index - 1] = (
                        prev_code,
                        prev_start,
                        None,
                        prev_mode,
                        prev_depth,
                    )
                codes[index] = (code, code_start, end, mode, depth)

        return codes

    def _deduplicate_timestamps(self, codes):
        """Ensure monotonically increasing frame values across cues.
        If two cues would land on the same frame, nudge the later one
        forward by one codeword duration until it occupies a unique frame."""
        last_emitted_frame = -1
        for index, (code, start, end, mode, depth) in enumerate(codes):
            cur_frame = self._microseconds_to_frame(start)
            if cur_frame <= last_emitted_frame:
                while self._microseconds_to_frame(start) <= last_emitted_frame:
                    start += MICROSECONDS_PER_CODEWORD
                codes[index] = (code, start, end, mode, depth)
            last_emitted_frame = self._microseconds_to_frame(start)
        return codes

    def _render_mixed(self, codes):
        """Serialize all cues in chronological order, emitting mode-appropriate
        preambles inline. Handles pop-on (ENM+RCL...EDM+EOC), roll-up
        (EDM on mode entry, RU+CR), and paint-on (RDC) seamlessly."""
        output = ""
        max_payload = SCC_TOKENS_PER_CAPTION_MAX - _SCC_OVERHEAD
        prev_mode = None

        for code, start, end, mode, depth in codes:
            ts = self._format_timestamp(start)

            if mode == "pop_on":
                code_tokens = code.split()
                if len(code_tokens) + _SCC_OVERHEAD <= SCC_TOKENS_PER_CAPTION_MAX:
                    output += f"{ts}\t"
                    output += "94ae 94ae 9420 9420 "
                    output += code
                    output += "942c 942c 942f 942f\n\n"
                else:
                    offset = 0
                    while offset < len(code_tokens):
                        chunk = code_tokens[offset : offset + max_payload]
                        if offset == 0:
                            line = ["94ae", "94ae", "9420", "9420"] + chunk
                        else:
                            line = chunk
                        is_last = offset + max_payload >= len(code_tokens)
                        if is_last:
                            line = line + ["942c", "942c", "942f", "942f"]
                        output += (
                            f"{self._format_timestamp(start)}\t"
                            + " ".join(line)
                            + "\n\n"
                        )
                        offset += max_payload
                        if not is_last:
                            start += MICROSECONDS_PER_CODEWORD

            elif mode == "roll_up":
                cap_ru = _ROLL_UP_COMMANDS.get(min(max(depth, 2), 4), "9426")
                output += f"{ts}\t"
                if prev_mode != "roll_up":
                    output += "942c 942c "
                output += f"{cap_ru} {cap_ru} "
                output += f"{_CARRIAGE_RETURN} {_CARRIAGE_RETURN} "
                output += code
                output += "\n\n"

            elif mode == "paint_on":
                output += f"{ts}\t"
                output += f"{_RESUME_DIRECT_CAPTIONING} {_RESUME_DIRECT_CAPTIONING} "
                output += code
                output += "\n\n"

            if end is not None:
                output += f"{self._format_timestamp(end)}\t942c 942c\n\n"

            prev_mode = mode

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
        for unmapped characters. Special/extended chars (4-byte codes)
        are control-like and must be doubled per CEA-608."""
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
            code = self._maybe_align(code)
            code += f"{char_code} {char_code} "
            return code
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
        If layout info has a Y percentage, reverses the reader's formula
        (y% = 90*(row-1)/15 + 5) to recover the original row. Multi-line
        captions stack downward from the base row, clamped at row 15.
        Without layout info, uses bottom-up placement from row 15."""
        layout = caption.layout_info
        if layout and layout.origin and layout.origin.y:
            y = layout.origin.y
            if y.unit == UnitEnum.PERCENT:
                base_row = max(1, min(15, round((y.value - 5) / 90.0 * 15) + 1))
            else:
                base_row = 15
            row = base_row + line_index
            return min(row, 15)
        return max(1, min(15, 16 - num_lines + line_index))

    @staticmethod
    def _compute_scc_indent(caption, line_text):
        """Map horizontal position to a CEA-608 column (0-31).
        Reverses the reader's formula (x% = 80*col/32 + 10) to recover
        the original column. Falls back to alignment-based centering/right
        for non-SCC sources. Returns (base_col, tab_offset) where base_col
        is a multiple of 4 and tab_offset is 0-3."""
        layout = caption.layout_info
        if not layout:
            return 0, 0

        if layout.origin and layout.origin.x:
            x = layout.origin.x
            if x.unit == UnitEnum.PERCENT and x.value > 10:
                raw_col = max(0, min(31, round((x.value - 10) / 80.0 * 32)))
                base_col = (raw_col // 4) * 4
                tab_offset = raw_col - base_col
                return min(base_col, 28), tab_offset

        if not layout.alignment:
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
                mid_row = (
                    MID_ROW_ITALIC_UNDERLINE if initial_underline else MID_ROW_ITALIC
                )
                code = self._emit_command(code, mid_row)

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
                global_offset = _skip_consumed_spaces(
                    line_text, global_offset, wrap_line
                )
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
        italic = False
        underline = False

        for node in nodes:
            if node.type_ == CaptionNode.BREAK:
                lines.append([])
            elif node.type_ == CaptionNode.STYLE:
                italic, underline = _update_style(node, italic, underline)
            elif node.type_ == CaptionNode.TEXT and node.content:
                lines[-1].append((node.content, italic, underline))

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
        emits a mid-row code when the style actually changes between segments.
        Strips one leading space from text after a mid-row code since the
        code itself produces a visible space on screen."""
        for text, seg_italic, seg_underline in segments:
            if seg_italic != current_italic or seg_underline != current_underline:
                mid_row = self._get_mid_row_code(seg_italic, seg_underline)
                code = self._emit_command(code, mid_row)
                current_italic = seg_italic
                current_underline = seg_underline
                if text.startswith(" "):
                    text = text[1:]

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
