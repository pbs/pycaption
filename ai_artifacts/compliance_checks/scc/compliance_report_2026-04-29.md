# SCC EXHAUSTIVE Compliance Report

**Generated**: 2026-04-29
**Spec**: ai_artifacts/specs/scc/scc_specs_summary.md
**Analysis**: Deep Validation + Systematic Rules + Control Codes + Tests
**Implementation**: pycaption/scc/__init__.py, pycaption/scc/constants.py

---

## Executive Summary

**Rules checked**: 44/44 (100%)
**Total issues**: 21
**MUST violations**: 10

| Category | Count |
|----------|-------|
| Validation gaps | 8 |
| Implementation caveats | 2 |
| Missing rules | 9 (MUST: 5) |
| Test gaps | 2 |

---

## 1. Validation Gaps (8)

Rules where the concept is detected but not properly validated.

### RULE-TMC-002: Frame rate boundary validation
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: MUST
- **Note**: Code parses frame number (int(time_split[3]) / 30.0) but never checks frame < 30

### RULE-TMC-003: Monotonic timecode validation
- **Status**: NOT_IMPLEMENTED
- **Severity**: MUST
- **Note**: No code checks that timecodes increase. Silent timing adjustment is not validation.

### RULE-TMC-004: Drop-frame timecode validation
- **Status**: DETECTED_NOT_VALIDATED
- **Severity**: MUST
- **Note**: Distinguishes DF/NDF via ";" for time math, but 00:01:00;00 (invalid DF) accepted silently

### RULE-LAY-003: 15-row maximum
- **Status**: INHERENT_NOT_EXPLICIT
- **Severity**: SHOULD
- **Note**: PAC map limits positioning to rows 1-15, but no explicit count of simultaneous rows

### RULE-EDM-001: EDM ignored in paint-on and roll-up modes
- **Status**: MODE_RESTRICTED
- **Severity**: MUST
- **Note**: EDM (942c) handler only fires for pop-on: guarded by pop_ons_queue (pop-on only); paint-on EDM ignored; roll-up EDM ignored. Per CEA-608, EDM is a global command that clears displayed memory in ALL modes.

### IMPL-ZERO-001: caption.end zero-value truthiness bug
- **Status**: TRUTHINESS_BUG
- **Severity**: MUST
- **Note**: _force_default_timing uses `if caption.end:` — a caption starting at time 0 with end=0 would be overwritten silently

### IMPL-ERR-001: TypeError suppression in buffer.setter
- **Status**: SILENT_ERROR_SUPPRESSION
- **Severity**: SHOULD
- **Note**: buffer.setter: except TypeError: pass — data loss if mode not initialized before caption data arrives

### IMPL-ERR-002: AttributeError suppression in InstructionNodeCreator
- **Status**: SILENT_ERROR_SUPPRESSION
- **Severity**: SHOULD
- **Note**: Position tracking silently fails if position_tracker is None — captions get no positioning data

---

## 2. Implementation Caveats (2)

Rules implemented but with significant limitations.

### IMPL-RO-001: Writer drops all styling
- **Status**: READ_ONLY
- **Note**: Reader parses mid-row codes (italics, colors, underline) but writer outputs only PAC + character data. Round-trip loses all styling.

### IMPL-POS-001: Silent position fallback to (14, 0)
- **Status**: SILENT_FALLBACK
- **Note**: Captions without PAC commands silently land on row 14, col 0. No warning that positioning data is missing.

---

## 3. Missing Rules (9)

### MUST Rules (5)

- **RULE-ENC-001**: Bytes have odd parity in bit 6 (N/A for SCC text format) (MISSING)
- **RULE-ENC-002**: Bit 7 MUST be 0 in CEA-608 bytes (MISSING)
- **RULE-FPS-001**: MUST support 23.976 fps (film pulldown) (MISSING)
- **RULE-FPS-002**: MUST support 24 fps (film) (MISSING)
- **RULE-FPS-003**: MUST support 25 fps (PAL) (MISSING)

### SHOULD Rules (0)


### MAY/MUST NOT Rules (1)

- **RULE-XDS-001**: XDS packets use Field 2 of Line 21 (MISSING)

---

## 4. Control Code Coverage

| Category | Found | Note |
|----------|-------|------|
| Misc control codes | 13/19 | RCL, BS, EDM, CR, EOC, RU2/3/4, etc. |
| PAC entries | 497 | Positioning (rows 1-15, indents, colors) |
| Special characters | 16 | Two-byte special chars |
| Extended characters | 64 | Spanish, French, German, Portuguese |
| Total hex keys | 621 | All codes in constants.py |

## 5. Frame Rate Support

| Rate | Supported | How |
|------|-----------|-----|
| 23.976 fps | No | Not implemented |
| 24 fps | No | Not implemented |
| 25 fps | No | Not implemented |
| 29.97 NDF | **Yes** | Via `:` separator, 1001/1000 time factor |
| 29.97 DF | **Yes** | Via `;` separator, 1.0 time factor |
| 30 fps | Hardcoded | Frame division always uses `/ 30.0` |

**Note**: SCC is an NTSC format, so 29.97 DF/NDF is the primary use case. Missing support for other frame rates may be intentional.

---

## 6. Test Gaps (2)

- **RULE-PAINTON-001**: Paint-on MUST use RDC → PAC → text sequence
- **RULE-EDM-001**: EDM (942c) MUST clear displayed memory in all caption modes

---

## 7. Key Findings

1. **Timecode format is validated**: Regex checks HH:MM:SS:FF/HH:MM:SS;FF format, raises `CaptionReadTimingError` on bad format.
2. **Frame numbers NOT range-checked**: `int(time_split[3]) / 30.0` accepts any number. Frame 45 produces garbage time, no error.
3. **Monotonic timecodes NOT checked**: No code compares current timecode to previous. `TimingCorrectingCaptionList` silently adjusts end times — that's correction, not validation.
4. **Drop-frame invariant NOT validated**: Code distinguishes DF vs NDF via `;` for time math, but accepts `00:01:00;00` (invalid DF — frames 0,1 should be skipped at non-10th minutes).
5. **32-char line limit IS validated**: Reader raises `CaptionLineLengthError`, writer wraps at 32 via `textwrap.fill`. Both directions covered.
6. **Roll-up base row NOT validated**: `roll_rows_expected` is set to 2/3/4, but no check that PAC base row has enough rows above it.
7. **Frame rate is 29.97 only**: Hardcoded `/ 30.0` for frame division, `1001/1000` for NDF factor. No support for 23.976, 24, 25, or true 30fps.
8. **Control code doubling IS handled**: `_handle_double_command` correctly skips redundant doubled commands.
9. **RU4 hex code `94a7` is CORRECT**: Per CEA-608 odd-parity encoding, `94a7` (not `9427`) is the correct RU4 code.
10. **EDM (942c) is pop-on only**: The Erase Displayed Memory handler is guarded by `and self.pop_ons_queue`, so it only fires in pop-on mode. In paint-on and roll-up, EDM is silently discarded. Per CEA-608, EDM is a global command that clears the screen in ALL modes.

---

**Generated**: 2026-04-29 16:35
**Rules**: 44 | **Found**: 34 | **Missing**: 9
**Validation gaps**: 8 | **Test gaps**: 2
