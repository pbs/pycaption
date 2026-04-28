---
name: suggest-dfxp-fixes
description: Analyzes the latest DFXP/TTML compliance report and generates detailed Python code suggestions for fixing the most critical issue.
---

# suggest-dfxp-fixes

## What this skill does

Focused fix generation for DFXP/TTML compliance issues:

1. **Finds** latest compliance report in `ai_artifacts/compliance_checks/dfxp/`
2. **Identifies** the MOST CRITICAL issue (highest priority)
3. **Generates** detailed fix with:
   - Exact Python code to implement
   - File locations and line numbers
   - Test cases for the fix
   - Implementation notes with spec references
4. **Saves** to `ai_artifacts/compliance_checks/dfxp/suggested_dfxp_fixes.md`

**Key optimization**: Focuses on ONE critical issue at a time to avoid context overflow.

## Usage

```bash
/suggest-dfxp-fixes
```

Automatically finds latest report and generates fix for top priority issue.

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
reports = glob.glob("ai_artifacts/compliance_checks/dfxp/compliance_report_*.md")
if not reports:
    print("No compliance report found. Run /check-dfxp-compliance first.")
    exit(0)

latest_report = max(reports, key=os.path.getmtime)
print(f"Using: {latest_report}")

# ===== Step 2: Extract Critical Issue =====
with open(latest_report) as _f:
    report_content = _f.read()

# Priority 1: Validation gaps (MUST severity, code exists but wrong)
val_gaps_section = re.search(
    r'## 1\. Validation Gaps.*?\n(.*?)(?=\n## |\Z)',
    report_content, re.DOTALL
)

# Priority 2: Implementation caveats
caveats_section = re.search(
    r'## 2\. Implementation Caveats.*?\n(.*?)(?=\n## |\Z)',
    report_content, re.DOTALL
)

# Priority 3: Missing MUST rules
missing_section = re.search(
    r'### MUST Rules.*?\n(.*?)(?=\n### |\n## |\Z)',
    report_content, re.DOTALL
)

issue_info = None

# Try validation gaps first
if val_gaps_section:
    text = val_gaps_section.group(1)
    match = re.search(
        r'### (RULE-[A-Z]+-\d{3}|IMPL-\d{3}):\s+(.+?)(?:\n|$)',
        text
    )
    if match:
        issue_id = match.group(1)
        issue_title = match.group(2).strip()
        issue_type = 'VALIDATION_GAP'

        status_match = re.search(
            rf'{re.escape(issue_id)}.*?\*\*Status\*\*:\s+(\S+)',
            text, re.DOTALL
        )
        severity_match = re.search(
            rf'{re.escape(issue_id)}.*?\*\*Severity\*\*:\s+(\S+)',
            text, re.DOTALL
        )
        note_match = re.search(
            rf'{re.escape(issue_id)}.*?\*\*Note\*\*:\s+(.+?)(?=\n###|\n##|\Z)',
            text, re.DOTALL
        )

        issue_info = {
            'id': issue_id,
            'title': issue_title,
            'type': issue_type,
            'severity': severity_match.group(1) if severity_match else 'UNKNOWN',
            'status': status_match.group(1) if status_match else 'UNKNOWN',
            'note': note_match.group(1).strip() if note_match else '',
        }
        print(f"Focus: {issue_id} - {issue_title} (VALIDATION GAP)")

# Try caveats
if not issue_info and caveats_section:
    text = caveats_section.group(1)
    match = re.search(
        r'### (RULE-[A-Z]+-\d{3}|IMPL-\d{3}):\s+(.+?)(?:\n|$)',
        text
    )
    if match:
        issue_id = match.group(1)
        issue_title = match.group(2).strip()
        issue_type = 'IMPLEMENTATION_CAVEAT'
        note_match = re.search(
            rf'{re.escape(issue_id)}.*?\*\*Note\*\*:\s+(.+?)(?=\n###|\n##|\Z)',
            text, re.DOTALL
        )
        issue_info = {
            'id': issue_id,
            'title': issue_title,
            'type': issue_type,
            'severity': 'SHOULD',
            'status': 'PARTIAL',
            'note': note_match.group(1).strip() if note_match else '',
        }
        print(f"Focus: {issue_id} - {issue_title} (CAVEAT)")

