---
name: suggest-vtt-fixes
description: Analyzes the latest WebVTT compliance report and generates detailed Python code suggestions for fixing the most critical issue.
---

# suggest-vtt-fixes

## What this skill does

Focused fix generation for WebVTT compliance issues:

1. **Finds** latest compliance report in `pycaption/compliance_checks/vtt/`
2. **Identifies** the MOST CRITICAL issue (highest priority)
3. **Generates** detailed fix with:
   - Exact Python code to implement
   - File locations and line numbers
   - Test cases for the fix
   - Implementation notes with spec references
4. **Saves** to `pycaption/compliance_checks/vtt/suggested_vtt_fixes.md`

**Key optimization**: Focuses on ONE critical issue at a time to avoid context overflow.

## Usage

```bash
/suggest-vtt-fixes
```

Automatically finds latest report and generates fix for top priority issue.

---

## Implementation

### Step 1: Find Latest Compliance Report

```bash
LATEST_REPORT=$(ls -t pycaption/compliance_checks/vtt/compliance_report_*.md 2>/dev/null | head -1)

if [ -z "$LATEST_REPORT" ]; then
    echo "❌ No compliance report found"
    echo "   Run /check-vtt-compliance first"
    exit 1
fi

echo "📄 Using report: $LATEST_REPORT"
```

---

### Step 2: Extract Critical Issue List

```python
import re
import os
from datetime import datetime

# Find latest report
reports = glob.glob("pycaption/compliance_checks/vtt/compliance_report_*.md")
if not reports:
    print("❌ No compliance report found. Run /check-vtt-compliance first.")
    exit(0)

latest_report = max(reports, key=os.path.getmtime)
print(f"📄 Using: {latest_report}")

# Read report sections
report_content = read(latest_report)

# Extract missing MUST rules (highest priority)
missing_section = re.search(r'## 3\. Missing MUST Rules.*?\n(.*?)(?=\n## |\Z)', 
                            report_content, re.DOTALL)

if missing_section:
    missing_text = missing_section.group(1)
    # Parse first missing rule
    first_match = re.search(r'1\.\s+\*\*\[(RULE-[A-Z]+-\d{3})\]\*\*:\s+(.+?)(?:\n|$)', 
                           missing_text)
    
    if first_match:
        issue_id = first_match.group(1)
        issue_title = first_match.group(2).strip()
        issue_type = 'MISSING_MUST'
        print(f"🎯 Focus: {issue_id} - {issue_title}")
    else:
        # Try validation gaps
        val_section = re.search(r'## 1\. Validation Gaps.*?\n(.*?)(?=\n## |\Z)', 
                               report_content, re.DOTALL)
        if val_section and '1.' in val_section.group(1):
            # Parse validation gap
            val_match = re.search(r'1\.\s+\*\*\[(RULE-[A-Z]+-\d{3})\]\*\*:\s+(.+?)(?:\n|$)', 
                                 val_section.group(1))
            if val_match:
                issue_id = val_match.group(1)
                issue_title = val_match.group(2).strip()
                issue_type = 'VALIDATION_GAP'
            else:
                print("✅ No critical issues found!")
                exit(0)
        else:
            print("✅ No critical issues found!")
            exit(0)
else:
    print("✅ No critical issues found!")
    exit(0)
```

---

### Step 3: Load Spec Details

```python
# Load VTT spec for this rule
spec_path = "pycaption/specs/vtt/vtt_specs_summary.md"
spec_section = grep(f"\\[{issue_id}\\]", path=spec_path, 
                   output_mode="content", context=20)

# Extract key info from spec
def extract_spec_info(spec_text, issue_id):
    info = {'id': issue_id, 'title': issue_title, 'type': issue_type}
    
    # Extract requirement
    req_match = re.search(r'\*\*Requirement:\*\*\s+(.+?)(?=\n\*\*|\n\n)', 
                         spec_text, re.DOTALL)
    if req_match:
        info['requirement'] = req_match.group(1).strip()
    
    # Extract level
    level_match = re.search(r'\*\*Level:\*\*\s+(MUST|SHOULD|MAY)', spec_text)
    if level_match:
        info['severity'] = level_match.group(1)
    else:
        info['severity'] = 'MUST'
    
    # Extract validation
    val_match = re.search(r'\*\*Validation:\*\*\s+(.+?)(?=\n\*\*|\n\n)', 
                         spec_text, re.DOTALL)
    if val_match:
        info['validation'] = val_match.group(1).strip()
    
    return info

issue_info = extract_spec_info(spec_section, issue_id)
```

---

### Step 4: Read Relevant Code

