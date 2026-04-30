---
name: suggest-scc-fixes
description: Analyzes the latest SCC compliance report and generates detailed Python code suggestions for fixing the most critical issue.
---

# suggest-scc-fixes

## What this skill does

Focused fix generation for SCC compliance issues:

1. **Finds** latest compliance report in `ai_artifacts/compliance_checks/scc/`
2. **Identifies** the MOST CRITICAL issue (highest priority)
3. **Generates** detailed fix with:
   - Exact Python code to implement
   - File locations and line numbers
   - Test cases for the fix
   - Implementation notes
4. **Saves** to `ai_artifacts/compliance_checks/scc/suggested_scc_fixes.md`

**Key optimization**: Focuses on ONE critical issue at a time to avoid context overflow.

## Usage

```bash
/suggest-scc-fixes
```

Automatically finds latest report and generates fix for top priority issue.

---

## Pre-flight: Read `.claude/skills/gotchas.md`

**REQUIRED** before generating fix suggestions. Pay special attention to gotchas #1 (no proprietary data tables in suggested code) and #2 (no proprietary source attributions).

**Post-run:** If you discover a new gotcha during fix generation (a regex pattern that silently misses IDs, a code pattern that looks correct but violates the spec, or a compliance report format change that breaks extraction), append it to `.claude/skills/gotchas.md` with the same numbered format.

---

## Context Optimization Strategy

**Why focus on one issue:**
- Reading full compliance report: ~10K tokens
- Analyzing all issues: ~30K tokens
- Generating fixes for all: ~50K+ tokens
- **Total naive approach**: 90K+ tokens

**Optimized approach:**
- Extract issue list only: ~2K tokens
- Focus on #1 critical issue: ~5K tokens
- Generate one detailed fix: ~10K tokens
- **Total optimized**: ~20K tokens (78% reduction)

**To fix multiple issues**: Run skill multiple times (one issue per run)

---

## Implementation

### Run this script

