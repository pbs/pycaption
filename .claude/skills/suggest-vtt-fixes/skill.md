---
name: suggest-vtt-fixes
description: Analyzes the latest WebVTT compliance report and generates detailed Python code suggestions for fixing the most critical issue.
---

# suggest-vtt-fixes

## What this skill does

Focused fix generation for WebVTT compliance issues:

1. **Finds** latest compliance report in `ai_artifacts/compliance_checks/vtt/`
2. **Identifies** the MOST CRITICAL issue (highest priority)
3. **Generates** detailed fix with:
   - Exact Python code to implement
   - File locations and line numbers
   - Test cases for the fix
   - Implementation notes with spec references
4. **Saves** to `ai_artifacts/compliance_checks/vtt/suggested_vtt_fixes.md`

**Key optimization**: Focuses on ONE critical issue at a time to avoid context overflow.

## Usage

```bash
/suggest-vtt-fixes
```

Automatically finds latest report and generates fix for top priority issue.

---

## Pre-flight: Read `.claude/skills/gotchas.md`

**REQUIRED** before generating fix suggestions. Pay special attention to gotchas #1 (no proprietary data tables in suggested code) and #3 (W3C license attribution).

**Post-run:** If you discover a new gotcha during fix generation (a regex pattern that silently misses IDs, a code pattern that looks correct but violates the spec, or a compliance report format change that breaks extraction), append it to `.claude/skills/gotchas.md` with the same numbered format.

---

## Implementation

### Run this script

```python
import re
import os
import glob
import subprocess
from datetime import datetime

# ===== Step 1: Find latest report =====
reports = glob.glob("ai_artifacts/compliance_checks/vtt/compliance_report_*.md")
if not reports:
    print("No compliance report found. Run /check-vtt-compliance first.")
    exit(0)

latest_report = max(reports, key=os.path.getmtime)
print(f"Using: {latest_report}")

# ===== Step 2: Extract Critical Issue =====
with open(latest_report) as _f:
    report_content = _f.read()

missing_section = re.search(r'## 3\. Missing MUST Rules.*?\n(.*?)(?=\n## |\Z)',
                            report_content, re.DOTALL)

issue_id = None
issue_title = None
issue_type = None

if missing_section:
    missing_text = missing_section.group(1)
    first_match = re.search(r'1\.\s+\*\*\[(RULE-[A-Z]+-\d{3})\]\*\*:\s+(.+?)(?:\n|$)',
                           missing_text)

    if first_match:
        issue_id = first_match.group(1)
        issue_title = first_match.group(2).strip()
        issue_type = 'MISSING_MUST'
        print(f"Focus: {issue_id} - {issue_title}")

if not issue_id:
    val_section = re.search(r'## 1\. Validation Gaps.*?\n(.*?)(?=\n## |\Z)',
                           report_content, re.DOTALL)
    if val_section and '1.' in val_section.group(1):
        val_match = re.search(r'1\.\s+\*\*\[(RULE-[A-Z]+-\d{3})\]\*\*:\s+(.+?)(?:\n|$)',
                             val_section.group(1))
        if val_match:
            issue_id = val_match.group(1)
            issue_title = val_match.group(2).strip()
            issue_type = 'VALIDATION_GAP'

if not issue_id:
    print("No critical issues found!")
    exit(0)

# ===== Step 3: Load Spec Details =====
spec_path = "ai_artifacts/specs/vtt/vtt_specs_summary.md"
spec_section = None

try:
    result = subprocess.run(['grep', '-A', '20', f'\\[{issue_id}\\]', spec_path],
                           capture_output=True, text=True)
    spec_section = result.stdout.strip() if result.stdout.strip() else None
except Exception:
    pass


def extract_spec_info(spec_text, _issue_id):
    info = {'id': _issue_id, 'title': issue_title, 'type': issue_type}

    req_match = re.search(r'\*\*Requirement:\*\*\s+(.+?)(?=\n\*\*|\n\n)',
                         spec_text, re.DOTALL)
    if req_match:
        info['requirement'] = req_match.group(1).strip()

    level_match = re.search(r'\*\*Level:\*\*\s+(MUST|SHOULD|MAY)', spec_text)
    if level_match:
        info['severity'] = level_match.group(1)
    else:
        info['severity'] = 'UNKNOWN'

    val_match = re.search(r'\*\*Validation:\*\*\s+(.+?)(?=\n\*\*|\n\n)',
                         spec_text, re.DOTALL)
    if val_match:
        info['validation'] = val_match.group(1).strip()

    return info


issue_info = extract_spec_info(spec_section, issue_id) if spec_section else {
    'id': issue_id, 'title': issue_title, 'type': issue_type, 'severity': 'UNKNOWN'
}

# ===== Step 4: Read Relevant Code =====
file_path = 'pycaption/webvtt.py'
line_num = None

search_terms = []
if 'TIME' in issue_id or 'timestamp' in issue_title.lower():
    search_terms = ['TIMESTAMP_PATTERN', '_parse_timestamp', '_validate_timings', 'ignore_timing_errors']
elif 'TAG' in issue_id or 'tag' in issue_title.lower():
    search_terms = ['OTHER_SPAN_PATTERN', 'VOICE_SPAN_PATTERN', '_convert_style_to_text_tag']
elif 'SET' in issue_id or 'setting' in issue_title.lower():
    search_terms = ['webvtt_positioning', 'left_offset', 'top_offset', 'cue_width', 'alignment']
elif 'REG' in issue_id or 'region' in issue_title.lower():
    search_terms = ['REGION', 'region']
elif 'ENT' in issue_id or 'entit' in issue_title.lower():
    search_terms = ['_decode', '_encode_illegal_characters', 'replace.*&']
elif 'WRITE' in issue_id or 'write' in issue_title.lower():
    search_terms = ['class WebVTTWriter', '_timestamp', '_encode_illegal_characters']
else:
    keywords = [w for w in issue_title.split() if len(w) > 3]
    search_terms = keywords[:3] if keywords else [issue_id]

grep_results = []
for term in search_terms:
    try:
        result = subprocess.run(['grep', '-n', term, file_path], capture_output=True, text=True)
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                grep_results.append(f"{file_path}:{line}")
    except Exception:
        pass

if 'SET' in issue_id or 'position' in issue_title.lower():
    try:
        result = subprocess.run(['grep', '-En', 'left_offset|top_offset|cue_width', 'pycaption/geometry.py'],
                               capture_output=True, text=True)
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                grep_results.append(f"pycaption/geometry.py:{line}")
    except Exception:
        pass

if grep_results:
    parts = grep_results[0].split(':')
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
    print(f"Reading {file_path} (no line match)")

already_implemented = False
if grep_results:
    for hit in grep_results:
        if any(term in hit for term in ['_validate_timings', '_decode', 'CaptionReadSyntaxError']):
            already_implemented = True
            break

if already_implemented:
    print(f"NOTE: Related code found — verify feature is not already implemented before applying fix")

print(f"Grep hits: {len(grep_results)}")


# ===== Helper Functions =====

def extract_spec_reference(spec_content, _issue_id):
    if not spec_content:
        return _issue_id
    sources_match = re.search(r'\*\*Sources:\*\*\s+(.+?)(?=\n\*\*|\n\n)',
                             spec_content, re.DOTALL)
    if sources_match:
        sources = sources_match.group(1).strip()
        if 'W3C' in sources:
            return f"{_issue_id} (per W3C WebVTT Specification)"
    return _issue_id


def generate_timestamp_format_fix(_issue_info, spec_ref):
    return f'''
#### Implementation Required

```python
# File: pycaption/webvtt.py
# Location: In timestamp validation section