```python
# Identify target file
if 'TIME' in issue_id or 'timestamp' in issue_title.lower():
    file_path = 'pycaption/webvtt.py'
    search_term = 'timestamp'
elif 'TAG' in issue_id or 'tag' in issue_title.lower():
    file_path = 'pycaption/webvtt.py'
    search_term = 'tag'
elif 'REG' in issue_id or 'region' in issue_title.lower():
    file_path = 'pycaption/webvtt.py'
    search_term = 'region'
elif 'ENT' in issue_id or 'entit' in issue_title.lower():
    file_path = 'pycaption/webvtt.py'
    search_term = 'escape|entity'
else:
    file_path = 'pycaption/webvtt.py'
    search_term = issue_title.split()[0].lower()

# Search for existing implementation
existing = grep(search_term, path=file_path, output_mode="content", 
               context=5, head_limit=50)
```

---

### Step 5: Generate Fix

```python
def generate_vtt_fix(issue_info, spec_section):
    """Generate VTT-specific fix with spec references"""
    
    issue_id = issue_info['id']
    
    # Extract spec reference
    spec_ref = extract_spec_reference(spec_section, issue_id)
    
    # Generate fix based on issue type
    if 'RULE-TIME-001' in issue_id:
        return generate_timestamp_format_fix(issue_info, spec_ref)
    elif 'RULE-TIME-005' in issue_id:
        return generate_time_validation_fix(issue_info, spec_ref)
    elif 'RULE-TAG' in issue_id:
        return generate_tag_support_fix(issue_info, spec_ref)
    elif 'RULE-REG' in issue_id:
        return generate_region_fix(issue_info, spec_ref)
    elif 'RULE-ENT' in issue_id:
        return generate_entity_fix(issue_info, spec_ref)
    else:
        return generate_generic_fix(issue_info, spec_ref)


def generate_timestamp_format_fix(issue_info, spec_ref):
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
    # Pattern: optional hours, required MM:SS.mmm
    pattern = r'^(?:(\d{{2,}}):)?(\d{{2}}):(\d{{2}})\.(\d{{3}})$'
    
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
    
    # Validate ranges (RULE-TIME-004)
    if minutes > 59:
        raise ValueError(f"Minutes must be 0-59, got {{minutes}}")
    if seconds > 59:
        raise ValueError(f"Seconds must be 0-59, got {{seconds}}")
    
    return hours, minutes, seconds, int(milliseconds)
```

**What**: Add timestamp format validation to WebVTT parser

**Why**: According to **{spec_ref}**, WebVTT timestamps MUST follow the format 
`[HH:]MM:SS.mmm` where:
- Hours are optional (but required if ≥ 1 hour)
- Minutes/seconds must be exactly 2 digits (0-59)
- Milliseconds must be exactly 3 digits (000-999)

This is a **MUST-level requirement** from the W3C WebVTT specification.

**Impact**: Without validation:
- Parser accepts malformed timestamps
- Files fail on compliant players (browsers, media players)
- Interoperability issues with other WebVTT tools

**Spec Reference**: See `pycaption/specs/vtt/vtt_specs_summary.md` → 
Section "Part 2: Timestamps" → `[RULE-TIME-001]`, `[RULE-TIME-003]`, `[RULE-TIME-004]`
'''


def generate_time_validation_fix(issue_info, spec_ref):
    return f'''
#### Validation Logic Required

```python
# File: pycaption/webvtt.py
# Location: In cue parsing method

def parse_cue_timing(timing_line):
    """
    Parse and validate cue timing line.
    
    :param timing_line: String like "00:01.000 --> 00:05.000"
    :raises: ValueError if times invalid
    """
    parts = timing_line.split('-->')
    if len(parts) != 2:
        raise ValueError(f"Invalid timing line: {{timing_line}}")
    
    start_str = parts[0].strip()
    end_str = parts[1].strip()
    
    # Parse timestamps
    start_time = parse_timestamp(start_str)
    end_time = parse_timestamp(end_str)
    
    # RULE-TIME-005: Start must be ≤ end
    if start_time > end_time:
        raise ValueError(
            f"Start time ({{start_str}}) must be ≤ end time ({{end_str}})"
        )
    
    return start_time, end_time
```

**What**: Add start ≤ end time validation

**Why**: According to **{spec_ref}**, cue start time MUST be less than or equal 
to end time. This is required by the W3C WebVTT specification Section 4.

**Impact**: Without this validation:
- Nonsensical cues (end before start) accepted
- Undefined behavior in players
- May crash or skip cues

**Spec Reference**: `pycaption/specs/vtt/vtt_specs_summary.md` → `[RULE-TIME-005]`
'''


def generate_tag_support_fix(issue_info, spec_ref):
    tag_name = issue_info['title'].split()[0] if '<' in issue_info['title'] else 'voice'
    
    return f'''