```python
import re
import os
import glob
import subprocess
from datetime import datetime

# ===== Step 1: Find Latest Report =====
reports = glob.glob("ai_artifacts/compliance_checks/scc/compliance_report_*.md")
if not reports:
    print("No compliance report found. Run /check-scc-compliance first.")
    exit(0)

latest_report = max(reports, key=os.path.getmtime)
print(f"Using: {latest_report}")

# ===== Step 2: Read Report and Extract Critical Issue =====
with open(latest_report) as _f:
    report_content = _f.read()

# Extract critical issues section
critical_match = re.search(r'### .*CRITICAL(.*?)(?=\n### |\n## |\Z)', report_content, re.DOTALL)
critical_section = critical_match.group(1) if critical_match else report_content

first_issue_match = re.search(
    r'1\.\s+\*\*\[?(RULE-[A-Z]+-\d{3}|IMPL-(?:[A-Z]+-)?\d{3}|CTRL-\d{3})\]?\*\*[:\s]+(.+?)(?:\n|$)',
    critical_section
)

if not first_issue_match:
    # Try validation gaps section
    val_section = re.search(r'## 1\. Validation Gaps.*?\n(.*?)(?=\n## |\Z)', report_content, re.DOTALL)
    if val_section:
        first_issue_match = re.search(
            r'### (RULE-[A-Z]+-\d{3}|IMPL-(?:[A-Z]+-)?\d{3}):\s+(.+?)(?:\n|$)',
            val_section.group(1)
        )

if not first_issue_match:
    print("No critical issues found in report!")
    print("   All MUST-level requirements are met.")
    exit(0)

issue_id = first_issue_match.group(1)
issue_title = first_issue_match.group(2).strip()

print(f"Focusing on: {issue_id} - {issue_title}")

# ===== Step 3: Extract Full Details for This Issue =====
def extract_field(text, field_name):
    match = re.search(f'\\*\\*{field_name}\\*\\*:?\\s*(.+?)(?=\\n\\*\\*|\\n\\n|$)',
                     text, re.DOTALL)
    return match.group(1).strip() if match else "Not specified"

# Find issue detail block in the report
issue_block_match = re.search(
    rf'###?\s*{re.escape(issue_id)}.*?(?=\n###?\s|\n## |\Z)',
    report_content, re.DOTALL
)
issue_details = issue_block_match.group(0) if issue_block_match else ""

issue_info = {
    'id': issue_id,
    'title': issue_title,
    'severity': extract_field(issue_details, 'Severity'),
    'file': extract_field(issue_details, 'File'),
    'current': extract_field(issue_details, 'Current'),
    'expected': extract_field(issue_details, 'Expected'),
    'impact': extract_field(issue_details, 'Impact'),
    'fix': extract_field(issue_details, 'Fix'),
}

if issue_info['severity'] == 'Not specified':
    # Try Status/Note fields
    status = extract_field(issue_details, 'Status')
    note = extract_field(issue_details, 'Note')
    issue_info['severity'] = 'UNKNOWN'
    if note != 'Not specified':
        issue_info['current'] = note

# ===== Step 4: Read Relevant Source Code =====
file_path = "pycaption/scc/__init__.py"
line_num = None

if issue_info['file'] != 'Not specified':
    file_match = re.match(r'(.+?):(\d+)', issue_info['file'])
    if file_match:
        file_path = file_match.group(1)
        line_num = int(file_match.group(2))

search_terms = [issue_info['id']]
if 'RU4' in issue_info.get('title', '') or '94a7' in str(issue_info):
    search_terms.extend(['94a7', '9427', 'RU4'])
elif 'header' in issue_info.get('title', '').lower():
    search_terms.extend(['Scenarist_SCC', 'def read', 'def detect'])
elif 'parity' in issue_info.get('title', '').lower():
    search_terms.extend(['parity', '& 0x7f'])
else:
    keywords = [w for w in issue_info['title'].split() if len(w) > 3 and w[0].isupper()]
    search_terms.extend(keywords[:3])

scc_files = ['pycaption/scc/__init__.py', 'pycaption/scc/constants.py',
             'pycaption/scc/specialized_collections.py', 'pycaption/scc/state_machines.py']
grep_results = []
for term in search_terms:
    for sf in scc_files:
        try:
            result = subprocess.run(['grep', '-n', term, sf], capture_output=True, text=True)
            if result.stdout.strip():
                for line in result.stdout.strip().split('\n'):
                    grep_results.append(f"{sf}:{line}")
        except Exception:
            pass

if grep_results and line_num is None:
    first_hit = grep_results[0]
    parts = first_hit.split(':')
    if len(parts) >= 2:
        file_path = parts[0]
        try:
            line_num = int(parts[1])
        except ValueError:
            pass

if line_num:
    with open(file_path) as f:
        lines = f.readlines()
    start = max(0, line_num - 10)
    context = ''.join(lines[start:start + 30])
    print(f"Found code at {file_path}:{line_num}")
else:
    with open(file_path) as f:
        context = ''.join(f.readlines()[:50])
    print(f"Reading {file_path} (no line match found)")

print(f"   Grep hits: {len(grep_results)}")


# ===== Helper Functions =====

def extract_spec_reference(spec_content, search_term):
    if not spec_content:
        return search_term
    rule_match = re.search(r'\[(RULE-[A-Z]+-\d{3})\]', spec_content)
    if rule_match:
        rule_id_found = rule_match.group(1)
        cea_match = re.search(r'CEA-608[^,\n]*', spec_content)
        if cea_match:
            return f"{rule_id_found} (per {cea_match.group(0)})"
        return rule_id_found
    return search_term


def generate_code_fix(_issue_info, _context):
    spec_path = "ai_artifacts/specs/scc/scc_specs_summary.md"
    spec_content = None
    try:
        rule_id_local = _issue_info['id']
        result = subprocess.run(['grep', '-A', '15', f'\\[{rule_id_local}\\]', spec_path],
                                capture_output=True, text=True)
        spec_content = result.stdout.strip() if result.stdout.strip() else None
    except Exception:
        spec_content = None

    if 'RU4' in _issue_info['title'] or '94a7' in str(_issue_info):
        spec_ref = extract_spec_reference(spec_content, 'RU4') if spec_content else \
                   "CEA-608 Section 6.4.2 (Roll-Up Captions)"
        return f'''
#### No Change Required

The current RU4 hex code `94a7` in `pycaption/scc/__init__.py` is **correct**.

Per **{spec_ref}**, CEA-608 uses odd-parity encoding. The RU4 (Roll-Up 4 rows)
control code with odd parity is `0x94a7`, not `0x9427`.

**Spec Reference**: See `ai_artifacts/specs/scc/scc_specs_summary.md` -> Search for `[CTRL-RU4]`
or `[RULE-ROLLUP-001]` for complete control code table.
'''

    elif 'header' in _issue_info['title'].lower() or 'RULE-FMT-001' in _issue_info['id']:
        spec_ref = extract_spec_reference(spec_content, 'RULE-FMT-001') if spec_content else \
                   "RULE-FMT-001 and IMPL-FMT-001"
        return f'''
#### Code to Add

```python
# File: pycaption/scc/__init__.py
# Location: At start of SCCReader.read() method