# Try missing MUST rules
if not issue_info and missing_section:
    text = missing_section.group(1)
    match = re.search(
        r'-\s+\*\*(RULE-[A-Z]+-\d{3}|IMPL-\d{3})\*\*:\s+(.+?)(?:\n|$)',
        text
    )
    if match:
        issue_id = match.group(1)
        issue_title = match.group(2).strip()
        status_match = re.search(r'\((\w+)\)$', issue_title)
        status = status_match.group(1) if status_match else 'MISSING'
        if status_match:
            issue_title = issue_title[:status_match.start()].strip()

        issue_info = {
            'id': issue_id,
            'title': issue_title,
            'type': 'MISSING_MUST',
            'severity': 'MUST',
            'status': status,
            'note': '',
        }
        print(f"Focus: {issue_id} - {issue_title} (MISSING MUST)")

if not issue_info:
    print("No critical issues found!")
    exit(0)

# ===== Step 3: Load Spec Details =====
spec_path = "ai_artifacts/specs/dfxp/dfxp_specs_summary.md"
spec_section = None

if os.path.exists(spec_path):
    with open(spec_path) as _f:
        spec_content = _f.read()
    rule_match = re.search(
        rf'\*\*\[{re.escape(issue_info["id"])}\]\*\*.*?(?=\*\*\[(?:RULE|IMPL)-|\Z)',
        spec_content, re.DOTALL
    )
    if rule_match:
        spec_section = rule_match.group(0)
        print(f"Found spec section for {issue_info['id']} ({len(spec_section)} chars)")
    else:
        print(f"No spec section found for {issue_info['id']}")


def extract_spec_reference(spec_text, _issue_id):
    if not spec_text:
        return _issue_id
    sources_match = re.search(r'\*\*Sources:\*\*\s+(.+?)(?=\n\*\*|\n\n)', spec_text, re.DOTALL)
    if sources_match:
        sources = sources_match.group(1).strip()
        if 'W3C' in sources or 'TTML' in sources:
            return f"{_issue_id} (per W3C TTML Specification)"
    return _issue_id


# ===== Step 4: Read Relevant Code =====
if 'TIME' in issue_info['id']:
    file_path = 'pycaption/dfxp/base.py'
    search_terms = ['_convert_clock_time', '_convert_time_count', 'CLOCK_TIME_PATTERN',
                    'OFFSET_TIME_PATTERN', 'frameRate', 'frame_rate']
elif 'STY' in issue_info['id'] or 'SMOD' in issue_info['id']:
    file_path = 'pycaption/dfxp/base.py'
    search_terms = ['_convert_style', '_recreate_style', '_get_style_reference_chain',
                    '_get_style_sources', 'tts:']
elif 'LAY' in issue_info['id'] or 'region' in issue_info['title'].lower():
    file_path = 'pycaption/dfxp/base.py'
    search_terms = ['_determine_region_id', 'RegionCreator', 'LayoutInfoScraper',
                    'tts:origin', 'tts:extent']
elif 'DOC' in issue_info['id']:
    file_path = 'pycaption/dfxp/base.py'
    search_terms = ['def detect', 'xml:lang', 'DEFAULT_LANGUAGE_CODE', 'read(']
elif 'PAR' in issue_info['id']:
    file_path = 'pycaption/dfxp/base.py'
    search_terms = ['ttp:', 'frameRate', 'tickRate', 'timeBase']
elif 'VAL' in issue_info['id']:
    file_path = 'pycaption/dfxp/base.py'
    search_terms = ['CaptionReadTimingError', 'CaptionReadSyntaxError',
                    'CaptionReadNoCaptions', 'raise']
