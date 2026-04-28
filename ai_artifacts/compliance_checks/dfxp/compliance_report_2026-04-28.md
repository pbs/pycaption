# DFXP/TTML EXHAUSTIVE Compliance Report

**Generated**: 2026-04-28
**Spec**: ai_artifacts/specs/dfxp/dfxp_specs_summary.md
**Analysis**: Deep Validation + Systematic Rules + Coverage + Tests
**Implementation files**: pycaption/dfxp/base.py, pycaption/dfxp/extras.py, pycaption/dfxp/__init__.py, pycaption/geometry.py

---

## Executive Summary

**Rules checked**: 115/115 (100%)
**Total issues**: 77
**MUST violations**: 30

| Category | Count |
|----------|-------|
| Validation gaps | 3 |
| Partial/caveats | 9 |
| Missing rules | 60 (MUST: 25) |
| Test gaps | 5 |

---

## 1. Validation Gaps (3)

Rules that are not properly implemented or validated.

### RULE-TIME-002: Clock-time frames hardcoded to /30
- **Status**: HARDCODED_FRAME_RATE
- **Severity**: MUST
- **Note**: int(frames) / 30 * MICROSECONDS_PER_UNIT["seconds"] — ignores ttp:frameRate

### RULE-TIME-014: ttp:frameRate not implemented
- **Status**: NOT_IMPLEMENTED
- **Severity**: MUST
- **Note**: Code never reads ttp:frameRate. Default 30fps used always.

### RULE-STY-002: tts:backgroundColor not implemented
- **Status**: NOT_IMPLEMENTED
- **Severity**: SHOULD
- **Note**: _convert_style has no case for tts:backgroundColor. _recreate_style does not write it. Completely missing.

---

## 2. Implementation Caveats (9)

Rules implemented but with significant limitations.

### RULE-DOC-001: Root tt element detection
- **Status**: DETECTED_NOT_VALIDATED
- **Note**: detect() uses "</tt>" in content.lower() (substring), not proper root element check

### RULE-DOC-003: xml:lang attribute
- **Status**: READ_NOT_VALIDATED
- **Note**: Reads with silent fallback to DEFAULT_LANGUAGE_CODE ("en"), no BCP-47 validation

### IMPL-007: Color handling
- **Status**: PASSTHROUGH_ONLY
- **Note**: tts:color passed through as raw string. No validation of color format (hex, named, rgba).

### RULE-STY-006: fontWeight/bold read-only
- **Status**: READ_NOT_WRITTEN
- **Note**: Reader: attrs["bold"]=True from tts:fontWeight. Writer: _recreate_style omits tts:fontWeight. Bold lost on write.

### RULE-STY-008: textDecoration/underline read-only
- **Status**: READ_NOT_WRITTEN
- **Note**: Reader: attrs["underline"]=True from tts:textDecoration. Writer: _recreate_style omits tts:textDecoration. Underline lost on write.

### IMPL-004: Region resolver silently drops conflicting regions
- **Status**: SILENT_ERROR_SUPPRESSION
- **Note**: except LookupError: return — conflicting descendant regions cause silent None region. No warning or error raised.

### RULE-STY-005: fontStyle only handles italic
- **Status**: PARTIAL_VALUES
- **Note**: Reader checks tts:fontStyle=="italic" only. "oblique" and "normal" values silently ignored.

### IMPL-008: Silent &apos; workaround
- **Status**: SILENT_WORKAROUND
- **Note**: markup.replace("&apos;", "'") silently rewrites valid XML entity before parsing. Could mask malformed input.

### RULE-STY-006: LegacyDFXPWriter also drops bold
- **Status**: READ_NOT_WRITTEN
- **Note**: extras.py LegacyDFXPWriter._recreate_style also omits tts:fontWeight. Same gap as base.py.

---

## 3. Missing Rules (60)

### MUST Rules (25)