#### Tag Support Implementation

```python
# File: pycaption/webvtt.py
# Location: In tag parsing section

def parse_voice_tag(content):
    """
    Parse <v Speaker> voice tags.
    
    Example: <v John>Hello!</v>
    """
    import re
    
    # Pattern: <v annotation>text</v>
    pattern = r'<v\s+([^>]+)>(.*?)</v>'
    
    def replace_voice(match):
        speaker = match.group(1).strip()
        text = match.group(2)
        # Convert to internal representation
        return f'{{VOICE:{speaker}}}{{text}}{{/VOICE}}'
    
    return re.sub(pattern, replace_voice, content, flags=re.DOTALL)
```

**What**: Add support for `<v>` voice tags

**Why**: According to **{spec_ref}**, WebVTT supports `<v annotation>text</v>` 
tags to indicate speaker/voice. This is part of the core WebVTT cue text syntax 
defined in the W3C specification.

**Impact**: Without voice tag support:
- Speaker information lost
- Multi-speaker dialogues unclear
- Accessibility reduced (screen readers can't announce speakers)

**Spec Reference**: `pycaption/specs/vtt/vtt_specs_summary.md` → 
Part 5 "Tags & Markup" → `[RULE-TAG-005]`
'''


def generate_region_fix(issue_info, spec_ref):
    return f'''
#### Region Block Parsing

```python
# File: pycaption/webvtt.py
# Location: Add to parser class

def parse_region_block(self, lines):
    """
    Parse REGION block.
    
    Format:
    REGION
    id:region_identifier
    width:50%
    lines:3
    regionanchor:0%,100%
    viewportanchor:10%,90%
    scroll:up
    """
    region_settings = {{}}
    
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            region_settings[key] = value
    
    # Validate required: id
    if 'id' not in region_settings:
        raise ValueError("REGION block must have 'id' setting")
    
    return region_settings
```

**What**: Add REGION block parsing support

**Why**: According to **{spec_ref}**, WebVTT REGION blocks define rendering regions 
for cues. This is an optional but important feature for positioning and styling.

Required settings per W3C spec:
- `id`: Required, unique identifier
- `width`, `lines`, `regionanchor`, `viewportanchor`, `scroll`: Optional

**Impact**: Without REGION support:
- Cannot handle cues with region references
- Positioning information lost
- Advanced layout features unavailable

**Spec Reference**: `pycaption/specs/vtt/vtt_specs_summary.md` → 
Part 7 "Regions" → `[RULE-REG-001]` through `[RULE-REG-009]`
'''


def generate_entity_fix(issue_info, spec_ref):
    return f'''
#### HTML Entity Handling

```python
# File: pycaption/webvtt.py
# Location: In text processing section

def decode_html_entities(text):
    """
    Decode HTML entities in WebVTT cue text.
    
    Required entities:
    - &amp; → &
    - &lt; → <
    - &gt; → >
    - &nbsp; → non-breaking space
    - &lrm; → left-to-right mark
    - &rlm; → right-to-left mark
    """
    import html
    
    # Use standard HTML entity decoder
    decoded = html.unescape(text)
    
    return decoded
```

**What**: Add HTML entity decoding

**Why**: According to **{spec_ref}**, WebVTT cue text MUST support HTML entities 
for special characters. The W3C spec requires handling of:
- `&amp;`, `&lt;`, `&gt;` (required for escaping)
- `&nbsp;` (non-breaking space)
- `&lrm;`, `&rlm;` (bidirectional text marks)

**Impact**: Without entity support:
- Special characters display incorrectly
- Cannot escape `<`, `>`, `&` in text
- Bidirectional text broken

**Spec Reference**: `pycaption/specs/vtt/vtt_specs_summary.md` → 
Part 7.5 "HTML Entities" → `[RULE-ENT-001]` through `[RULE-ENT-007]`
'''


def generate_generic_fix(issue_info, spec_ref):
    return f'''
#### Implementation Template

```python
# File: pycaption/webvtt.py

# TODO: Implement {issue_info['title']}
# 
# Requirement: {issue_info.get('requirement', 'See spec')}
# Validation: {issue_info.get('validation', 'See spec')}
```

**What**: Fix for {issue_info['title']}

**Why**: According to **{spec_ref}**, this is a {issue_info['severity']}-level 
requirement in the WebVTT specification.

**Spec Reference**: See `pycaption/specs/vtt/vtt_specs_summary.md` → 
Search for `[{issue_info['id']}]` for complete requirements.
'''


def extract_spec_reference(spec_content, issue_id):
    """Extract spec reference from content"""
    if not spec_content:
        return issue_id
    
    import re
    
    # Look for Sources section
    sources_match = re.search(r'\*\*Sources:\*\*\s+(.+?)(?=\n\*\*|\n\n)', 
                             spec_content, re.DOTALL)
    if sources_match:
        sources = sources_match.group(1).strip()
        if 'W3C' in sources:
            return f"{issue_id} (per W3C WebVTT Specification)"
    
    return issue_id
```

---

### Step 6: Generate Test Cases

```python
def generate_vtt_tests(issue_info):
    """Generate test cases for VTT fix"""
    
    issue_id = issue_info['id']
    
    if 'TIME' in issue_id:
        return '''
```python
# File: tests/test_webvtt.py

def test_timestamp_validation():
    """Test timestamp format validation"""
    from pycaption.webvtt import WebVTTReader
    
    # Valid timestamps
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
    """Test rejection of invalid timestamps"""
    from pycaption.webvtt import WebVTTReader
    from pycaption.exceptions import CaptionReadError
    import pytest
    
    # Invalid: wrong milliseconds
    invalid_vtt = """WEBVTT

00:01.00 --> 00:05.000
Missing millisecond digit
"""
    
    reader = WebVTTReader()
    with pytest.raises(CaptionReadError):
        reader.read(invalid_vtt)
```
'''
    
    elif 'TAG' in issue_id:
        return '''
```python
# File: tests/test_webvtt.py

def test_voice_tag_parsing():
    """Test <v> voice tag support"""
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
    # Verify speaker information preserved
```
'''
    
    else:
        return f'''
```python
# File: tests/test_webvtt.py

def test_{issue_id.lower().replace("-", "_")}():
    """Test fix for {issue_id}"""
    from pycaption.webvtt import WebVTTReader
    
    vtt_content = """WEBVTT

00:00:01.000 --> 00:00:05.000
Test content
"""
    
    reader = WebVTTReader()
    result = reader.read(vtt_content)
    
    # TODO: Add specific assertions for {issue_id}
    assert result is not None
```
'''
```

---

### Step 7: Write Report

```python
from datetime import datetime

report = f"""# WebVTT Compliance Fix Suggestions

**Generated**: {datetime.now().strftime("%Y-%m-%d")}
**Source Report**: {latest_report}
**Focus**: Most Critical Issue Only

---

## Issue Being Fixed

**Issue ID**: {issue_info['id']}  
**Title**: {issue_info['title']}  
**Severity**: {issue_info['severity']}  
**Priority**: 🔴 CRITICAL (Issue #1)
**Type**: {issue_info['type']}

**Specification Context**: This issue violates **{issue_info['id']}** in the WebVTT specification.
See `pycaption/specs/vtt/vtt_specs_summary.md` for complete specification text and validation criteria.

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
   - Open `pycaption/specs/vtt/vtt_specs_summary.md`
   - Search for `[{issue_info['id']}]`
   - Confirm fix meets all requirements
4. **Test with real VTT file**
5. **Browser compatibility**: Test in Chrome/Firefox if possible

---

## Specification Details

**Rule**: {issue_info['id']}
**Level**: {issue_info['severity']} (mandatory compliance)
**Source**: W3C WebVTT Specification
**Location in Spec**: `pycaption/specs/vtt/vtt_specs_summary.md`

---

## Next Steps

After fixing this issue:
1. ✅ Mark {issue_info['id']} as resolved
2. 🔄 Run `/suggest-vtt-fixes` again for next issue
3. 📊 Re-run `/check-vtt-compliance` to verify
4. 📖 Review full spec section if needed

---

**Generated by**: suggest-vtt-fixes skill  
**Spec-backed**: ✅ All fixes reference W3C WebVTT specification
"""

# Save report
os.makedirs("pycaption/compliance_checks/vtt", exist_ok=True)
write("pycaption/compliance_checks/vtt/suggested_vtt_fixes.md", report)

print(f"""
✅ Fix suggestion generated!

🎯 Issue Fixed: {issue_info['id']} - {issue_info['title']}
📄 Saved to: pycaption/compliance_checks/vtt/suggested_vtt_fixes.md

💡 Next Steps:
   1. Review the suggested fix
   2. Apply the code changes
   3. Run the test cases
   4. Run /suggest-vtt-fixes again for next issue

""")
```

---

## Success Criteria

✅ **Context-efficient** - Focuses on one issue  
✅ **Actionable** - Exact code with examples  
✅ **Spec-backed** - All fixes reference W3C spec  
✅ **Testable** - Includes test cases  
✅ **Educational** - Explains why fixes needed
