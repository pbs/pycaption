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
- `ai_artifacts/specs/scc/standards_summary.md` (CEA-608/708)
- `ai_artifacts/specs/scc/scc_web_summary.md` (web docs)
- `ai_artifacts/specs/scc/scc_web_sources.md` (checked URLs)

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

Search for missing specs, exclude URLs in `scc_web_sources.md`.

### Step 4: Generate Specification

Create `ai_artifacts/specs/scc/scc_specs_summary.md` with:

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

Append new URLs to `ai_artifacts/specs/scc/scc_web_sources.md`.

### Step 8: Post-Generation Validation Against Master Checklist

**CRITICAL:** After generating the spec, run this validation script. If it reports FAIL, fix the spec and re-run until PASS.

```python
import re

print("=" * 60)
print("POST-GENERATION VALIDATION: SCC")
print("Checking scc_specs_summary.md against master_checklist.md")
print("=" * 60)

with open('ai_artifacts/specs/scc/master_checklist.md') as _f: checklist = _f.read()
with open('ai_artifacts/specs/scc/scc_specs_summary.md') as _f: spec = _f.read()

failures = []
warnings = []

# 1. Check all required rule IDs
rule_ids = re.findall(r'^- ((?:RULE|IMPL)-[A-Z]+-\d{3})', checklist, re.M)
for rid in rule_ids:
    if rid not in spec:
        failures.append(f"MISSING RULE: {rid}")
print(f"[1/5] Rule IDs: {len(rule_ids) - len([f for f in failures if 'RULE' in f])}/{len(rule_ids)}")

# 2. Check required control code hex values
hex_codes = re.findall(r'^- ([0-9a-f]{4})\s+#', checklist, re.M)
for code in hex_codes:
    if code not in spec.lower():
        failures.append(f"MISSING CONTROL CODE: {code}")
print(f"[2/5] Control codes: {len(hex_codes) - len([f for f in failures if 'CONTROL' in f])}/{len(hex_codes)}")

# 3. Check required enum values
enum_sections = re.findall(r'### (.+?)\n((?:- .+\n)+)', checklist)
for section_name, values_block in enum_sections:
    values = re.findall(r'^- (.+)$', values_block, re.M)
    for val in values:
        val_clean = val.strip()
        if val_clean not in spec:
            # Try case-insensitive for colors/modes
            if not re.search(re.escape(val_clean), spec, re.I):
                warnings.append(f"MISSING ENUM [{section_name}]: {val_clean}")
print(f"[3/5] Enum values: checked {sum(len(re.findall(r'^- .+$', vb, re.M)) for _, vb in enum_sections)} values")

# 4. Check severity distribution
severity_section = re.search(r'## Required Severity Distribution\n((?:.*\n)*)', checklist)
if severity_section:
    for match in re.finditer(r'- (MUST|SHOULD|MAY|MUST NOT): (\d+)', severity_section.group(1)):
        level, minimum = match.group(1), int(match.group(2))
        actual = len(re.findall(rf'Level:\*\*\s*{re.escape(level)}\b', spec))
        if actual < minimum:
            failures.append(f"SEVERITY {level}: found {actual}, need >= {minimum}")
        print(f"[4/5] {level}: {actual} (min {minimum}) {'PASS' if actual >= minimum else 'FAIL'}")

# 5. Check control code category coverage
for category in ['PAC', 'Mid-row', 'Special character', 'Extended character', 'XDS']:
    if not re.search(category.replace('-', '.'), spec, re.I):
        warnings.append(f"MISSING CATEGORY: {category}")
print(f"[5/5] Control code categories checked")

# Report
print("\n" + "=" * 60)
if failures:
    print(f"FAIL: {len(failures)} failures, {len(warnings)} warnings\n")
    for f in failures:
        print(f"  FAIL: {f}")
    for w in warnings:
        print(f"  WARN: {w}")
    print("\nFix the spec and re-run this validation.")
else:
    print(f"PASS: All checks passed ({len(warnings)} warnings)")
    for w in warnings:
        print(f"  WARN: {w}")
print("=" * 60)
```

**If FAIL:** Fix the missing items in the spec, then re-run the validation script. Repeat until PASS.

---

## Output Files

1. **`ai_artifacts/specs/scc/scc_specs_summary.md`** - Complete specification
2. **`ai_artifacts/specs/scc/scc_web_sources.md`** - Updated URL list

---

## Success Criteria

**Master Checklist Validation (CRITICAL - must PASS):**
- All rule IDs from `master_checklist.md` present in generated spec
- All control code hex values present
- All enum values present
- Severity distribution meets minimums
- All control code categories documented

**Completeness:**
- 300+ control codes documented
- All frame rates (5 variants)
- Parity rules (RULE-ENC-001, IMPL-ENC-001, marked N/A for SCC)
- Character limits (32/row, 15 rows)
- Base row validation
- Protocol sequences
- All caption modes

**Quality:**
- Unique rule IDs
- Valid test patterns
- Source attribution
- Generic IMPL rules (no pycaption references)

**Usability:**
- Parseable by check-scc-compliance
- Error messages can reference rule IDs
- Ready for code compliance checking

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