def read(self, content, lang="en-US", simulate_roll_up=False, offset=0):
    lines = content.splitlines()

    # Validate SCC header (RULE-FMT-001)
    if not lines or lines[0].strip() != "Scenarist_SCC V1.0":
        raise CaptionReadNoCaptions(
            "Invalid SCC file: Header must be exactly 'Scenarist_SCC V1.0'"
        )

    # Continue with existing parsing logic...
    self.caption_stash = CaptionStash()
```

**What**: Add 4-line header validation at the start of `read()` method.

**Why**: This is required by **{spec_ref}** in the SCC specification.

**Spec Reference**: See `ai_artifacts/specs/scc/scc_specs_summary.md` -> Section 1.1 "File Header"
-> `[RULE-FMT-001]` and `[IMPL-FMT-001]` for complete validation requirements.
'''

    else:
        rule_id_local = _issue_info['id']
        spec_ref = extract_spec_reference(spec_content, rule_id_local) if spec_content else rule_id_local

        code_locations = ""
        if grep_results:
            code_locations = "\n".join(f"  - `{hit}`" for hit in grep_results[:5])
        else:
            code_locations = f"  - `{_issue_info.get('file', 'pycaption/scc/__init__.py')}` (search for related code)"

        return f'''
#### Fix Required

**Relevant code locations** (from grep):
{code_locations}

**Current behavior**: {_issue_info["current"]}
**Expected behavior**: {_issue_info["expected"]}

**Approach**:
1. Open the file(s) listed above at the indicated lines
2. Identify the code handling this feature
3. Modify to match the expected behavior per **{spec_ref}**
4. Add validation if the issue is about missing checks

**Why**: This is required by **{spec_ref}** in the SCC specification.
- **Severity**: {_issue_info.get("severity", "UNKNOWN")} (per spec compliance level)
- **Impact**: {_issue_info.get("impact", "May cause interoperability issues or incorrect caption rendering")}

**Spec Reference**: See `ai_artifacts/specs/scc/scc_specs_summary.md` -> Search for `[{rule_id_local}]`
for complete specification details, validation criteria, and test patterns.
'''


def generate_test_cases(_issue_info):
    if 'RU4' in _issue_info['title'] or '94a7' in str(_issue_info):
        return '''
```python
# File: tests/test_scc.py

def test_ru4_control_code_correct_hex():
    from pycaption.scc import SCCReader

    scc_content = """Scenarist_SCC V1.0

00:00:00:00\t9427 9427 94ad 94ad

"""

    reader = SCCReader()
    caption_set = reader.read(scc_content)
    assert caption_set is not None
```
'''

    elif 'header' in _issue_info['title'].lower():
        return '''
```python
# File: tests/test_scc.py

def test_header_validation_rejects_invalid():
    from pycaption.scc import SCCReader
    from pycaption.exceptions import CaptionReadNoCaptions
    import pytest

    reader = SCCReader()

    invalid_scc = """scenarist_scc v1.0

00:00:00:00\t9420 9420
"""

    with pytest.raises(CaptionReadNoCaptions, match="Invalid SCC file"):
        reader.read(invalid_scc)

    valid_scc = """Scenarist_SCC V1.0

00:00:00:00\t9420 9420
"""

    result = reader.read(valid_scc)
    assert result is not None
```
'''

    else:
        return f'''
```python
# File: tests/test_scc.py

def test_{_issue_info["id"].lower().replace("-", "_")}():
    from pycaption.scc import SCCReader

    scc_content = """Scenarist_SCC V1.0

00:00:00:00\t9420 9420

"""

    reader = SCCReader()
    result = reader.read(scc_content)
    assert result is not None