elif 'CONT' in issue_info['id']:
    file_path = 'pycaption/dfxp/base.py'
    search_terms = ['find_all', 'new_tag', 'NavigableString', '_pre_order_visit']
elif 'IMPL' in issue_info['id']:
    file_path = 'pycaption/dfxp/base.py'
    search_terms = ['_convert_style', '_get_style', 'namespace', 'escape']
else:
    file_path = 'pycaption/dfxp/base.py'
    search_terms = [issue_info['title'].split()[0].lower()]

existing_code = None
grep_results = []
for term in search_terms:
    try:
        result = subprocess.run(['grep', '-n', term, file_path], capture_output=True, text=True)
        if result.stdout.strip():
            grep_results.extend([f"{file_path}:{line}" for line in result.stdout.strip().split('\n')])
            if existing_code is None:
                existing_code = result.stdout.strip()
    except Exception:
        pass

if 'LAY' in issue_info['id'] or 'STY' in issue_info['id']:
    for geom_term in ['cell_resolution', 'UnitEnum', 'from_string']:
        try:
            result = subprocess.run(['grep', '-n', geom_term, 'pycaption/geometry.py'],
                                   capture_output=True, text=True)
            if result.stdout.strip():
                grep_results.extend([f"pycaption/geometry.py:{line}" for line in result.stdout.strip().split('\n')])
        except Exception:
            pass


# ===== Fix Generation Functions =====