- **RULE-DOC-006**: `head` element structure MUST follow prescribed child ordering (MISSING)
- **RULE-DOC-007**: Media type MUST be `application/ttml+xml` (MISSING)
- **RULE-LAY-005**: Region `tts:origin` positioning (NO_PATTERN)
- **RULE-LAY-006**: Region `tts:extent` dimensions (NO_PATTERN)
- **RULE-PAR-001**: `ttp:timeBase` - time reference base (MISSING)
- **RULE-PAR-002**: `ttp:frameRate` - frames per second (MISSING)
- **RULE-PROF-001**: DFXP Transformation Profile (MISSING)
- **RULE-PROF-002**: DFXP Presentation Profile (MISSING)
- **RULE-PROF-005**: Profile feature designations (MISSING)
- **RULE-SMOD-006**: Inline styling via `tts:*` attributes on content elements (NO_PATTERN)
- **RULE-SMOD-007**: Style association from region to content (NO_PATTERN)
- **RULE-STY-009**: `tts:direction` - text direction (MISSING)
- **RULE-STY-010**: `tts:writingMode` - writing mode (MISSING)
- **RULE-STY-011**: `tts:display` - display mode (MISSING)
- **RULE-STY-013**: `tts:lineHeight` - line height (MISSING)
- **RULE-STY-019**: `tts:overflow` - region overflow behavior (MISSING)
- **RULE-STY-020**: `tts:showBackground` - background visibility (MISSING)
- **RULE-STY-021**: `tts:visibility` - element visibility (MISSING)
- **RULE-STY-022**: `tts:wrapOption` - text wrapping (MISSING)
- **RULE-STY-023**: `tts:unicodeBidi` - bidirectional override (MISSING)
- **RULE-STY-025**: Named colors - complete enumeration (MISSING)
- **RULE-STY-026**: Color expression formats (MISSING)
- **RULE-TIME-012**: Default time container is parallel (`par`) (MISSING)
- **RULE-TIME-013**: Time containment: children constrained by parent (MISSING)
- **RULE-VAL-006**: `xml:lang` MUST be valid BCP 47 (NO_PATTERN)

### SHOULD Rules (5)

- **RULE-DOC-008**: XML declaration SHOULD specify UTF-8 encoding (NO_PATTERN)
- **RULE-LAY-007**: Region stacking and z-ordering (NO_PATTERN)
- **RULE-PAR-011**: `ttp:profile` attribute - profile designation (MISSING)
- **RULE-PROF-004**: Profile element vs attribute precedence (MISSING)
- **RULE-VAL-007**: Percentage values SHOULD be in valid range (NO_PATTERN)

### MAY/MUST NOT Rules (20)

- **RULE-CONT-006**: `set` element for animation (MISSING)
- **RULE-CONT-008**: `div` nesting is permitted (MISSING)
- **RULE-META-001**: `ttm:title` - document title (MISSING)
- **RULE-META-002**: `ttm:desc` - description (MISSING)
- **RULE-META-003**: `ttm:copyright` - copyright information (MISSING)
- **RULE-META-004**: `ttm:agent` - agent definition (MISSING)
- **RULE-META-005**: `ttm:actor` - actor reference (MISSING)
- **RULE-META-006**: `ttm:role` attribute on content elements (MISSING)
- **RULE-PAR-003**: `ttp:subFrameRate` - sub-frame rate (MISSING)
- **RULE-PAR-004**: `ttp:frameRateMultiplier` - frame rate scaling (MISSING)
- **RULE-PAR-005**: `ttp:tickRate` - tick rate (MISSING)
- **RULE-PAR-006**: `ttp:dropMode` - frame dropping mode (MISSING)
- **RULE-PAR-007**: `ttp:clockMode` - clock interpretation (MISSING)
- **RULE-PAR-008**: `ttp:markerMode` - marker semantics (MISSING)
- **RULE-PAR-010**: `ttp:pixelAspectRatio` - pixel aspect ratio (MISSING)
- **RULE-PROF-003**: DFXP Full Profile (MISSING)
- **RULE-STY-014**: `tts:opacity` - element opacity (MISSING)
- **RULE-STY-015**: `tts:textOutline` - text outline/shadow (MISSING)
- **RULE-STY-024**: `tts:zIndex` - region stacking order (MISSING)
- **RULE-VAL-008**: Unknown elements in TT namespace MUST NOT appear (NO_PATTERN)