import re

def validate_timestamp_format(timestamp_str):
    """
    Validate WebVTT timestamp format: [HH:]MM:SS.mmm

    :param timestamp_str: Timestamp string to validate
    :raises: ValueError if format invalid
    """
    pattern = r'^(?:(\\d{{2,}}):)?(\\d{{2}}):(\\d{{2}})\\.(\\d{{3}})$'

    match = re.match(pattern, timestamp_str)
    if not match:
        raise ValueError(
            f"Invalid timestamp format '{{timestamp_str}}'. "
            f"Expected [HH:]MM:SS.mmm format."
        )

    hours, minutes, seconds, milliseconds = match.groups()
    hours = int(hours) if hours else 0
    minutes = int(minutes)
    seconds = int(seconds)

    if minutes > 59:
        raise ValueError(f"Minutes must be 0-59, got {{minutes}}")
    if seconds > 59:
        raise ValueError(f"Seconds must be 0-59, got {{seconds}}")

    return hours, minutes, seconds, int(milliseconds)
```

**What**: Add timestamp format validation to WebVTT parser

**Why**: According to **{spec_ref}**, WebVTT timestamps MUST follow the format
`[HH:]MM:SS.mmm` where:
- Hours are optional (but required if >= 1 hour)
- Minutes/seconds must be exactly 2 digits (0-59)
- Milliseconds must be exactly 3 digits (000-999)

**Spec Reference**: See `ai_artifacts/specs/vtt/vtt_specs_summary.md` ->
Section "Part 2: Timestamps" -> `[RULE-TIME-001]`, `[RULE-TIME-003]`, `[RULE-TIME-004]`
'''


def generate_time_validation_fix(_issue_info, spec_ref):
    return f'''
#### Validation Logic Required

```python
# File: pycaption/webvtt.py