def generate_dfxp_fix(_issue_info, _spec_section, _existing_code):
    _issue_id = _issue_info['id']
    spec_ref = extract_spec_reference(_spec_section, _issue_id)

    if _issue_id in ('RULE-TIME-002', 'RULE-TIME-014') or 'frameRate' in _issue_info.get('note', ''):
        return f'''
#### Change Required

The frame rate is hardcoded to 30 in two locations. Both must read `ttp:frameRate` from the document.

```python
# File: pycaption/dfxp/base.py
# Location: DFXPReader class -- add frame rate extraction in read()

class DFXPReader(BaseReader):

    def read(self, content, lang=None, ...):
        dfxp_document = bs4.BeautifulSoup(content, "lxml-xml")

        # ADD: Read ttp:frameRate from root <tt> element
        tt_element = dfxp_document.find("tt")
        frame_rate = 30  # TTML default
        if tt_element:
            fr_attr = tt_element.get("ttp:frameRate")
            if fr_attr:
                try:
                    frame_rate = int(fr_attr)
                except ValueError:
                    pass
```

```python
# File: pycaption/dfxp/base.py
# Location: _convert_clock_time_to_microseconds

# BEFORE (hardcoded /30):
if clock_time_match.group("frames"):
    frames = int(clock_time_match.group("frames"))
    microseconds += frames / 30 * MICROSECONDS_PER_UNIT["seconds"]

# AFTER (uses document frame rate):
if clock_time_match.group("frames"):
    frames = int(clock_time_match.group("frames"))
    microseconds += frames / frame_rate * MICROSECONDS_PER_UNIT["seconds"]
```

**What**: Read `ttp:frameRate` from the `<tt>` root element and use it instead of hardcoded 30.

**Why**: According to **{spec_ref}**, the `ttp:frameRate` parameter specifies the frame rate
for interpreting frame components in time expressions.

**Spec Reference**: See `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` ->
`[RULE-TIME-002]`, `[RULE-TIME-014]`, `[RULE-PAR-002]`
'''

    elif _issue_id == 'RULE-DOC-001':
        return f'''
#### Change Required

```python
# File: pycaption/dfxp/base.py
# Location: DFXPReader.detect() class method

# BEFORE (substring check):
@staticmethod
def detect(content):
    return "</tt>" in content.lower()

# AFTER (proper XML root element check):
@staticmethod
def detect(content):
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(content)
        local_name = root.tag.split("}}")[1] if "{{" in root.tag else root.tag
        return local_name == "tt"
    except (ET.ParseError, IndexError):
        return bool(re.search(
            r'<tt\\b[^>]*xmlns[^>]*http://www.w3.org/ns/ttml',
            content
        ))
```

**What**: Replace substring `"</tt>"` check with proper XML root element detection.

**Why**: According to **{spec_ref}**, a DFXP document MUST have `<tt>` as the root element.

**Spec Reference**: See `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` -> `[RULE-DOC-001]`
'''

    elif _issue_id == 'RULE-DOC-003':
        return f'''
#### Change Required

```python
# File: pycaption/dfxp/base.py
# Location: Where xml:lang is read

import warnings

# BEFORE (silent fallback):
lang = dfxp_document.tt.attrs.get("xml:lang", DEFAULT_LANGUAGE_CODE)

# AFTER (with warning on fallback):
lang = dfxp_document.tt.attrs.get("xml:lang")
if not lang:
    warnings.warn(
        "DFXP document missing xml:lang attribute, "
        f"defaulting to '{{DEFAULT_LANGUAGE_CODE}}'",
        UserWarning,
        stacklevel=2,
    )
    lang = DEFAULT_LANGUAGE_CODE
```

**What**: Emit a warning when xml:lang is missing instead of silently falling back to "en".

**Why**: According to **{spec_ref}**, the `xml:lang` attribute specifies the document language.

**Spec Reference**: See `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` -> `[RULE-DOC-003]`
'''

    elif _issue_id in ('RULE-STY-006', 'RULE-STY-008'):
        attr_name = 'fontWeight' if '006' in _issue_id else 'textDecoration'
        style_key = 'bold' if '006' in _issue_id else 'underline'
        tts_value = 'bold' if '006' in _issue_id else 'underline'

        return f'''
#### Change Required

```python
# File: pycaption/dfxp/base.py
# Location: _recreate_style() function

def _recreate_style(content, dfxp):
    attrs = {{}}
    # ... existing attribute handling ...

    # ADD: Write {attr_name}
    if content.get("{style_key}"):
        attrs["tts:{attr_name}"] = "{tts_value}"

    return attrs
```

**What**: Add `tts:{attr_name}` to `_recreate_style()` output so it round-trips through write.

**Why**: Currently `_convert_style()` reads `tts:{attr_name}` and sets `attrs["{style_key}"] = True`,
but `_recreate_style()` never checks for `"{style_key}"` -- silently dropping it on write.

**Spec Reference**: See `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` -> `[RULE-STY-{_issue_id[-3:]}]`
'''

    elif _issue_id == 'RULE-STY-002':
        return f'''
#### Change Required

```python
# File: pycaption/dfxp/base.py
# Location 1: _convert_style() in DFXPReader

def _convert_style(self, attrs):
    result = {{}}
    # ... existing conversions ...

    # ADD: Read backgroundColor
    if "tts:backgroundColor" in attrs:
        result["background-color"] = attrs["tts:backgroundColor"]

    return result
```

```python
# File: pycaption/dfxp/base.py
# Location 2: _recreate_style()

def _recreate_style(content, dfxp):
    attrs = {{}}
    # ... existing attribute handling ...

    # ADD: Write backgroundColor
    if content.get("background-color"):
        attrs["tts:backgroundColor"] = content["background-color"]

    return attrs
```

**What**: Add read + write support for `tts:backgroundColor`.

**Why**: According to **{spec_ref}**, `tts:backgroundColor` is a core styling attribute.

**Spec Reference**: See `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` -> `[RULE-STY-002]`
'''

    elif _issue_id == 'RULE-TIME-009':
        return f'''
#### Change Required

```python
# File: pycaption/dfxp/base.py
# Location: _convert_time_count_to_microseconds

# BEFORE (raises NotImplementedError):
elif metric == "t":
    raise NotImplementedError(
        "The tick metric is not currently implemented."
    )

# AFTER (implements tick conversion):
elif metric == "t":
    tick_rate = getattr(self, '_tick_rate', None)
    if tick_rate is None:
        frame_rate = getattr(self, '_frame_rate', 30)
        sub_frame_rate = getattr(self, '_sub_frame_rate', 1)
        tick_rate = frame_rate * sub_frame_rate
    return value / tick_rate * MICROSECONDS_PER_UNIT["seconds"]
```

**What**: Implement tick time conversion instead of raising NotImplementedError.

**Why**: According to **{spec_ref}**, the tick metric (`Nt`) is a valid TTML time expression.

**Spec Reference**: See `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` ->
`[RULE-TIME-009]`, `[RULE-PAR-005]`
'''

    else:
        return f'''
#### Implementation Template

```python
# File: {file_path}

# Issue: {_issue_info['title']}
# Status: {_issue_info['status']}
# Current: {_issue_info.get('note', 'See compliance report')}

# TODO: Implement fix for {_issue_id}
```

**What**: Fix for {_issue_info['title']}

**Why**: According to **{spec_ref}**, this is a {_issue_info['severity']}-level requirement.

**Spec Reference**: See `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` ->
Search for `[{_issue_id}]` for complete specification details.
'''