---

## 4. Coverage Analysis

### Styling Attributes (11/24 read, 9/24 write, 9/24 round-trip)

| Attribute | Read | Write | Round-trip | Note |
|-----------|------|-------|------------|------|
| `tts:color` | Yes | Yes | Yes | Full round-trip (raw string passthrough) |
| `tts:backgroundColor` | No | No | No | Not implemented |
| `tts:fontSize` | Yes | Yes | Yes | Full round-trip |
| `tts:fontFamily` | Yes | Yes | Yes | Full round-trip |
| `tts:fontStyle` | Yes | Yes | Yes | Full round-trip (italic only) |
| `tts:fontWeight` | Yes | No | No | READ-ONLY: Reader detects bold, writer silently drops it |
| `tts:textAlign` | Yes | Yes | Yes | Full round-trip (also via LayoutInfoScraper) |
| `tts:textDecoration` | Yes | No | No | READ-ONLY: Reader detects underline, writer silently drops it |
| `tts:direction` | No | No | No | Not implemented |
| `tts:writingMode` | No | No | No | Not implemented |
| `tts:display` | No | No | No | Not implemented (distinct from tts:displayAlign) |
| `tts:displayAlign` | Yes | Yes | Yes | Full round-trip via LayoutInfoScraper + _create_external_alignment |
| `tts:lineHeight` | No | No | No | Not implemented |
| `tts:opacity` | No | No | No | Not implemented |
| `tts:textOutline` | No | No | No | Not implemented |
| `tts:padding` | Yes | Yes | Yes | Full round-trip via LayoutInfoScraper + _convert_layout_to_attributes |
| `tts:extent` | Yes | Yes | Yes | Full round-trip via LayoutInfoScraper. Root tt extent must be in pixels. |
| `tts:origin` | Yes | Yes | Yes | Full round-trip via LayoutInfoScraper |
| `tts:overflow` | No | No | No | Not implemented |
| `tts:showBackground` | No | No | No | Not implemented |
| `tts:visibility` | No | No | No | Not implemented |
| `tts:wrapOption` | No | No | No | Not implemented |
| `tts:unicodeBidi` | No | No | No | Not implemented |
| `tts:zIndex` | No | No | No | Not implemented |

### Time Expression Formats (7/8)

| Format | Supported | Note |
|--------|-----------|------|
| Clock-time fractional (HH:MM:SS.sss) | Yes | Via CLOCK_TIME_PATTERN sub_frames group, .ljust(3, "0") |
| Clock-time frames (HH:MM:SS:FF) | Yes | Parsed but hardcoded /30 (ignores ttp:frameRate) |
| Offset hours (Nh) | Yes | Supported |
| Offset minutes (Nm) | Yes | Supported |
| Offset seconds (Ns) | Yes | Supported |
| Offset milliseconds (Nms) | Yes | Supported |
| Offset frames (Nf) | Yes | Parsed but hardcoded /30 (ignores ttp:frameRate) |
| Offset ticks (Nt) | No | Raises NotImplementedError |

### Content Elements (9/11 read, 9/11 write)

| Element | Read | Write |
|---------|------|-------|
| `<body>` | Yes | Yes |
| `<div>` | Yes | Yes |
| `<p>` | Yes | Yes |
| `<span>` | Yes | Yes |
| `<br>` | Yes | Yes |
| `<set>` | No | No |
| `<styling>` | Yes | Yes |
| `<style>` | Yes | Yes |
| `<layout>` | Yes | Yes |
| `<region>` | Yes | Yes |
| `<metadata>` | No | No |

### Parameter Attributes (0/11 read from document)

