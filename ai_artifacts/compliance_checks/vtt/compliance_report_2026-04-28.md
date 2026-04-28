# WebVTT EXHAUSTIVE Compliance Report

**Generated**: 2026-04-28
**Spec**: ai_artifacts/specs/vtt/vtt_specs_summary.md (76 rules)
**Implementation**: pycaption/webvtt.py
**Analysis**: Deep Validation + Systematic Rules + Coverage + Tests

---

## Executive Summary

**Rules checked**: 76/76 (100%)
**Total issues**: 65
**MUST violations**: 12

| Category | Count |
|----------|-------|
| Validation gaps | 10 |
| Implementation caveats | 3 |
| Missing rules | 36 (MUST: 9) |
| Tag round-trip gaps | 5/8 |
| Setting parse gaps | 6/6 |
| Entity gaps | 1/7 |
| Test gaps | 4 |

---

## 1. Validation Gaps (10)

### RULE-SET-002: Zero-value cue settings silently dropped
- **Status**: TRUTHINESS_BUG
- **Severity**: MUST
- **Note**: `if position:` is falsy for 0. Cues at position:0/line:0/size:0 lose positioning. Affected: position, line, size. Fix: use `is not None` checks.

### RULE-FMT-001: WEBVTT header
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: MUST
- **Note**: detect() uses substring check, not first-line validation

### RULE-FMT-002: UTF-8 encoding
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: MUST
- **Note**: Checks isinstance(content, str) but no explicit UTF-8 decode validation

### RULE-TIME-006: Monotonic timestamps
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: SHOULD
- **Note**: DISABLED BY DEFAULT (ignore_timing_errors=True)

### RULE-SET-002: Zero-value position/line/size dropped on write
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: MAY
- **Note**: Writer uses truthiness check instead of `is not None`: position=True, line=True, size=True

### RULE-SET-005: Center alignment silently dropped on write
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: MAY
- **Note**: Writer skips align:center assuming it is the default. Explicit center alignment lost on round-trip. Logic bug: DEFAULT_ALIGN is "start" but center is dropped as if it were the default. Explicit center alignment is valid and should be preserved.

### RULE-VAL-007: Timing validation disabled by default
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: SHOULD
- **Note**: ignore_timing_errors defaults to True. Invalid timing (start>end, non-monotonic) silently accepted.

### IMPL-PARSE-006: Tag stripping destroys all inline formatting
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: UNKNOWN
- **Note**: OTHER_SPAN_PATTERN.sub("", ...) strips all tags. VTT→VTT round-trip loses italic, bold, underline, class, lang, ruby.

### IMPL-WRITE-003: Writer drops zero-hours in timestamps
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: UNKNOWN
- **Note**: `if hh:` omits hours when 0. Produces MM:SS.mmm. Valid per spec but non-reversible (reader may have had HH:MM:SS.mmm).

### IMPL-WRITE-002: Entity encoding partially commented out
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: UNKNOWN
- **Note**: &lrm;, &rlm;, &gt;, &nbsp; encoding explicitly commented out in _encode_illegal_characters.

---

## 2. Implementation Caveats (3)

Rules implemented but with significant limitations.

### RULE-TIME-003: Milliseconds exactly 3 digits
- **Status**: IMPLEMENTED_WITH_CAVEATS
- **Note**: Enforced by TIMESTAMP_PATTERN regex \d{3}

### RULE-TIME-005: Start time <= end time
- **Status**: IMPLEMENTED_WITH_CAVEATS
- **Note**: DISABLED BY DEFAULT (ignore_timing_errors=True)

### RULE-CUE-001: Timing separator -->
- **Status**: IMPLEMENTED_WITH_CAVEATS
- **Note**: TIMING_LINE_PATTERN captures arrow with surrounding whitespace

---

## 3. Missing Rules (36)

### MUST Rules (9)

- **RULE-BLK-003**: STYLE block MUST precede first cue (MISSING)
- **RULE-ENT-007**: Numeric character references (MISSING)
- **RULE-REG-002**: Region setting: id (required) (MISSING)
- **RULE-REG-009**: All region identifiers MUST be unique (MISSING)
- **RULE-TIME-007**: Internal timestamps within cue boundaries (MISSING)
- **RULE-VAL-001**: Keywords MUST be case-sensitive (MISSING)
- **RULE-VAL-002**: Cue identifiers MUST be unique (MISSING)
- **RULE-VAL-003**: Region identifiers MUST be unique (MISSING)
- **RULE-VAL-006**: Authoring tools MUST generate conforming files (MISSING)

### SHOULD Rules (1)

- **RULE-CUE-004**: Cue identifier SHOULD be unique (MISSING)

### MAY/MUST NOT Rules (25)