def generate_dfxp_tests(_issue_info):
    _issue_id = _issue_info['id']

    if _issue_id in ('RULE-TIME-002', 'RULE-TIME-014'):
        return '''
```python
# File: tests/test_dfxp.py

def test_frame_rate_from_document():
    from pycaption.dfxp import DFXPReader

    dfxp_25fps = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:ttp="http://www.w3.org/ns/ttml#parameter"
    ttp:frameRate="25">
  <body>
    <div>
      <p begin="00:00:01:12" end="00:00:05:00">Test at 25fps</p>
    </div>
  </body>
</tt>"""

    reader = DFXPReader()
    result = reader.read(dfxp_25fps)
    captions = result.get_captions("en")
    assert len(captions) == 1
    # begin = 1s + 12/25s = 1.48s = 1480000us
    assert captions[0].start == 1480000


def test_frame_rate_default_30():
    from pycaption.dfxp import DFXPReader

    dfxp_no_fps = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
  <body>
    <div>
      <p begin="00:00:01:15" end="00:00:05:00">Test default fps</p>
    </div>
  </body>
</tt>"""

    reader = DFXPReader()
    result = reader.read(dfxp_no_fps)
    captions = result.get_captions("en")
    # begin = 1s + 15/30s = 1.5s = 1500000us
    assert captions[0].start == 1500000
```
'''

    elif _issue_id == 'RULE-DOC-001':
        return '''
```python
# File: tests/test_dfxp.py

def test_detect_rejects_html_with_tt():
    from pycaption.dfxp import DFXPReader
    html_content = "<html><body><tt>teletype</tt></body></html>"
    assert not DFXPReader.detect(html_content)


def test_detect_valid_dfxp():
    from pycaption.dfxp import DFXPReader
    dfxp_content = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
  <body><div><p begin="00:00:01.000" end="00:00:05.000">Test</p></div></body>
</tt>"""
    assert DFXPReader.detect(dfxp_content)
```
'''

    elif _issue_id in ('RULE-STY-006', 'RULE-STY-008'):
        attr = 'bold' if '006' in _issue_id else 'underline'
        tts_attr = 'fontWeight' if '006' in _issue_id else 'textDecoration'
        tts_value = 'bold' if '006' in _issue_id else 'underline'

        return f'''
```python
# File: tests/test_dfxp.py

def test_{attr}_round_trip():
    from pycaption.dfxp import DFXPReader, DFXPWriter

    dfxp_input = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml"
    xmlns:tts="http://www.w3.org/ns/ttml#styling">
  <body>
    <div>
      <p begin="00:00:01.000" end="00:00:05.000">
        <span tts:{tts_attr}="{tts_value}">Styled text</span>
      </p>
    </div>
  </body>
</tt>"""

    reader = DFXPReader()
    caption_set = reader.read(dfxp_input)

    writer = DFXPWriter()
    output = writer.write(caption_set)

    assert "tts:{tts_attr}" in output or "{tts_value}" in output
```
'''

    else:
        return f'''
```python
# File: tests/test_dfxp.py

def test_{_issue_id.lower().replace("-", "_")}():
    from pycaption.dfxp import DFXPReader

    dfxp_content = """<?xml version="1.0" encoding="UTF-8"?>
<tt xml:lang="en" xmlns="http://www.w3.org/ns/ttml">
  <body>
    <div>
      <p begin="00:00:01.000" end="00:00:05.000">Test content</p>
    </div>
  </body>
</tt>"""

    reader = DFXPReader()
    result = reader.read(dfxp_content)
    assert result is not None
```
'''