def parse_cue_timing(timing_line):
    parts = timing_line.split('-->')
    if len(parts) != 2:
        raise ValueError(f"Invalid timing line: {{timing_line}}")

    start_str = parts[0].strip()
    end_str = parts[1].strip()

    start_time = parse_timestamp(start_str)
    end_time = parse_timestamp(end_str)

    if start_time > end_time:
        raise ValueError(
            f"Start time ({{start_str}}) must be <= end time ({{end_str}})"
        )

    return start_time, end_time
```

**What**: Add start <= end time validation

**Why**: According to **{spec_ref}**, cue start time MUST be less than or equal
to end time. This is required by the W3C WebVTT specification Section 4.

**Spec Reference**: `ai_artifacts/specs/vtt/vtt_specs_summary.md` -> `[RULE-TIME-005]`
'''


def generate_tag_support_fix(_issue_info, spec_ref):
    return f'''
#### Tag Support Implementation

```python
# File: pycaption/webvtt.py

def parse_voice_tag(content):
    import re
    pattern = r'<v\\s+([^>]+)>(.*?)</v>'

    def replace_voice(match):
        speaker = match.group(1).strip()
        text = match.group(2)
        return f'{{VOICE:{{speaker}}}}{{text}}{{/VOICE}}'

    return re.sub(pattern, replace_voice, content, flags=re.DOTALL)
```

**What**: Add support for `<v>` voice tags

**Why**: According to **{spec_ref}**, WebVTT supports `<v annotation>text</v>`
tags to indicate speaker/voice.

**Spec Reference**: `ai_artifacts/specs/vtt/vtt_specs_summary.md` ->
Part 5 "Tags & Markup" -> `[RULE-TAG-005]`
'''


def generate_region_fix(_issue_info, spec_ref):
    return f'''
#### Region Block Parsing

```python
# File: pycaption/webvtt.py

def parse_region_block(self, lines):
    region_settings = {{}}

    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            region_settings[key] = value

    if 'id' not in region_settings:
        raise ValueError("REGION block must have 'id' setting")

    return region_settings
```

**What**: Add REGION block parsing support

**Why**: According to **{spec_ref}**, WebVTT REGION blocks define rendering regions
for cues.

**Spec Reference**: `ai_artifacts/specs/vtt/vtt_specs_summary.md` ->
Part 7 "Regions" -> `[RULE-REG-001]` through `[RULE-REG-009]`
'''


def generate_entity_fix(_issue_info, spec_ref):
    return f'''
#### HTML Entity Handling

```python
# File: pycaption/webvtt.py

def decode_html_entities(text):
    import html
    decoded = html.unescape(text)
    return decoded
```

**What**: Add HTML entity decoding

**Why**: According to **{spec_ref}**, WebVTT cue text MUST support HTML entities
for special characters: `&amp;`, `&lt;`, `&gt;`, `&nbsp;`, `&lrm;`, `&rlm;`

**Spec Reference**: `ai_artifacts/specs/vtt/vtt_specs_summary.md` ->
Part 7.5 "HTML Entities" -> `[RULE-ENT-001]` through `[RULE-ENT-007]`
'''


def generate_generic_fix(_issue_info, spec_ref, _grep_results=None, _already_implemented=False):
    code_locations = ""
    if _grep_results:
        code_locations = "\n".join(f"  - `{hit}`" for hit in _grep_results[:5])
    else:
        code_locations = f"  - `pycaption/webvtt.py` (search for related code)"

    already_note = ""
    if _already_implemented:
        already_note = """
**WARNING**: Related code already exists in the source. Before implementing, verify
this feature is not already handled. The grep results above may show existing code."""

    return f'''
#### Fix Required

**Relevant code locations** (from grep):
{code_locations}
{already_note}

**Current behavior**: {_issue_info.get('requirement', 'See compliance report')}
**Required**: Per **{spec_ref}**, this is a {_issue_info['severity']}-level requirement.

**Approach**:
1. Open the file(s) listed above at the indicated lines
2. Identify the code handling this feature (or confirm it is missing)
3. Implement or modify to match the expected behavior per **{spec_ref}**
4. Add validation and error handling per the spec

**Spec Reference**: See `ai_artifacts/specs/vtt/vtt_specs_summary.md` ->
Search for `[{_issue_info["id"]}]` for complete requirements, validation criteria, and test patterns.
'''


def generate_vtt_fix(_issue_info, _spec_section):
    _spec_ref = extract_spec_reference(_spec_section, _issue_info['id'])

    if 'RULE-TIME-001' in _issue_info['id']:
        return generate_timestamp_format_fix(_issue_info, _spec_ref)
    elif 'RULE-TIME-005' in _issue_info['id']:
        return generate_time_validation_fix(_issue_info, _spec_ref)
    elif 'RULE-TAG' in _issue_info['id']:
        return generate_tag_support_fix(_issue_info, _spec_ref)
    elif 'RULE-REG' in _issue_info['id']:
        return generate_region_fix(_issue_info, _spec_ref)
    elif 'RULE-ENT' in _issue_info['id']:
        return generate_entity_fix(_issue_info, _spec_ref)
    else:
        return generate_generic_fix(_issue_info, _spec_ref, grep_results, already_implemented)


def generate_vtt_tests(_issue_info):
    _issue_id = _issue_info['id']

    if 'TIME' in _issue_id:
        return '''
```python
# File: tests/test_webvtt.py