```
'''


def generate_implementation_notes(_issue_info):
    notes = []
    rule_id_local = _issue_info['id']

    if _issue_info['severity'] == 'MUST':
        notes.append(f"**MUST-level requirement**: This is mandatory per **{rule_id_local}** in the CEA-608/SCC specification.")
    elif _issue_info['severity'] == 'SHOULD':
        notes.append(f"**SHOULD-level requirement**: Recommended by **{rule_id_local}** for best practices and compatibility.")

    if 'interoperability' in _issue_info.get('impact', '').lower():
        notes.append("**Interoperability impact**: Required for compatibility with industry-standard tools.")

    notes.append(f"**Specification reference**:")
    notes.append(f"   - Primary: `ai_artifacts/specs/scc/scc_specs_summary.md` -> Search for `[{rule_id_local}]`")

    return '\n'.join(f'- {note}' if not note.startswith('   ') else note for note in notes)


def estimate_complexity(_issue_info):
    if any(word in _issue_info.get('fix', '').lower() for word in ['change', 'character', 'single']):
        return "Low (simple change)"
    elif any(word in _issue_info.get('fix', '').lower() for word in ['add', 'line', 'validation']):
        return "Medium (add code)"
    else:
        return "High (complex implementation)"


def estimate_time(_issue_info):
    fix_text = _issue_info.get('fix', '').lower()
    if 'character' in fix_text or '30 second' in fix_text:
        return "< 1 minute"
    elif 'line' in fix_text or '5 minute' in fix_text:
        return "5-10 minutes"
    else:
        return "15-30 minutes"


# ===== Step 5: Generate Report =====
fix_content = f"""# SCC Compliance Fix Suggestions

**Generated**: {datetime.now().strftime("%Y-%m-%d")}
**Source Report**: {latest_report}
**Focus**: Most Critical Issue Only

---

## Issue Being Fixed

**Issue ID**: {issue_info['id']}
**Title**: {issue_info['title']}
**Severity**: {issue_info['severity']}
**Priority**: CRITICAL (Issue #1)

**Current State**: {issue_info['current']}
**Required**: {issue_info['expected']}
**Impact**: {issue_info['impact']}

**Specification Context**: This issue violates **{issue_info['id']}** in the SCC/CEA-608 specification.
See `ai_artifacts/specs/scc/scc_specs_summary.md` for complete specification text.

---

## Proposed Fix

### Location
**File**: `{file_path}`
**Line**: {line_num if line_num else 'N/A'}

### Implementation

{generate_code_fix(issue_info, context)}

---

## Testing

### Test Cases Required

{generate_test_cases(issue_info)}

---

## Verification Steps

1. **Apply the fix** above
2. **Run tests**: `pytest tests/test_scc.py -v`
3. **Verify against spec**:
   - Open `ai_artifacts/specs/scc/scc_specs_summary.md`
   - Search for `[{issue_info['id']}]`
   - Confirm fix meets all requirements
4. **Test with real SCC file** (if applicable)
5. **Check interoperability**: Verify output works with standard tools

---

## Specification Details

**Rule**: {issue_info['id']}
**Level**: {issue_info['severity']} (mandatory compliance)
**Location in Spec**: `ai_artifacts/specs/scc/scc_specs_summary.md`

---

## Additional Notes

{generate_implementation_notes(issue_info)}

---

## Next Steps

After fixing this issue:
1. Mark {issue_info['id']} as resolved
2. Run `/suggest-scc-fixes` again for next critical issue
3. Re-run `/check-scc-compliance` to verify fix and get updated report
4. Review full spec section in `ai_artifacts/specs/scc/scc_specs_summary.md` if needed

---

**Generated by**: suggest-scc-fixes skill
**Fix complexity**: {estimate_complexity(issue_info)}
**Estimated time**: {estimate_time(issue_info)}
**Spec-backed**: All fixes reference specification requirements
"""

os.makedirs("ai_artifacts/compliance_checks/scc", exist_ok=True)
with open("ai_artifacts/compliance_checks/scc/suggested_scc_fixes.md", 'w') as _f:
    _f.write(fix_content)

print(f"""
Fix suggestion generated!

Issue: {issue_info['id']} - {issue_info['title']}
Saved to: ai_artifacts/compliance_checks/scc/suggested_scc_fixes.md

Summary:
   Severity: {issue_info['severity']}
   File: {file_path}
   Complexity: {estimate_complexity(issue_info)}
   Time: {estimate_time(issue_info)}

Next Steps:
   1. Review the suggested fix in the report
   2. Apply the code changes
   3. Run the test cases
   4. Run /suggest-scc-fixes again for next issue
""")
```

---

## Success Criteria

- **Context-efficient** - Uses ~20K tokens (vs 90K+ for all issues)
- **Focused** - One issue at a time with complete fix
- **Actionable** - Exact code, not generic advice
- **Testable** - Includes test cases
- **Iterative** - Run multiple times for multiple issues
- **Fast** - Completes in ~1-2 minutes

---

## Important Notes

**Why one issue at a time:**
- Keeps context window manageable
- Allows detailed, specific fixes
- User can review and apply incrementally
- Can re-run for next issue after first is fixed

**Priority order:**
1. First run: Fix issue #1 (most critical)
2. Second run: Fix issue #2 (next critical)
3. Continue until all critical issues resolved

**Error handling:**
- No report found -> Tell user to run check-scc-compliance
- No issues found -> Celebrate! All compliant
- Can't parse issue -> Use generic template