def generate_dfxp_notes(_issue_info):
    notes = []
    rule_id_local = _issue_info['id']

    if _issue_info['severity'] == 'MUST':
        notes.append(
            f"**MUST-level requirement**: This is mandatory per **{rule_id_local}** in the "
            "W3C TTML specification."
        )
    elif _issue_info['severity'] == 'SHOULD':
        notes.append(
            f"**SHOULD-level requirement**: Recommended by **{rule_id_local}** for best practices."
        )

    if _issue_info['type'] == 'VALIDATION_GAP':
        notes.append(
            "**Validation gap**: Code exists that parses this data but does not "
            "validate it. This is more dangerous than missing functionality."
        )
    elif _issue_info['type'] == 'IMPLEMENTATION_CAVEAT':
        notes.append(
            "**Implementation caveat**: Feature is partially implemented with "
            "significant limitations."
        )

    if 'TIME' in rule_id_local or 'PAR' in rule_id_local:
        notes.append(
            "**Timing impact**: Frame rate and timing parameter issues affect ALL "
            "frame-based time expressions in the document."
        )
    elif 'STY' in rule_id_local:
        notes.append(
            "**Styling impact**: Lost styling attributes degrade visual presentation. "
            "Check both `_convert_style()` (read) and `_recreate_style()` (write) paths."
        )

    notes.append("**Implementation files**:")
    notes.append("  - `pycaption/dfxp/base.py` -- DFXPReader, DFXPWriter, time parsing, style handling")
    notes.append("  - `pycaption/dfxp/extras.py` -- SinglePositioningDFXPWriter, LegacyDFXPWriter")
    notes.append("  - `pycaption/geometry.py` -- Layout, Size, UnitEnum, cell resolution")

    notes.append(f"**Specification reference**:")
    notes.append(f"  - Primary: `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` -> Search for `[{rule_id_local}]`")

    return '\n'.join(f'- {note}' if not note.startswith('  ') else note for note in notes)


def estimate_complexity(_issue_info):
    _issue_id = _issue_info['id']
    if _issue_id in ('RULE-DOC-003',):
        return "Low (add warning)"
    elif _issue_id in ('RULE-DOC-001', 'RULE-STY-006', 'RULE-STY-008', 'RULE-STY-002'):
        return "Medium (add/modify code path)"
    elif _issue_id in ('RULE-TIME-002', 'RULE-TIME-014', 'RULE-TIME-009'):
        return "High (requires plumbing frame_rate through multiple functions)"
    else:
        return "Medium (implementation needed)"


def estimate_time(_issue_info):
    _issue_id = _issue_info['id']
    if _issue_id in ('RULE-DOC-003',):
        return "5-10 minutes"
    elif _issue_id in ('RULE-STY-006', 'RULE-STY-008', 'RULE-STY-002', 'RULE-DOC-001'):
        return "15-30 minutes"
    elif _issue_id in ('RULE-TIME-002', 'RULE-TIME-014', 'RULE-TIME-009'):
        return "30-60 minutes"
    else:
        return "15-30 minutes"