def test_timestamp_validation():
    from pycaption.webvtt import WebVTTReader

    valid_vtt = """WEBVTT

00:01.000 --> 00:05.000
Valid cue

01:30:45.123 --> 01:30:50.456
Valid with hours
"""

    reader = WebVTTReader()
    result = reader.read(valid_vtt)
    assert result is not None


def test_timestamp_invalid_format():
    from pycaption.webvtt import WebVTTReader
    from pycaption.exceptions import CaptionReadSyntaxError
    import pytest

    invalid_vtt = """WEBVTT

00:01.00 --> 00:05.000
Missing millisecond digit
"""

    reader = WebVTTReader()
    with pytest.raises(CaptionReadSyntaxError):
        reader.read(invalid_vtt)
```
'''

    elif 'TAG' in _issue_id:
        return '''
```python
# File: tests/test_webvtt.py

def test_voice_tag_parsing():
    from pycaption.webvtt import WebVTTReader

    vtt_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
<v John>Hello!</v>

00:00:06.000 --> 00:00:10.000
<v Mary>Hi there!</v>
"""

    reader = WebVTTReader()
    caption_set = reader.read(vtt_content)
    captions = caption_set.get_captions('en')

    assert len(captions) == 2
```
'''

    else:
        return f'''
```python
# File: tests/test_webvtt.py

def test_{_issue_id.lower().replace("-", "_")}():
    from pycaption.webvtt import WebVTTReader

    vtt_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Test content
"""

    reader = WebVTTReader()
    result = reader.read(vtt_content)

    assert result is not None
```
'''


# ===== Step 5: Generate and Write Report =====
report = f"""# WebVTT Compliance Fix Suggestions

**Generated**: {datetime.now().strftime("%Y-%m-%d")}
**Source Report**: {latest_report}
**Focus**: Most Critical Issue Only

---

## Issue Being Fixed

**Issue ID**: {issue_info['id']}
**Title**: {issue_info['title']}
**Severity**: {issue_info['severity']}
**Priority**: CRITICAL (Issue #1)
**Type**: {issue_info['type']}

**Specification Context**: This issue violates **{issue_info['id']}** in the WebVTT specification.
See `ai_artifacts/specs/vtt/vtt_specs_summary.md` for complete specification text and validation criteria.

---

## Proposed Fix

{generate_vtt_fix(issue_info, spec_section)}

---

## Testing

### Test Cases Required

{generate_vtt_tests(issue_info)}

---

## Verification Steps

1. **Apply the fix** above
2. **Run tests**: `pytest tests/test_webvtt.py -v`
3. **Verify against spec**:
   - Open `ai_artifacts/specs/vtt/vtt_specs_summary.md`
   - Search for `[{issue_info['id']}]`
   - Confirm fix meets all requirements
4. **Test with real VTT file**
5. **Browser compatibility**: Test in Chrome/Firefox if possible

---

## Specification Details

**Rule**: {issue_info['id']}
**Level**: {issue_info['severity']} (mandatory compliance)
**Source**: W3C WebVTT Specification
**Location in Spec**: `ai_artifacts/specs/vtt/vtt_specs_summary.md`

---

## Next Steps

After fixing this issue:
1. Mark {issue_info['id']} as resolved
2. Run `/suggest-vtt-fixes` again for next issue
3. Re-run `/check-vtt-compliance` to verify
4. Review full spec section if needed

---

**Generated by**: suggest-vtt-fixes skill
**Spec-backed**: All fixes reference W3C WebVTT specification
"""

os.makedirs("ai_artifacts/compliance_checks/vtt", exist_ok=True)
with open("ai_artifacts/compliance_checks/vtt/suggested_vtt_fixes.md", 'w') as _f:
    _f.write(report)

print(f"""
Fix suggestion generated!

Issue: {issue_info['id']} - {issue_info['title']}
Saved to: ai_artifacts/compliance_checks/vtt/suggested_vtt_fixes.md

Next Steps:
   1. Review the suggested fix
   2. Apply the code changes
   3. Run the test cases
   4. Run /suggest-vtt-fixes again for next issue
""")
```

---

## Success Criteria

- **Context-efficient** - Focuses on one issue
- **Actionable** - Exact code with examples
- **Spec-backed** - All fixes reference W3C spec
- **Testable** - Includes test cases
- **Educational** - Explains why fixes needed
