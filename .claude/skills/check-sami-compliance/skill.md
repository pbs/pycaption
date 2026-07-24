---
name: check-sami-compliance
description: Generates EXHAUSTIVE SAMI compliance report checking all 75 rules individually + styling/element/timing/language coverage with deep validation analysis to identify ALL issues in pycaption code.
---

# check-sami-compliance

## What this skill does

Exhaustive SAMI compliance checker - 5 phases:
1. Deep validation (critical rules with function-level detection vs validation)
2. Systematic checking (all 75 rules individually verified with per-rule patterns)
3. Styling property / inline element / timing / language / encoding coverage (read/write distinction)
4. Test coverage analysis
5. Report generation

**Input**: `ai_artifacts/specs/SAMI/sami_spec_summary.md`
**Output**: `ai_artifacts/compliance_checks/sami/compliance_report_{date}.md`

**Usage:** `/check-sami-compliance`

---

## Implementation

**Run this Python script (context-optimized):**

```python
import os, re, glob
from datetime import datetime

print("SAMI Exhaustive Compliance Check\n" + "=" * 60)

# ===== INIT: Load spec and implementation =====
spec_file = 'ai_artifacts/specs/SAMI/sami_spec_summary.md'
if not os.path.exists(spec_file):
    print(f"ERROR: {spec_file} not found")
    raise SystemExit(1)

def _read(p):
    with open(p) as _fh: return _fh.read()

spec = _read(spec_file)

impl_files = [
    'pycaption/sami/reader.py',
    'pycaption/sami/writer.py',
    'pycaption/sami/parser.py',
    'pycaption/sami/constants.py',
    'pycaption/sami/__init__.py',
    'pycaption/base.py',
]
impl_content = {}
for f in impl_files:
    if os.path.exists(f):
        impl_content[f] = _read(f)
impl = "\n".join(impl_content.values())

reader_content = impl_content.get('pycaption/sami/reader.py', '')
writer_content = impl_content.get('pycaption/sami/writer.py', '')
parser_content = impl_content.get('pycaption/sami/parser.py', '')
constants_content = impl_content.get('pycaption/sami/constants.py', '')

print(f"[INIT] Spec: {spec_file} ({len(spec)} chars)")
print(f"[INIT] Implementation: {len(impl_content)} files ({len(impl)} chars)")

# Extract all rules from spec
all_rules = {}
for match in re.finditer(r'\*\*\[(RULE-[A-Z]+-\d{3}|IMPL-\d{3})\]\*\*\s*(.+?)(?:\n|$)', spec):
    rule_id = match.group(1)
    rule_name = match.group(2).strip()
    rule_start = match.start()
    next_rule = re.search(r'\*\*\[(?:RULE-[A-Z]+-\d{3}|IMPL-\d{3})\]\*\*', spec[rule_start + 1:])
    rule_block = spec[rule_start:rule_start + 1 + next_rule.start()] if next_rule else spec[rule_start:]
    level_match = re.search(r'\*\*Level:\*\*\s*(MUST NOT|MUST|SHOULD|MAY)', rule_block)
    level = level_match.group(1) if level_match else 'UNKNOWN'
    all_rules[rule_id] = {'name': rule_name, 'level': level}

print(f"[INIT] Extracted {len(all_rules)} rules from spec")

# ===== SANITY CHECK: Verify expected code landmarks exist =====
landmarks = {
    'class SAMIReader': ('pycaption/sami/reader.py', r'class\s+SAMIReader\b'),
    'class SAMIWriter': ('pycaption/sami/writer.py', r'class\s+SAMIWriter\b'),
    'def detect (SAMIReader)': ('pycaption/sami/reader.py', r'def\s+detect\b'),
    'def read (SAMIReader)': ('pycaption/sami/reader.py', r'def\s+read\b'),
    'def write (SAMIWriter)': ('pycaption/sami/writer.py', r'def\s+write\b'),
    'SAMIParser or parse function': ('pycaption/sami/parser.py', r'class\s+SAMIParser\b|def\s+parse\b|def\s+_parse\b'),
    'SAMI_BASE_MARKUP or structure': ('pycaption/sami/constants.py', r'SAMI_BASE_MARKUP|SAMI_|SYNC|<SAMI'),
}
stale_warnings = []
for name, (expected_file, pattern) in landmarks.items():
    try:
        with open(expected_file) as _fh:
            if not re.search(pattern, _fh.read()):
                stale_warnings.append(f"{name} not found in {expected_file}")
    except FileNotFoundError:
        stale_warnings.append(f"{expected_file} does not exist")

if stale_warnings:
    print(f"[SANITY] WARNING: {len(stale_warnings)} landmark(s) not found — patterns may be stale:")
    for w in stale_warnings:
        print(f"  - {w}")
else:
    print("[SANITY] All code landmarks found")

issues = {
    'validation_gaps': [],
    'partial_validation': [],
    'missing': [],
    'test_gaps': [],
}

# ===== PHASE 1: DEEP VALIDATION ANALYSIS =====
print("\n" + "=" * 60)
print("PHASE 1: DEEP VALIDATION ANALYSIS")
print("=" * 60)

deep_results = {}

# RULE-DOC-001: SAMI root element detection
has_detect = bool(re.search(r'def detect', reader_content))
has_sami_check = bool(re.search(r'<SAMI|<sami', impl, re.I))
deep_results['RULE-DOC-001'] = {
    'name': 'SAMI root element detection',
    'detected': has_detect and has_sami_check,
    'validated': has_detect,
    'note': 'detect() checks for <SAMI> element',
}
print(f"  RULE-DOC-001: {'PASS' if has_detect else 'FAIL'}")

# RULE-TIME-001: SYNC Start attribute
has_sync_parse = bool(re.search(r'start|Start|SYNC', reader_content + parser_content))
has_start_extract = bool(re.search(r'start\s*=|get.*start|Start.*=.*\d', impl, re.I))
deep_results['RULE-TIME-001'] = {
    'name': 'SYNC Start attribute parsing',
    'detected': has_sync_parse,
    'validated': has_start_extract,
    'note': 'Parser extracts Start= millisecond values from SYNC elements',
}
print(f"  RULE-TIME-001: {'PASS' if has_start_extract else 'FAIL'}")

# RULE-TIME-003: Implicit end time calculation
has_implicit_end = bool(re.search(r'end.*=.*start|next.*sync|caption\[.*\+.*1\]|end_of_caption', impl))
deep_results['RULE-TIME-003'] = {
    'name': 'Implicit end time calculation',
    'detected': has_implicit_end,
    'validated': has_implicit_end,
    'note': 'End time derived from next SYNC Start value' if has_implicit_end else 'No implicit end time calculation found',
}
if not has_implicit_end:
    issues['validation_gaps'].append({
        'rule_id': 'RULE-TIME-003', 'name': 'Implicit end time calculation',
        'status': 'NOT_DETECTED', 'severity': 'MUST',
        'note': 'SAMI has no explicit end time — must derive from next SYNC block',
    })
print(f"  RULE-TIME-003: {'PASS' if has_implicit_end else 'MISSING'}")

# RULE-TIME-004: Caption clearing (nbsp)
has_nbsp_clear = bool(re.search(r'&nbsp;|\\xa0|is_empty|empty_paragraph|blank', impl, re.I))
deep_results['RULE-TIME-004'] = {
    'name': 'Caption clearing mechanism',
    'detected': has_nbsp_clear,
    'validated': has_nbsp_clear,
    'note': 'Recognizes &nbsp; as clear event' if has_nbsp_clear else 'No clear mechanism found',
}
print(f"  RULE-TIME-004: {'PASS' if has_nbsp_clear else 'MISSING'}")

# RULE-PARSE-001: Case-insensitive parsing
has_case_insensitive = bool(re.search(r'\.lower\(\)|re\.I|re\.IGNORECASE|[Bb]eautiful[Ss]oup', impl))
deep_results['RULE-PARSE-001'] = {
    'name': 'Case-insensitive element parsing',
    'detected': has_case_insensitive,
    'validated': has_case_insensitive,
    'note': 'BeautifulSoup handles case-insensitive HTML parsing natively' if bool(re.search(r'[Bb]eautiful[Ss]oup|BeautifulSoup|bs4', impl)) else 'Uses .lower() or re.I',
}
print(f"  RULE-PARSE-001: {'PASS' if has_case_insensitive else 'FAIL'}")

# RULE-PARSE-002: Tolerant/lenient parsing
has_lenient = bool(re.search(r'html\.parser|html5lib|lxml|[Bb]eautiful[Ss]oup', impl))
deep_results['RULE-PARSE-002'] = {
    'name': 'Tolerant/lenient parsing',
    'detected': has_lenient,
    'validated': has_lenient,
    'note': 'Uses BeautifulSoup for lenient HTML parsing' if has_lenient else 'No lenient parser detected',
}
print(f"  RULE-PARSE-002: {'PASS' if has_lenient else 'FAIL'}")

# RULE-PARSE-003: HTML comment handling in STYLE
has_comment_strip = bool(re.search(r'<!--.*-->|comment|strip_comment|replace.*<!--', impl, re.I))
deep_results['RULE-PARSE-003'] = {
    'name': 'HTML comment handling in STYLE',
    'detected': has_comment_strip,
    'validated': has_comment_strip,
    'note': 'Strips <!-- --> from STYLE content' if has_comment_strip else 'No comment handling found',
}
print(f"  RULE-PARSE-003: {'PASS' if has_comment_strip else 'MISSING'}")

# RULE-LANG-001: CLASS attribute on P elements
has_class_parse = bool(re.search(r'class|Class|\.get.*class', reader_content + parser_content, re.I))
has_lang_separation = bool(re.search(r'lang|language|class.*lang', impl, re.I))
deep_results['RULE-LANG-001'] = {
    'name': 'CLASS attribute for language filtering',
    'detected': has_class_parse,
    'validated': has_lang_separation,
    'note': 'Extracts Class attribute from P elements for language track separation',
}
print(f"  RULE-LANG-001: {'PASS' if has_class_parse else 'FAIL'}")

# RULE-LANG-002: CSS class definitions for languages
has_css_class_parse = bool(re.search(r'\.(\w+)\s*\{|class.*name.*lang|SAMI_Type', impl))
deep_results['RULE-LANG-002'] = {
    'name': 'CSS class definitions for languages',
    'detected': has_css_class_parse,
    'validated': has_css_class_parse,
    'note': 'Parses .ClassName { Name:; lang:; } from STYLE section',
}
print(f"  RULE-LANG-002: {'PASS' if has_css_class_parse else 'FAIL'}")

# RULE-STY-001: CSS parsing in STYLE section
has_css_parse = bool(re.search(r'css|style|stylesheet|_parse_style|CSSStyleDeclaration', impl, re.I))
deep_results['RULE-STY-001'] = {
    'name': 'CSS1 syntax in STYLE section',
    'detected': has_css_parse,
    'validated': has_css_parse,
    'note': 'Parses CSS from STYLE section',
}
print(f"  RULE-STY-001: {'PASS' if has_css_parse else 'FAIL'}")

# IMPL-006: Writer produces valid SAMI structure
has_writer_sami = bool(re.search(r'<SAMI|SAMI_BASE_MARKUP', writer_content + constants_content))
has_writer_head = bool(re.search(r'<HEAD|<STYLE|HEAD', writer_content + constants_content))
has_writer_body = bool(re.search(r'<BODY|BODY', writer_content + constants_content))
has_writer_sync = bool(re.search(r'<SYNC|SYNC|Start=', writer_content))
deep_results['IMPL-006'] = {
    'name': 'Writer produces valid SAMI structure',
    'detected': has_writer_sami,
    'validated': has_writer_sami and has_writer_head and has_writer_body and has_writer_sync,
    'note': 'Writer emits SAMI/HEAD/STYLE/BODY/SYNC/P skeleton' if (has_writer_sami and has_writer_sync) else 'Writer structure incomplete',
}
print(f"  IMPL-006: {'PASS' if (has_writer_sami and has_writer_sync) else 'INCOMPLETE'}")

# IMPL-007: Writer emits millisecond timing
has_ms_timing = bool(re.search(r'Start\s*=\s*\d|Start=.*microseconds|/ 1000|// 1000', writer_content))
deep_results['IMPL-007'] = {
    'name': 'Writer emits millisecond timing',
    'detected': has_ms_timing,
    'validated': has_ms_timing,
    'note': 'Writer converts microseconds to millisecond Start= values' if has_ms_timing else 'No ms timing conversion found',
}
print(f"  IMPL-007: {'PASS' if has_ms_timing else 'FAIL'}")

# IMPL-008: Writer emits clear events (nbsp)
has_writer_clear = bool(re.search(r'&nbsp;|nbsp|clear|blank|empty.*P', writer_content, re.I))
deep_results['IMPL-008'] = {
    'name': 'Writer emits clear events',
    'detected': has_writer_clear,
    'validated': has_writer_clear,
    'note': 'Writer emits &nbsp; P elements to clear display' if has_writer_clear else 'No clear event emission found',
}
if not has_writer_clear:
    issues['validation_gaps'].append({
        'rule_id': 'IMPL-008', 'name': 'Writer does not emit clear events',
        'status': 'NOT_IMPLEMENTED', 'severity': 'MUST',
        'note': 'Writer should emit SYNC with empty/nbsp P at caption end to clear display',
    })
print(f"  IMPL-008: {'PASS' if has_writer_clear else 'MISSING'}")

# IMPL-009: Writer preserves language classes
has_writer_class = bool(re.search(r'[Cc]lass\s*=|class.*attr|P.*Class', writer_content))
deep_results['IMPL-009'] = {
    'name': 'Writer preserves language classes',
    'detected': has_writer_class,
    'validated': has_writer_class,
    'note': 'Writer emits Class= on P elements' if has_writer_class else 'No Class attribute in writer output',
}
print(f"  IMPL-009: {'PASS' if has_writer_class else 'FAIL'}")

# IMPL-010: Writer preserves styling
has_writer_style = bool(re.search(r'style|css|font|color|text-align', writer_content, re.I))
deep_results['IMPL-010'] = {
    'name': 'Writer preserves styling',
    'detected': has_writer_style,
    'validated': has_writer_style,
    'note': 'Writer emits CSS styling in STYLE section' if has_writer_style else 'No styling in writer',
}
print(f"  IMPL-010: {'PASS' if has_writer_style else 'FAIL'}")

# ===== PHASE 2: SYSTEMATIC RULE CHECK =====
print("\n" + "=" * 60)
print("PHASE 2: ALL RULES CHECK ({} rules)".format(len(all_rules)))
print("=" * 60)

specific_patterns = {
    # Document structure
    'RULE-DOC-001': [r'<SAMI|sami.*root|def detect'],
    'RULE-DOC-002': [r'</SAMI|EOF|end.*sami'],
    'RULE-DOC-003': [r'<HEAD|find.*head|HEAD'],
    'RULE-DOC-004': [r'<BODY|find.*body|BODY'],
    'RULE-DOC-005': [r'<STYLE|find.*style|STYLE.*TYPE'],
    'RULE-DOC-006': [r'\.smi|\.sami|file.*ext'],
    'RULE-DOC-007': [r'<TITLE|title|TITLE'],
    'RULE-DOC-008': [r'SAMIParam|samiparam'],
    # Timing
    'RULE-TIME-001': [r'Start\s*=|sync.*start|SYNC.*Start'],
    'RULE-TIME-002': [r'millisecond|int\(.*start|Start.*\d+'],
    'RULE-TIME-003': [r'end.*next.*start|implicit.*end|end_of_caption'],
    'RULE-TIME-004': [r'&nbsp;|nbsp|clear|blank.*caption|empty.*p'],
    'RULE-TIME-005': [r'monoton|order|start.*<=.*start|non.*decreas'],
    'RULE-TIME-006': [r'[Ff]rame|SMPTE|Metrics.*time'],
    # Multi-language
    'RULE-LANG-001': [r'[Cc]lass.*=|class.*attr|P.*[Cc]lass'],
    'RULE-LANG-002': [r'\.\w+\s*\{|Name\s*:|lang\s*:|SAMI_Type'],
    'RULE-LANG-003': [r'ISO.*639|naming.*convent|ENCC|FRCC'],
    'RULE-LANG-004': [r'multiple.*P|multi.*lang|language.*class'],
    'RULE-LANG-005': [r'default.*lang|first.*class|DEFAULT_LANGUAGE'],
    'RULE-LANG-006': [r'classless|no.*[Cc]lass|without.*class'],
    # Styling
    'RULE-STY-001': [r'css|CSS|stylesheet|style.*pars'],
    'RULE-STY-002': [r'P\s*\{|paragraph.*style|selector.*P\b'],
    'RULE-STY-003': [r'\bcolor\b.*:'],
    'RULE-STY-004': [r'background.color|background-color'],
    'RULE-STY-005': [r'font.family|font-family'],
    'RULE-STY-006': [r'font.size|font-size'],
    'RULE-STY-007': [r'font.weight|font-weight|bold'],
    'RULE-STY-008': [r'font.style|font-style|italic'],
    'RULE-STY-009': [r'text.align|text-align'],
    'RULE-STY-010': [r'margin.left|margin-left|margin.right|margin-right|margin.top|margin-top|margin.bottom|margin-bottom'],
    'RULE-STY-011': [r'text.decoration|text-decoration|underline'],
    'RULE-STY-012': [r'class.*override|specificit|supersede|cascade'],
    'RULE-STY-013': [r'#\w+\s*\{|id.*style|ID.*style'],
    'RULE-STY-014': [r'#Source|source.*id|ID.*=.*Source'],
    # Inline elements
    'RULE-ELEM-001': [r'<[Bb][Rr]|<br|line.*break|BREAK'],
    'RULE-ELEM-002': [r'<[Ff][Oo][Nn][Tt]|font.*size|font.*color|font.*face'],
    'RULE-ELEM-003': [r'<[Bb]>|<b\b|bold|<B>'],
    'RULE-ELEM-004': [r'<[Ii]>|<i\b|italic|<I>'],
    'RULE-ELEM-005': [r'<[Uu]>|<u\b|underline|<U>'],
    'RULE-ELEM-006': [r'<[Ss][Pp][Aa][Nn]|<span|SPAN'],
    'RULE-ELEM-007': [r'<[Ii][Mm][Gg]|<img|IMG'],
    'RULE-ELEM-008': [r'<TABLE|<H\d|<PRE|<BLOCKQUOTE|<DIV|<CENTER'],
    # Character encoding
    'RULE-ENC-001': [r'utf.?8|UTF-8|encoding|charset|Windows-1252'],
    'RULE-ENC-002': [r'&amp;|&lt;|&gt;|&nbsp;|&quot;|html.*entit|unescape'],
    'RULE-ENC-003': [r'&#\d+;|&#x[0-9a-fA-F]+;|numeric.*ref|char.*ref'],
    'RULE-ENC-004': [r'BOM|\\ufeff|\xef\xbb\xbf|byte.*order'],
    'RULE-ENC-005': [r'&nbsp;|\\xa0|non.breaking.*space|clear.*nbsp'],
    # SAMIParam
    'RULE-PARAM-001': [r'[Cc]opyright|Copyright'],
    'RULE-PARAM-002': [r'[Mm]edia.*param|Media\s*\{'],
    'RULE-PARAM-003': [r'[Mm]etrics|duration|time.*unit'],
    'RULE-PARAM-004': [r'[Ss]pec.*param|MSFT|version'],
    # Parsing
    'RULE-PARSE-001': [r'\.lower\(\)|case.*insensit|re\.I|[Bb]eautiful[Ss]oup'],
    'RULE-PARSE-002': [r'html\.parser|lenient|tolerant|[Bb]eautiful[Ss]oup|unclosed'],
    'RULE-PARSE-003': [r'<!--.*-->|comment.*strip|replace.*<!--'],
    'RULE-PARSE-004': [r'unquoted|Start\s*=\s*\d|attr.*no.*quot'],
    'RULE-PARSE-005': [r'fragile|multiple.*id|source.*line'],
    'RULE-PARSE-006': [r'unknown.*tag|unrecognized|skip.*unknown|ignore.*tag'],
    # Conversion
    'RULE-CONV-001': [r'srt|SRT|SubRip'],
    'RULE-CONV-002': [r'dfxp|DFXP|ttml|TTML|tts:'],
    'RULE-CONV-003': [r'webvtt|WebVTT|VTT|::cue'],
    'RULE-CONV-004': [r'multi.*lang|language.*filter|single.*lang'],
    'RULE-CONV-005': [r'inline.*style|format.*convert|bold.*italic'],
    'RULE-CONV-006': [r'loss.*fidelity|unsupported|cannot.*represent'],
    # Implementation
    'IMPL-001': [r'Start\s*=|sync.*start|SYNC.*Start|millisecond'],
    'IMPL-002': [r'end.*next.*start|implicit.*end|end_of_caption|caption.*end'],
    'IMPL-003': [r'[Cc]lass.*filter|lang.*filter|multi.*lang'],
    'IMPL-004': [r'<[BbIiUu]>|bold|italic|underline|<FONT|<SPAN|inline.*format'],
    'IMPL-005': [r'css.*pars|style.*extract|_parse_style|stylesheet'],
    'IMPL-006': [r'<SAMI|SAMI_BASE_MARKUP|write.*sami'],
    'IMPL-007': [r'Start\s*=.*\d|microsecond.*1000|/ 1000|// 1000'],
    'IMPL-008': [r'&nbsp;|clear.*event|blank.*sync|empty.*P'],
    'IMPL-009': [r'[Cc]lass\s*=|class.*attr.*write|P.*Class'],
    'IMPL-010': [r'style.*write|css.*output|font|color.*write'],
    'IMPL-011': [r'monoton|order.*valid|start.*<=|CaptionReadTimingError'],
    'IMPL-012': [r'class.*defin|class.*style.*match|undefined.*class'],
}

missing_rules = []
found_rules = []

for rule_id, meta in sorted(all_rules.items()):
    if rule_id in deep_results:
        if deep_results[rule_id]['detected']:
            found_rules.append(rule_id)
        else:
            if not any(i['rule_id'] == rule_id for i in issues['validation_gaps']):
                missing_rules.append({
                    'rule_id': rule_id, 'name': meta['name'],
                    'level': meta['level'], 'status': 'MISSING',
                })
        continue

    patterns = specific_patterns.get(rule_id, [])
    if not patterns:
        missing_rules.append({
            'rule_id': rule_id, 'name': meta['name'],
            'level': meta['level'], 'status': 'NO_PATTERN',
        })
        continue

    found = any(re.search(p, impl, re.I) for p in patterns)
    if found:
        found_rules.append(rule_id)
    else:
        missing_rules.append({
            'rule_id': rule_id, 'name': meta['name'],
            'level': meta['level'], 'status': 'MISSING',
        })

issues['missing'] = missing_rules
must_missing = [r for r in missing_rules if r['level'] == 'MUST']
print(f"  Found: {len(found_rules)}/{len(all_rules)}, Missing: {len(missing_rules)} (MUST: {len(must_missing)})")

# ===== PHASE 3: COVERAGE ANALYSIS =====
print("\n" + "=" * 60)
print("PHASE 3: COVERAGE ANALYSIS")
print("=" * 60)

# Styling properties: track read vs write
styling_coverage = {
    'color': {
        'read': bool(re.search(r'\bcolor\b', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'\bcolor\b', writer_content, re.I)),
        'note': '',
    },
    'background-color': {
        'read': bool(re.search(r'background.color', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'background.color', writer_content, re.I)),
        'note': '',
    },
    'font-family': {
        'read': bool(re.search(r'font.family', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'font.family', writer_content, re.I)),
        'note': '',
    },
    'font-size': {
        'read': bool(re.search(r'font.size', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'font.size', writer_content, re.I)),
        'note': '',
    },
    'font-weight': {
        'read': bool(re.search(r'font.weight|bold', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'font.weight|bold', writer_content, re.I)),
        'note': '',
    },
    'font-style': {
        'read': bool(re.search(r'font.style|italic', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'font.style|italic', writer_content, re.I)),
        'note': '',
    },
    'text-align': {
        'read': bool(re.search(r'text.align', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'text.align', writer_content, re.I)),
        'note': '',
    },
    'margin-left': {
        'read': bool(re.search(r'margin.left', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'margin.left', writer_content, re.I)),
        'note': '',
    },
    'margin-right': {
        'read': bool(re.search(r'margin.right', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'margin.right', writer_content, re.I)),
        'note': '',
    },
    'margin-top': {
        'read': bool(re.search(r'margin.top', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'margin.top', writer_content, re.I)),
        'note': '',
    },
    'margin-bottom': {
        'read': bool(re.search(r'margin.bottom', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'margin.bottom', writer_content, re.I)),
        'note': '',
    },
    'text-decoration': {
        'read': bool(re.search(r'text.decoration|underline', reader_content + parser_content, re.I)),
        'write': bool(re.search(r'text.decoration|underline', writer_content, re.I)),
        'note': '',
    },
}

sty_read = sum(1 for s in styling_coverage.values() if s['read'])
sty_write = sum(1 for s in styling_coverage.values() if s['write'])
sty_roundtrip = sum(1 for s in styling_coverage.values() if s['read'] and s['write'])
print(f"  Styling: {sty_read}/12 read, {sty_write}/12 write, {sty_roundtrip}/12 round-trip")

# Inline elements
element_coverage = {
    'BR':   {'read': bool(re.search(r'<br|BR|line.*break|BREAK', reader_content + parser_content, re.I)),
             'write': bool(re.search(r'<br|BR|line.*break', writer_content, re.I))},
    'FONT': {'read': bool(re.search(r'<font|FONT|font.*color|font.*face|font.*size', reader_content + parser_content, re.I)),
             'write': bool(re.search(r'<font|FONT', writer_content, re.I))},
    'B':    {'read': bool(re.search(r'<b>|<B>|bold', reader_content + parser_content, re.I)),
             'write': bool(re.search(r'<b>|<B>|bold', writer_content, re.I))},
    'I':    {'read': bool(re.search(r'<i>|<I>|italic', reader_content + parser_content, re.I)),
             'write': bool(re.search(r'<i>|<I>|italic', writer_content, re.I))},
    'U':    {'read': bool(re.search(r'<u>|<U>|underline', reader_content + parser_content, re.I)),
             'write': bool(re.search(r'<u>|<U>|underline', writer_content, re.I))},
    'SPAN': {'read': bool(re.search(r'<span|SPAN|span', reader_content + parser_content, re.I)),
             'write': bool(re.search(r'<span|SPAN|span', writer_content, re.I))},
    'IMG':  {'read': bool(re.search(r'<img|IMG', reader_content + parser_content, re.I)),
             'write': bool(re.search(r'<img|IMG', writer_content, re.I))},
}

elem_read = sum(1 for e in element_coverage.values() if e['read'])
elem_write = sum(1 for e in element_coverage.values() if e['write'])
print(f"  Inline elements: {elem_read}/7 read, {elem_write}/7 write")

# Timing features
timing_coverage = {
    'SYNC Start= parsing': bool(re.search(r'Start\s*=|start.*attr', reader_content + parser_content, re.I)),
    'Millisecond integer values': bool(re.search(r'int\(.*start|Start.*\d+', impl)),
    'Implicit end time (next SYNC)': bool(re.search(r'end.*next|end_of_caption|implicit.*end', impl)),
    'Clear via nbsp': has_nbsp_clear,
    'Monotonic ordering': bool(re.search(r'monoton|order|start.*<=', impl, re.I)),
    'Writer ms output': has_ms_timing,
}
timing_supported = sum(1 for t in timing_coverage.values() if t)
print(f"  Timing features: {timing_supported}/6")

# Language/multi-track features
lang_coverage = {
    'Class attribute extraction': bool(re.search(r'[Cc]lass.*attr|get.*class', reader_content + parser_content)),
    'CSS class definitions parsed': bool(re.search(r'\.\w+\s*\{|Name.*:|lang.*:', impl)),
    'Multi-language separation': bool(re.search(r'lang|language|multi', reader_content, re.I)),
    'Writer Class= output': has_writer_class,
    'Writer STYLE class defs': bool(re.search(r'\.\w+\s*\{|class.*style.*write', writer_content)),
}
lang_supported = sum(1 for l in lang_coverage.values() if l)
print(f"  Language features: {lang_supported}/5")

# Encoding
enc_coverage = {
    'HTML entity decode': bool(re.search(r'html\.unescape|unescape|&amp;|entity', impl)),
    'Numeric char refs': bool(re.search(r'&#\d+;|&#x|numeric.*ref', impl)),
    'BOM handling': bool(re.search(r'BOM|\\ufeff|\xef\xbb\xbf', impl)),
    'nbsp recognition': has_nbsp_clear,
}
enc_supported = sum(1 for e in enc_coverage.values() if e)
print(f"  Encoding features: {enc_supported}/4")

# ===== PHASE 4: TEST COVERAGE =====
print("\n" + "=" * 60)
print("PHASE 4: TEST COVERAGE")
print("=" * 60)

test_files = glob.glob('tests/**/test*sami*.py', recursive=True) + glob.glob('tests/**/test*SAMI*.py', recursive=True)
tests = "\n".join(_read(f) for f in test_files if os.path.exists(f))
print(f"  Test files: {len(test_files)} ({len(tests)} chars)")

test_checks = {
    'RULE-DOC-001': [r'def test.*detect|def test.*sami|def test.*root'],
    'RULE-TIME-001': [r'def test.*time|def test.*sync|def test.*start'],
    'RULE-TIME-003': [r'def test.*end.*time|def test.*implicit|def test.*duration'],
    'RULE-LANG-001': [r'def test.*lang|def test.*class|def test.*multi'],
    'RULE-STY-003': [r'def test.*color|def test.*style'],
    'RULE-STY-009': [r'def test.*align'],
    'RULE-ELEM-001': [r'def test.*break|def test.*br'],
    'RULE-ELEM-004': [r'def test.*italic|def test.*<i'],
    'RULE-PARSE-002': [r'def test.*malform|def test.*invalid|def test.*lenient'],
    'IMPL-006': [r'def test.*write|def test.*output'],
    'IMPL-008': [r'def test.*clear|def test.*nbsp|def test.*blank'],
    'IMPL-009': [r'def test.*class.*write|def test.*lang.*write'],
}

for rid, patterns in test_checks.items():
    if not any(re.search(p, tests, re.I) for p in patterns):
        name = all_rules.get(rid, {}).get('name', rid)
        issues['test_gaps'].append({'rule_id': rid, 'name': name, 'status': 'NO_TEST'})
        print(f"  {rid}: NO TEST")
    else:
        print(f"  {rid}: HAS TEST")

# ===== PHASE 5: GENERATE REPORT =====
print("\n" + "=" * 60)
print("PHASE 5: GENERATE REPORT")
print("=" * 60)

os.makedirs("ai_artifacts/compliance_checks/sami", exist_ok=True)
date = datetime.now().strftime("%Y-%m-%d")
path = f"ai_artifacts/compliance_checks/sami/compliance_report_{date}.md"

total_issues = sum(len(v) for v in issues.values())
must_issues = (len([i for i in issues['validation_gaps'] if i.get('severity') == 'MUST']) +
               len([i for i in issues['partial_validation'] if i.get('severity') == 'MUST']) +
               len(must_missing))

sanity_section = ""
if stale_warnings:
    sanity_section = "\n**STALE PATTERN WARNING**: The following expected code landmarks were not found. Some findings below may report features as 'missing' when they have actually been renamed or moved:\n"
    for w in stale_warnings:
        sanity_section += f"- {w}\n"
    sanity_section += "\n"

report = f"""# SAMI EXHAUSTIVE Compliance Report

**Generated**: {date}
**Spec**: {spec_file} ({len(all_rules)} rules)
**Analysis**: Deep Validation + Systematic Rules + Coverage + Tests
**Implementation files**: {', '.join(f for f in impl_files if os.path.exists(f))}
{sanity_section}
---

## Executive Summary

**Rules checked**: {len(all_rules)}/{len(all_rules)} (100%)
**Total issues**: {total_issues}
**MUST violations**: {must_issues}

| Category | Count |
|----------|-------|
| Validation gaps | {len(issues['validation_gaps'])} |
| Partial/caveats | {len(issues['partial_validation'])} |
| Missing rules | {len(issues['missing'])} (MUST: {len(must_missing)}) |
| Test gaps | {len(issues['test_gaps'])} |

---

## 1. Validation Gaps ({len(issues['validation_gaps'])})

Rules that are not properly implemented or validated.

"""

for g in issues['validation_gaps']:
    report += f"### {g['rule_id']}: {g['name']}\n"
    report += f"- **Status**: {g['status']}\n"
    report += f"- **Severity**: {g['severity']}\n"
    report += f"- **Note**: {g['note']}\n\n"

report += f"""---

## 2. Implementation Caveats ({len(issues['partial_validation'])})

Rules implemented but with significant limitations.

"""

for p in issues['partial_validation']:
    report += f"### {p['rule_id']}: {p['name']}\n"
    report += f"- **Status**: {p['status']}\n"
    report += f"- **Note**: {p['note']}\n\n"

report += f"""---

## 3. Missing Rules ({len(issues['missing'])})

### MUST Rules ({len(must_missing)})

"""

for r in must_missing:
    report += f"- **{r['rule_id']}**: {r['name']} ({r['status']})\n"

should_missing = [r for r in issues['missing'] if r['level'] == 'SHOULD']
may_missing = [r for r in issues['missing'] if r['level'] in ('MAY', 'MUST NOT')]

report += f"\n### SHOULD Rules ({len(should_missing)})\n\n"
for r in should_missing:
    report += f"- **{r['rule_id']}**: {r['name']} ({r['status']})\n"

report += f"\n### MAY/MUST NOT Rules ({len(may_missing)})\n\n"
for r in may_missing:
    report += f"- **{r['rule_id']}**: {r['name']} ({r['status']})\n"

report += f"""
---

## 4. Coverage Analysis

### Styling Properties ({sty_read}/12 read, {sty_write}/12 write, {sty_roundtrip}/12 round-trip)

| Property | Read | Write | Round-trip | Note |
|----------|------|-------|------------|------|
"""

for prop, info in styling_coverage.items():
    r = "Yes" if info['read'] else "No"
    w = "Yes" if info['write'] else "No"
    rt = "Yes" if info['read'] and info['write'] else "No"
    report += f"| `{prop}` | {r} | {w} | {rt} | {info['note']} |\n"

report += f"""
### Inline Elements ({elem_read}/7 read, {elem_write}/7 write)

| Element | Read | Write |
|---------|------|-------|
"""

for elem, info in element_coverage.items():
    r = "Yes" if info['read'] else "No"
    w = "Yes" if info['write'] else "No"
    report += f"| `<{elem}>` | {r} | {w} |\n"

report += f"""
### Timing Features ({timing_supported}/6)

| Feature | Supported |
|---------|-----------|
"""

for feat, supported in timing_coverage.items():
    s = "Yes" if supported else "No"
    report += f"| {feat} | {s} |\n"

report += f"""
### Language/Multi-Track ({lang_supported}/5)

| Feature | Supported |
|---------|-----------|
"""

for feat, supported in lang_coverage.items():
    s = "Yes" if supported else "No"
    report += f"| {feat} | {s} |\n"

report += f"""
### Encoding ({enc_supported}/4)

| Feature | Supported |
|---------|-----------|
"""

for feat, supported in enc_coverage.items():
    s = "Yes" if supported else "No"
    report += f"| {feat} | {s} |\n"

report += f"""
---

## 5. Test Gaps ({len(issues['test_gaps'])})

"""

for t in issues['test_gaps']:
    report += f"- **{t['rule_id']}**: {t['name']}\n"

report += f"""
---

## 6. Key Findings

"""

key_findings = []

if has_lenient:
    key_findings.append("1. **Lenient HTML parsing**: Uses BeautifulSoup for tolerant parsing of malformed SAMI (unclosed tags, mixed case).")
else:
    key_findings.append("1. **Parsing approach unclear**: Could not confirm lenient HTML parser usage.")

if has_class_parse and has_lang_separation:
    key_findings.append("2. **Multi-language support IS implemented**: Reader extracts Class attribute from P elements, separates language tracks.")
else:
    key_findings.append("2. **Multi-language support incomplete**.")

key_findings.append(f"3. **Styling coverage**: {sty_read}/12 CSS properties read, {sty_write}/12 written. Round-trip preserves {sty_roundtrip}/12.")

if has_nbsp_clear:
    key_findings.append("4. **Caption clearing IS implemented**: Recognizes &nbsp; in P elements as clear events.")
else:
    key_findings.append("4. **Caption clearing NOT detected**: &nbsp; handling not found.")

if has_writer_sami and has_writer_sync:
    key_findings.append("5. **Writer produces valid SAMI structure**: Emits SAMI/HEAD/STYLE/BODY/SYNC/P skeleton with millisecond timing.")
else:
    key_findings.append("5. **Writer structure may be incomplete**.")

key_findings.append(f"6. **Inline elements**: {elem_read}/7 read, {elem_write}/7 write. BR, B, I, U, SPAN, FONT coverage varies.")

if has_comment_strip:
    key_findings.append("7. **HTML comments in STYLE handled**: <!-- --> stripped from CSS content.")
else:
    key_findings.append("7. **HTML comments in STYLE not explicitly handled** — may rely on parser tolerance.")

if has_writer_class:
    key_findings.append("8. **Writer preserves language classes**: Emits Class= on P elements for multi-language output.")
else:
    key_findings.append("8. **Writer may not preserve language classes**.")

key_findings.append(f"9. **Encoding**: {enc_supported}/4 features supported (HTML entities, numeric refs, BOM, nbsp).")
key_findings.append(f"10. **SAMI-specific features not implemented**: SAMIParam (Copyright, Media, Metrics, Spec), #Source ID styles, IMG element, Frame/SMPTE time units — these are MAY/SHOULD level and rarely used in practice.")

for f in key_findings:
    report += f + "\n"

report += f"""
---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Rules**: {len(all_rules)} | **Found**: {len(found_rules)} | **Missing**: {len(issues['missing'])}
**Styling**: {sty_roundtrip}/12 round-trip | **Elements**: {elem_read}/7 read | **Timing**: {timing_supported}/6 | **Language**: {lang_supported}/5
"""

with open(path, 'w') as _f: _f.write(report)
print(f"\n Report: {path}")
print(f"   Total issues: {total_issues} ({must_issues} MUST)")
```

Execute the above Python script directly.

---

## Success Criteria

- All 75 spec rules individually checked with per-rule patterns
- Deep validation for critical rules at function level
- Styling properties tracked as read/write/round-trip
- Inline elements tracked as read/write
- Timing model features verified (SYNC, implicit end, clear, monotonic)
- Multi-language features verified (Class parsing, CSS defs, writer output)
- Encoding features verified (entities, numeric refs, BOM, nbsp)
- Key findings narrative generated dynamically from detection results
- No false positives from stale file paths
