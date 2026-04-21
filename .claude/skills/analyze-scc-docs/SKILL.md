---
name: analyze-scc-docs
description: Analyzes and validates comprehensive SCC specification coverage, ensuring all rules, formats, and best practices are documented with automated verification.
---

# analyze-scc-docs

## What this skill does

Generates unified, code-verifiable SCC specification (`scc_specs_summary.md`) as single source of truth for compliance checking.

**Outputs:**
1. Specification rules with unique IDs and test patterns
2. Generic implementation requirements (IMPL-###)
3. Self-validated structure
4. Source attribution

**Key:** Ensures NO requirements missed (parity, frame rates, character limits, protocol sequences, etc.)

---

## Implementation

### Step 1: Load Documentation

Read and analyze:
- `pycaption/specs/scc/standards_summary.md` (CEA-608/708)
- `pycaption/specs/scc/scc_web_summary.md` (web docs)
- `pycaption/specs/scc/web_sources.txt` (checked URLs)

### Step 2: Completeness Verification

**CRITICAL:** Verify ALL these areas covered (check standards_summary.md thoroughly):

**File Format:**
- Header: "Scenarist_SCC V1.0" exact match
- Timecode: HH:MM:SS:FF format, all frame rates (23.976, 24, 25, 29.97 DF/NDF, 30)
- Hex encoding: 4 digits, space-separated, control code doubling

**Byte Encoding (IMPORTANT - was missed):**
- Parity: Odd parity in bit 6 (mark as "N/A for SCC text format")
- Bit 7: Always 0
- Byte structure: 7 data + 1 parity

**Control Codes:**
- Miscellaneous: RCL, BS, DER, RU2/3/4, RDC, EDM, CR, ENM, EOC, etc.
- PAC codes: 128 positioning codes (rows 1-15, indents 0-28, colors, underline)
- Mid-row: Color/attribute changes
- Tab offsets: TO1/2/3
- Special characters: ®, °, ♪, etc.
- Extended characters: Spanish, French, German, Portuguese

**Caption Modes:**
- Pop-on protocol: RCL → PAC → text → EOC
- Roll-up protocol: RU2/3/4 → PAC → text → CR
- Paint-on protocol: RDC → PAC → text
- Mode transitions

**Layout Limits (IMPORTANT - was missed):**
- 32 characters per row maximum
- 15 rows maximum
- Base row validation for roll-up (must have room for rows)

**Timing:**
- Frame number limits per rate (0-23, 0-24, 0-29)
- Monotonic timecodes (increasing only)
- Drop-frame calculation rules

**Validation:**
- All MUST/SHOULD/MAY/MUST NOT requirements
- Protocol sequence validation
- Character set validation
- Error messages with rule IDs

**Identify gaps** - anything missing from above.

### Step 3: Web Search (if gaps exist)

Search for missing specs, exclude URLs in `web_sources.txt`.

### Step 4: Generate Specification

Create `pycaption/specs/scc/scc_specs_summary.md` with:

**Structure:**
```markdown
# SCC Specification - Complete Reference

## Part 1: File Format (RULE-FMT-###)
Header, timecode, hex encoding

## Part 2: Byte Encoding (RULE-ENC-###)
Parity (mark N/A for SCC), bit 7, structure

## Part 3: Control Codes (CTRL-###)
All 300+ with hex values, tables

## Part 4: Caption Modes (RULE-MODE-###)
Pop-on, roll-up, paint-on protocols, base row validation

## Part 5: Character Sets (RULE-CHAR-###)
Basic, special, extended, destructive behavior

## Part 6: Timing & Frames (RULE-TIME-###)
All frame rates, limits, monotonic requirement, drop-frame

## Part 7: Layout (RULE-LAY-###)
32 chars/row, 15 rows, positioning

## Part 8: Protocols (RULE-PROTO-###)
Mode sequences, state transitions

## Part 9: Implementation Requirements (IMPL-###)
Generic requirements mapping to code

## Part 10: Validation Summary
Rules count, self-validation report

## Appendices
Quick reference, sources
```

**Rule Format:**
```markdown
**[RULE-XXX-###]** Brief requirement
- **Requirement:** What must be true
- **Level:** MUST | SHOULD | MAY | MUST NOT
- **Validation:** How to check
- **Test Pattern:** Regex or algorithm
- **Sources:** [Attribution]
```

**Implementation Rule Format (GENERIC - no pycaption references):**
```markdown
**[IMPL-XXX-###]** Component MUST do X
- **Spec Rule:** RULE-XXX-###
- **Component:** Parser | Writer | Validator
- **Implementation Requirement:** What ANY compliant implementation must do
- **Expected Behavior:** Input → Output examples
- **Validation Criteria:** What to verify
- **Common Patterns:** Correct vs incorrect (generic)
- **Test Coverage:** Required test scenarios
```

**Critical Requirements to Include:**

**Parity (from standards_summary.md:1896-1898):**
```markdown
**[RULE-ENC-001]** Bytes MUST have odd parity
- **Applicability:** N/A for SCC text format (parity pre-encoded in hex)
- **Note:** Relevant for raw transmission, not SCC files

**[IMPL-ENC-001]** Parser MAY skip parity for SCC
- Parity already encoded in hex values
```

**Character/Row Limits (from standards_summary.md:2504-2505):**
```markdown
**[RULE-LAY-001]** MUST NOT exceed 32 characters per row
**[RULE-LAY-002]** MUST NOT exceed 15 rows total
**[RULE-MODE-001]** Roll-up MUST have valid base row (≥ roll-up depth)
```

**Frame Rates:**
```markdown
**[RULE-TIME-001]** Frame numbers MUST be valid for rate
- 23.976 fps: 0-23
- 24 fps: 0-23
- 25 fps: 0-24
- 29.97 fps DF/NDF: 0-29
- 30 fps: 0-29
```

**Protocols:**
```markdown
**[RULE-PROTO-001]** Pop-on: RCL → text → EOC
**[RULE-PROTO-002]** Roll-up: RU2/3/4 → text → CR
**[RULE-PROTO-003]** Paint-on: RDC → text
```

### Step 5: Quality Validation

**Structure checks:**
- All rule IDs unique
- Sequential numbering
- Valid test patterns

**Content checks:**
- 300+ control codes
- 50+ MUST, 25+ SHOULD, 15+ MAY rules
- Parity rules documented (RULE-ENC-001, IMPL-ENC-001)
- Frame rate rules for all rates
- Character limits (RULE-LAY-001/002)
- Protocol sequences (RULE-PROTO-001/002/003)
- Base row validation (RULE-MODE-001)
- All IMPL rules generic (no pycaption-specific references)

**Generate validation report:**
```markdown
## Validation Report
- Total RULE-###: X
- Total IMPL-###: Y
- Total CTRL-###: 300+
- Parity documented: ✅
- Frame rates documented: ✅
- Character limits documented: ✅
- Status: ✅ PASS | ❌ FAIL
```

If FAIL, fix and re-validate.

### Step 6: Source Attribution

Track sources for each rule:
- CEA-608-E section (Primary)
- CEA-708-E section (Primary)
- scc_web_summary.md line (Confirms)
- Confidence: High/Medium/Low

Document conflicts and resolutions.

### Step 7: Update Web Sources

Append new URLs to `pycaption/specs/scc/web_sources.txt`.

---

## Output Files

1. **`pycaption/specs/scc/scc_specs_summary.md`** - Complete specification
2. **`pycaption/specs/scc/web_sources.txt`** - Updated URL list

---

## Success Criteria

**Completeness (CRITICAL):**
- ✅ 300+ control codes documented
- ✅ All frame rates (5 variants)
- ✅ Parity rules (RULE-ENC-001, IMPL-ENC-001, marked N/A for SCC)
- ✅ Character limits (32/row, 15 rows)
- ✅ Base row validation
- ✅ Protocol sequences
- ✅ 50+ MUST, 25+ SHOULD, 15+ MAY rules
- ✅ All caption modes

**Quality:**
- ✅ Unique rule IDs
- ✅ Valid test patterns
- ✅ Source attribution
- ✅ Generic IMPL rules (no pycaption references)

**Usability:**
- ✅ Parseable by check-scc-compliance
- ✅ Error messages can reference rule IDs
- ✅ Ready for code compliance checking

---

## Important Notes

**Generic Implementation Rules:**
- DO: Describe what any compliant implementation must do
- DO: Provide validation criteria
- DON'T: Reference pycaption-specific files/classes/methods
- WHY: check-scc-compliance discovers actual code structure

**Missed Requirements Prevention:**
- Parity: From standards_summary.md:1896-1898 (mark N/A for SCC)
- Character limits: From standards_summary.md:2504-2505
- Base row: From standards_summary.md:231-232, 1768-1778
- Frame rates: From standards_summary.md (all 5 variants)
- Protocol sequences: From caption mode sections

**Thoroughness:**
- Read standards_summary.md completely
- Extract ALL MUST/SHOULD/MAY statements
- Document even if "N/A for SCC" (for completeness)
- Verify against completeness checklist in Step 2