# ===== Step 5: Build and Write Report =====
report = f"""# DFXP/TTML Compliance Fix Suggestions

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
**Status**: {issue_info['status']}

**Current State**: {issue_info.get('note', 'See compliance report')}

**Specification Context**: This issue violates **{issue_info['id']}** in the TTML specification.
See `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` for complete specification text.

---

## Proposed Fix

{generate_dfxp_fix(issue_info, spec_section, existing_code)}

---

## Testing

### Test Cases Required

{generate_dfxp_tests(issue_info)}

---

## Verification Steps

1. **Apply the fix** above
2. **Run tests**: `pytest tests/test_dfxp.py -v`
3. **Verify against spec**:
   - Open `ai_artifacts/specs/dfxp/dfxp_specs_summary.md`
   - Search for `[{issue_info['id']}]`
   - Confirm fix meets all requirements
4. **Test with real DFXP/TTML file**
5. **Round-trip test**: Read DFXP -> write DFXP -> diff

---

## Specification Details

**Rule**: {issue_info['id']}
**Level**: {issue_info['severity']} (mandatory compliance)
**Source**: W3C Timed Text Markup Language (TTML)
**Location in Spec**: `ai_artifacts/specs/dfxp/dfxp_specs_summary.md`

---

## Implementation Notes

{generate_dfxp_notes(issue_info)}

---

## Next Steps

After fixing this issue:
1. Mark {issue_info['id']} as resolved
2. Run `/suggest-dfxp-fixes` again for next critical issue
3. Re-run `/check-dfxp-compliance` to verify fix and get updated report
4. Review full spec section in `ai_artifacts/specs/dfxp/dfxp_specs_summary.md` if needed

---

**Generated by**: suggest-dfxp-fixes skill
**Fix complexity**: {estimate_complexity(issue_info)}
**Estimated time**: {estimate_time(issue_info)}
**Spec-backed**: All fixes reference W3C TTML specification requirements
"""

os.makedirs("ai_artifacts/compliance_checks/dfxp", exist_ok=True)
with open("ai_artifacts/compliance_checks/dfxp/suggested_dfxp_fixes.md", "w") as _f:
    _f.write(report)

print(f"""
Fix suggestion generated!

Issue: {issue_info['id']} - {issue_info['title']}
Saved to: ai_artifacts/compliance_checks/dfxp/suggested_dfxp_fixes.md

Summary:
   Severity: {issue_info['severity']}
   Type: {issue_info['type']}
   Complexity: {estimate_complexity(issue_info)}
   Time: {estimate_time(issue_info)}

Next Steps:
   1. Review the suggested fix in the report
   2. Apply the code changes
   3. Run the test cases
   4. Run /suggest-dfxp-fixes again for next issue
""")
```

---

## Success Criteria

- **Context-efficient** - Focuses on one issue (~20K tokens vs 90K+)
- **Actionable** - Exact Python code with file paths and line numbers
- **Spec-backed** - All fixes reference W3C TTML specification
- **Testable** - Includes complete test cases
- **Iterative** - Run multiple times for multiple issues
- **DFXP-aware** - Handles DFXP-specific patterns:
  - Read vs write path distinction (`_convert_style` vs `_recreate_style`)
  - Read-only attributes (fontWeight, textDecoration)
  - Frame rate plumbing (ttp:frameRate through multiple functions)
  - Zero ttp: parameter support (11 parameters never read)
  - Module-level functions vs class methods

## Important Notes

**Priority order for DFXP issues:**
1. Validation gaps (code exists but wrong -- most dangerous)
2. Implementation caveats (partial, may cause subtle bugs)
3. Missing MUST rules (not implemented)
4. Missing SHOULD rules
5. Test gaps

**Key DFXP implementation files:**
- `pycaption/dfxp/base.py` -- DFXPReader, DFXPWriter, LayoutAwareDFXPParser, LayoutInfoScraper
- `pycaption/dfxp/extras.py` -- SinglePositioningDFXPWriter, LegacyDFXPWriter
- `pycaption/geometry.py` -- Layout, Size, UnitEnum (cell resolution hardcoded 32x15)

**Run iteratively**: Each run fixes one issue. Run `/suggest-dfxp-fixes` repeatedly until all critical issues resolved.