- **RULE-BLK-001**: NOTE blocks for comments (MISSING)
- **RULE-BLK-002**: STYLE blocks for CSS (MISSING)
- **RULE-BLK-004**: STYLE block cannot contain "-->" (MISSING)
- **RULE-CUE-002**: Cue identifier MUST NOT contain "-->" (MISSING)
- **RULE-CUE-003**: Cue identifier MUST NOT contain line terminators (MISSING)
- **RULE-CUE-006**: Cue payload MUST NOT contain "-->" (MISSING)
- **RULE-FMT-003**: Optional UTF-8 BOM MAY be present (MISSING)
- **RULE-REG-001**: REGION block defines region (MISSING)
- **RULE-REG-003**: Region setting: width (percentage) (MISSING)
- **RULE-REG-004**: Region setting: lines (integer) (MISSING)
- **RULE-REG-005**: Region setting: regionanchor (x%,y%) (MISSING)
- **RULE-REG-006**: Region setting: viewportanchor (x%,y%) (MISSING)
- **RULE-REG-007**: Region setting: scroll (up) (MISSING)
- **RULE-REG-008**: Each region setting appears once maximum (MISSING)
- **RULE-SET-003**: Setting: position (N% [,alignment]) (MISSING)
- **RULE-SET-004**: Setting: size (N%) (MISSING)
- **RULE-SET-006**: Setting: region (id) (MISSING)
- **RULE-SET-007**: Each setting appears maximum once per cue (MISSING)
- **RULE-SET-008**: Region setting excludes vertical/line/size (MISSING)
- **RULE-TAG-001**: Class span: `<c>...</c>` or `<c.class>...</c>` (MISSING)
- **RULE-TAG-006**: Language: `<lang bcp47>...</lang>` (MISSING)
- **RULE-TAG-007**: Ruby: `<ruby>...<rt>...</rt></ruby>` (MISSING)
- **RULE-TAG-008**: Internal timestamp: `<HH:MM:SS.mmm>` (MISSING)
- **RULE-TAG-009**: Tags support class notation (MISSING)
- **RULE-VAL-005**: Unicode MUST NOT be normalized (MISSING)

---

## 4. Coverage Analysis

### Tags (3/8 round-trip)

| Tag | Read | Write | Round-trip | Note |
|-----|------|-------|------------|------|
| `<c>` | Yes (strip) | No | No | Reader strips via OTHER_SPAN_PATTERN (matches [cibuv]) |
| `<i>` | Yes (strip) | Yes | Yes | Reader strips via OTHER_SPAN_PATTERN, writer generates from style nodes |
| `<b>` | Yes (strip) | Yes | Yes | Reader strips via OTHER_SPAN_PATTERN, writer generates from style nodes |
| `<u>` | Yes (strip) | Yes | Yes | Reader strips via OTHER_SPAN_PATTERN, writer generates from style nodes |
| `<v>` | Yes (strip) | No | No | Reader extracts speaker annotation, strips tag |
| `<lang>` | No | No | No | Stripped by OTHER_SPAN_PATTERN, not individually parsed |
| `<ruby>/<rt>` | No | No | No | Stripped by OTHER_SPAN_PATTERN, not individually parsed |
| `<timestamp>` | No | No | No | Stripped by OTHER_SPAN_PATTERN, not individually parsed |

### Cue Settings (0/6 parsed, 0/6 written)

| Setting | Parsed | Written | Note |
|---------|--------|---------|------|
| `vertical` | No | No | Reader stores raw string via Layout(webvtt_positioning=...), no individual parsing |
| `line` | No | No | Writer generates from layout origin.y |
| `position` | No | No | Writer generates from layout origin.x |
| `size` | No | No | Writer generates from layout extent.horizontal |
| `align` | No | No | Writer generates from layout alignment |
| `region` | No | No | Not implemented |

### Entities (6/7 read, 4/7 write)

| Entity | Read (decode) | Write (encode) |
|--------|---------------|----------------|
| `&amp;` | Yes | Yes |
| `&lt;` | Yes | Yes |
| `&gt;` | Yes | Yes |
| `&nbsp;` | Yes | Yes |
| `&lrm;` | Yes | No |
| `&rlm;` | Yes | No |
| `&#ref` | No | No |

---

## 5. Test Gaps (4)

- **RULE-TIME-006**: Cue start times SHOULD be non-decreasing
- **RULE-CUE-001**: Cue timing separator MUST be ` --> `
- **IMPL-WRITE-002**: Writer MUST escape special chars
- **IMPL-WRITE-003**: Writer MUST format timestamps correctly

---

## 6. Key Findings

1. **Reader strips all tags** except voice annotation: `<c>`, `<i>`, `<b>`, `<u>`, `<lang>`, `<ruby>`, `<rt>`, timestamp tags are all removed by `OTHER_SPAN_PATTERN.sub("", ...)`. Only `<v>` speaker name is extracted.
2. **Writer generates `<i>`, `<b>`, `<u>`** from internal style nodes (when converting from other formats), but VTT-to-VTT loses all tags.
3. **Cue settings stored as raw string** in reader (`Layout(webvtt_positioning=cue_settings)`). No individual setting parsing (vertical, line, position, size, align, region).
4. **Writer generates settings** (line, position, size, align) from structured Layout data when converting from other formats.
5. **Timing validation exists but is DISABLED by default** (`ignore_timing_errors=True`). Start<=end and monotonic checks are opt-in.
6. **Entity decode is complete** (reader handles &amp;, &lt;, &gt;, &nbsp;, &lrm;, &rlm;). **Entity encode is partial** (writer only encodes &amp;, &lt;, and --> to --&gt;). &lrm;/&rlm; encoding is commented out.
7. **STYLE blocks not implemented** (explicit TODO in code). REGION blocks not implemented.
8. **Header detection is overly permissive**: `"WEBVTT" in content` matches substring anywhere, not first-line-only.

---

**Generated**: 2026-04-28 23:05
**Rules**: 76 | **Found**: 40 | **Missing**: 36
**Tags**: 3/8 round-trip | **Settings**: 0/6 parsed | **Entities**: 6/7 read, 4/7 write