| Attribute | Read | Note |
|-----------|------|------|
| `ttp:timeBase` | No | Not read (media assumed) |
| `ttp:frameRate` | No | Not read (hardcoded /30) |
| `ttp:subFrameRate` | No | Not implemented |
| `ttp:frameRateMultiplier` | No | Not implemented |
| `ttp:tickRate` | No | Not read (tick raises NotImplementedError) |
| `ttp:dropMode` | No | Not implemented |
| `ttp:clockMode` | No | Not implemented |
| `ttp:markerMode` | No | Not implemented |
| `ttp:cellResolution` | No | Not read (hardcoded 32x15 defaults in geometry.py) |
| `ttp:pixelAspectRatio` | No | Not implemented |
| `ttp:profile` | No | Not implemented |

### Length Units (5/5)

| Unit | Supported |
|------|-----------|
| px (pixel) | Yes |
| em | Yes |
| % (percent) | Yes |
| c (cell) | Yes |
| pt (point) | Yes |

---

## 5. Test Gaps (5)

- **RULE-STY-001**: `tts:color` - foreground/text color
- **RULE-STY-003**: `tts:fontSize` - font size
- **RULE-STY-006**: `tts:fontWeight` - font weight
- **RULE-STY-008**: `tts:textDecoration` - text decoration
- **RULE-SMOD-003**: Style referencing via `style` attribute

---

## 6. Key Findings

1. **Frame rate hardcoded to /30**: Both clock-time frames (HH:MM:SS:FF) and offset frames (Nf) divide by 30. The code never reads `ttp:frameRate` from the document. This affects any TTML file with non-30fps frame references.
2. **Tick time raises NotImplementedError**: `_convert_time_count_to_microseconds` recognizes the `t` metric but raises `NotImplementedError` instead of computing. Also can't compute without `ttp:tickRate` (which is never read).
3. **Zero ttp: parameters read from document**: None of the 11 TTML parameter attributes (ttp:timeBase, ttp:frameRate, ttp:tickRate, ttp:cellResolution, etc.) are actually read from the input. All use hardcoded defaults.
4. **fontWeight (bold) and textDecoration (underline) are READ-ONLY**: Reader correctly detects these attributes, but `_recreate_style()` has no case for "bold" or "underline" keys — they are silently dropped on write. Round-trip DFXP→pycaption→DFXP loses bold and underline styling.
5. **tts:display is NOT implemented** (distinct from tts:displayAlign which IS implemented). Previous audit had a false positive where `tts:display` pattern matched `tts:displayAlign` as a substring.
6. **xml:lang reads with silent fallback**: `dfxp_document.tt.attrs.get("xml:lang", DEFAULT_LANGUAGE_CODE)` falls back to "en" silently. No BCP-47 validation of the language code.
7. **Color passed through as raw string**: `tts:color` is read and written but never parsed or validated. Named colors, hex, and rgba() formats are all passed through without checking.
8. **Style chaining IS implemented**: `_get_style_reference_chain` follows style references recursively, with duplicate xml:id detection raising `CaptionReadSyntaxError`.
9. **Region resolution IS implemented**: Full ancestor→descendant lookup via `_determine_region_id`, region creation via `RegionCreator`, and unused region cleanup.
10. **detect() uses substring check**: `"</tt>" in content.lower()` matches anywhere in the content, not proper XML root validation.
11. **Root tt extent validated**: `_find_root_extent` correctly requires root `tts:extent` to be in pixel units, raising `CaptionReadSyntaxError` otherwise.
12. **Cell resolution uses hardcoded 32x15**: geometry.py's `as_percentage_of` uses 32 columns and 15 rows as default cell resolution instead of reading `ttp:cellResolution`.
13. **5 length units supported**: px, em, %, c (cell), pt — all via `Size.from_string()` in geometry.py.
14. **tts:backgroundColor NOT supported**: Despite being one of the most common TTML styling attributes, it's not read or written.

---

**Generated**: 2026-04-28 23:05
**Rules**: 115 | **Found**: 53 | **Missing**: 60
**Styling**: 9/24 round-trip (2 read-only) | **Timing**: 7/8 | **Elements**: 9/11 read | **Params**: 0/11
