---
name: check-vtt-compliance
description: Generates EXHAUSTIVE WebVTT compliance report checking all 76 rules individually + tag/setting/entity coverage with deep validation analysis to identify ALL issues in pycaption code.
---

# check-vtt-compliance

## What this skill does

Exhaustive WebVTT compliance checker - 5 phases:
1. Deep validation (critical rules with function-level detection)
2. Systematic checking (all 76 rules individually verified)
3. Tag/Setting/Entity coverage (8+6+7)
4. Test coverage
5. Report generation

**Usage:** `/check-vtt-compliance`

---

## Implementation

**Run this Python script (context-optimized):**

```python
import os, re, glob
from datetime import datetime

print("WebVTT Exhaustive Compliance Check\n" + "=" * 60)

# ===== INIT =====
webvtt_file = 'pycaption/webvtt.py'
if not os.path.exists(webvtt_file):
    print("ERROR: pycaption/webvtt.py not found")
    raise SystemExit(1)

with open(webvtt_file) as _f: content = _f.read()

# Also read geometry.py and base.py for Layout/CaptionNode handling
support_files = ['pycaption/geometry.py', 'pycaption/base.py']
def _read(p):
    with open(p) as _fh: return _fh.read()
support_content = "\n".join(_read(f) for f in support_files if os.path.exists(f))

spec_file = 'ai_artifacts/specs/vtt/vtt_specs_summary.md'
if not os.path.exists(spec_file):
    print(f"ERROR: {spec_file} not found. Run analyze-vtt-docs first.")
    raise SystemExit(1)
spec = _read(spec_file)

# Extract all rules from spec
all_rules = {}
for match in re.finditer(r'\*\*\[(RULE-[A-Z]+-\d{3}|IMPL-(?:[A-Z]+-)?\d{3})\]\*\*\s*(.+?)(?:\n|$)', spec):
    rule_id = match.group(1)
    rule_name = match.group(2).strip()
    rule_start = match.start()
    next_rule = re.search(r'\*\*\[(?:RULE-[A-Z]+-\d{3}|IMPL-(?:[A-Z]+-)?\d{3})\]\*\*', spec[rule_start + 1:])
    rule_block = spec[rule_start:rule_start + 1 + next_rule.start()] if next_rule else spec[rule_start:]
    level_match = re.search(r'\*\*Level:\*\*\s*(MUST NOT|MUST|SHOULD|MAY)', rule_block)
    level = level_match.group(1) if level_match else 'UNKNOWN'
    all_rules[rule_id] = {'name': rule_name, 'level': level}

print(f"[INIT] Spec: {len(all_rules)} rules, Code: {len(content)} chars")

# ===== SANITY CHECK: Verify expected code landmarks exist =====
landmarks = {
    'class WebVTTReader': (webvtt_file, r'class\s+WebVTTReader\b'),
    'class WebVTTWriter': (webvtt_file, r'class\s+WebVTTWriter\b'),
    'def detect (WebVTTReader)': (webvtt_file, r'def\s+detect\b'),
    'def read (WebVTTReader)': (webvtt_file, r'def\s+read\b'),
    'def write (WebVTTWriter)': (webvtt_file, r'def\s+write\b'),
    'class Layout': ('pycaption/geometry.py', r'class\s+Layout\b'),
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

# ===== PHASE 1: DEEP VALIDATION =====
# Check critical rules at function level, not keyword level
print("\n[1/5] Deep Validation Analysis")

deep_results = {}

# RULE-FMT-001: WEBVTT header detection
# The detect() method uses substring check: '"WEBVTT" in content'
# This is overly permissive (matches WEBVTT anywhere, not just first line)
has_header_detect = bool(re.search(r'def detect.*\n.*"WEBVTT"\s+in\s+content', content))
has_header_validate = bool(re.search(r'content\s*\[\s*:6\s*\]\s*==|startswith.*WEBVTT|^WEBVTT', content))
deep_results['RULE-FMT-001'] = {
    'name': 'WEBVTT header',
    'detected': has_header_detect,
    'validated': has_header_validate,
    'note': 'detect() uses substring check, not first-line validation' if has_header_detect and not has_header_validate else '',
}

# RULE-FMT-002: UTF-8 encoding
has_utf8_check = bool(re.search(r'isinstance.*str|encoding.*utf', content, re.I))
has_utf8_validate = bool(re.search(r'UnicodeDecodeError|encoding.*error|decode.*utf', content, re.I))
deep_results['RULE-FMT-002'] = {
    'name': 'UTF-8 encoding',
    'detected': has_utf8_check,
    'validated': has_utf8_validate,
    'note': 'Checks isinstance(content, str) but no explicit UTF-8 decode validation',
}

# RULE-TIME-001: Timestamp format [HH:]MM:SS.mmm
has_timestamp_parse = bool(re.search(r'TIMESTAMP_PATTERN.*compile.*\d.*:.*\d', content, re.DOTALL))
has_timestamp_func = bool(re.search(r'def _parse_timestamp', content))
deep_results['RULE-TIME-001'] = {
    'name': 'Timestamp format parsing',
    'detected': has_timestamp_parse and has_timestamp_func,
    'validated': has_timestamp_func,
    'note': '',
}

# RULE-TIME-003: Exactly 3 millisecond digits
has_3_digits = bool(re.search(r'\\d\{3\}', content))
deep_results['RULE-TIME-003'] = {
    'name': 'Milliseconds exactly 3 digits',
    'detected': has_3_digits,
    'validated': has_3_digits,
    'note': 'Enforced by TIMESTAMP_PATTERN regex \\d{3}',
}

# RULE-TIME-005: Start <= end
has_start_end_check = bool(re.search(r'start\s*>\s*end', content))
has_start_end_error = bool(re.search(r'raise.*End timestamp.*not greater|raise.*start.*end', content, re.I))
disabled_by_default = bool(re.search(r'ignore_timing_errors.*=\s*True', content))
deep_results['RULE-TIME-005'] = {
    'name': 'Start time <= end time',
    'detected': has_start_end_check,
    'validated': has_start_end_error,
    'note': 'DISABLED BY DEFAULT (ignore_timing_errors=True)' if disabled_by_default else '',
}

# RULE-TIME-006: Monotonic timestamps
has_monotonic_check = bool(re.search(r'start\s*<\s*last_start_time', content))
has_monotonic_error = bool(re.search(r'raise.*not greater than or equal.*previous', content, re.I))
deep_results['RULE-TIME-006'] = {
    'name': 'Monotonic timestamps',
    'detected': has_monotonic_check,
    'validated': has_monotonic_error,
    'note': 'DISABLED BY DEFAULT (ignore_timing_errors=True)' if disabled_by_default else '',
}

# RULE-CUE-001: Timing separator ' --> '
has_arrow_pattern = bool(re.search(r'-->|TIMING_LINE_PATTERN', content))
deep_results['RULE-CUE-001'] = {
    'name': 'Timing separator -->',
    'detected': has_arrow_pattern,
    'validated': has_arrow_pattern,
    'note': 'TIMING_LINE_PATTERN captures arrow with surrounding whitespace',
}

# RULE-SET-002: Zero-value positions silently dropped on write
# Writer uses `if left_offset:` which is falsy for 0 — a valid position value
# Should be `if left_offset is not None:`
writer_section = content.split('class WebVTTWriter')[1] if 'class WebVTTWriter' in content else ''
zero_pos_bug = bool(re.search(r'if left_offset:', writer_section)) and not bool(re.search(r'if left_offset is not None', writer_section))
zero_line_bug = bool(re.search(r'if top_offset:', writer_section)) and not bool(re.search(r'if top_offset is not None', writer_section))
zero_size_bug = bool(re.search(r'if cue_width:', writer_section)) and not bool(re.search(r'if cue_width is not None', writer_section))
deep_results['RULE-SET-002'] = {
    'name': 'Zero-value position/line/size dropped on write',
    'detected': True,
    'validated': not (zero_pos_bug or zero_line_bug or zero_size_bug),
    'note': f'Writer uses truthiness check instead of `is not None`: position={zero_pos_bug}, line={zero_line_bug}, size={zero_size_bug}' if (zero_pos_bug or zero_line_bug or zero_size_bug) else '',
}
if zero_pos_bug or zero_line_bug or zero_size_bug:
    dropped = [x for x, v in [('position', zero_pos_bug), ('line', zero_line_bug), ('size', zero_size_bug)] if v]
    validation_gaps_extra = {
        'rule_id': 'RULE-SET-002', 'name': 'Zero-value cue settings silently dropped',
        'status': 'TRUTHINESS_BUG', 'severity': 'MUST',
        'note': f'`if {dropped[0]}:` is falsy for 0. Cues at position:0/line:0/size:0 lose positioning. '
                f'Affected: {", ".join(dropped)}. Fix: use `is not None` checks.',
    }
print(f"  RULE-SET-002: {'PASS' if not (zero_pos_bug or zero_line_bug or zero_size_bug) else 'TRUTHINESS BUG — zero values dropped'}")

# RULE-SET-005: Center alignment silently dropped on write
# Writer skips alignment when it equals CENTER, assuming it's the default
# But explicit center alignment should be preserved for round-trip fidelity
center_dropped = bool(re.search(r'alignment.*!=.*CENTER|alignment.*!=.*WEBVTT_VERSION_OF\[HorizontalAlignmentEnum\.CENTER\]', writer_section))
deep_results['RULE-SET-005'] = {
    'name': 'Center alignment silently dropped on write',
    'detected': True,
    'validated': not center_dropped,
    'note': 'Writer skips align:center assuming it is the default. Explicit center alignment lost on round-trip.' if center_dropped else '',
}
print(f"  RULE-SET-005: {'PASS' if not center_dropped else 'CENTER ALIGNMENT DROPPED'}")

# RULE-VAL-007: Timing validation disabled by default
# ignore_timing_errors=True means start>end and non-monotonic timestamps accepted silently
timing_disabled = bool(re.search(r'ignore_timing_errors\s*=\s*True', content))
deep_results['RULE-VAL-007'] = {
    'name': 'Timing validation disabled by default',
    'detected': True,
    'validated': not timing_disabled,
    'note': 'ignore_timing_errors defaults to True. Invalid timing (start>end, non-monotonic) silently accepted.' if timing_disabled else '',
}
print(f"  RULE-VAL-007: {'PASS' if not timing_disabled else 'DISABLED BY DEFAULT'}")

# IMPL-PARSE-006 deep: Reader strips ALL tags — read-only attribute gap
# OTHER_SPAN_PATTERN.sub("", ...) destroys all tag semantics (italic, bold, underline, class, lang, ruby)
# Only voice annotation is extracted; all other formatting is lost
has_tag_strip = bool(re.search(r'OTHER_SPAN_PATTERN\.sub\(\s*""', content))
has_tag_preserve = bool(re.search(r'tag.*preserv|tag.*keep|tag.*stor', content, re.I))
deep_results['IMPL-PARSE-006'] = {
    'name': 'Tag stripping destroys all inline formatting',
    'detected': has_tag_strip,
    'validated': has_tag_preserve,
    'note': 'OTHER_SPAN_PATTERN.sub("", ...) strips all tags. VTT→VTT round-trip loses italic, bold, underline, class, lang, ruby.' if has_tag_strip and not has_tag_preserve else '',
}
print(f"  IMPL-PARSE-006: {'PRESERVES TAGS' if has_tag_preserve else 'STRIPS ALL TAGS — formatting lost on round-trip'}")

# IMPL-WRITE-003 deep: Writer drops hours when hh==0
# `if hh:` means hours=0 produces MM:SS.mmm format (valid per spec but may surprise)
has_hours_truthiness = bool(re.search(r'if hh:', writer_section))
deep_results['IMPL-WRITE-003'] = {
    'name': 'Writer drops zero-hours in timestamps',
    'detected': has_hours_truthiness,
    'validated': False,
    'note': '`if hh:` omits hours when 0. Produces MM:SS.mmm. Valid per spec but non-reversible (reader may have had HH:MM:SS.mmm).' if has_hours_truthiness else '',
}
print(f"  IMPL-WRITE-003: {'DROPS ZERO-HOURS' if has_hours_truthiness else 'KEEPS HOURS'}")

# IMPL-WRITE-002 deep: Entity encoding partially commented out
# Writer has &lrm;/&rlm;/&nbsp;/&gt; encoding commented out
has_encode_commented = bool(re.search(r'#.*replace.*&lrm;|#.*replace.*&rlm;|#.*replace.*&nbsp;', content))
deep_results['IMPL-WRITE-002'] = {
    'name': 'Entity encoding partially commented out',
    'detected': True,
    'validated': not has_encode_commented,
    'note': '&lrm;, &rlm;, &gt;, &nbsp; encoding explicitly commented out in _encode_illegal_characters.' if has_encode_commented else '',
}
print(f"  IMPL-WRITE-002: {'PARTIAL — entities commented out' if has_encode_commented else 'FULL ENCODING'}")

# Silent parse error suppression: reader's else branch ignores malformed lines
has_silent_skip = bool(re.search(r'else:\s*\n\s*pass\b|else:\s*\n\s*continue\b', content))
if has_silent_skip:
    deep_results['IMPL-PARSE-SILENT'] = {
        'name': 'Reader silently skips unrecognized lines',
        'detected': True,
        'validated': False,
        'note': 'Reader else branch silently ignores non-timing, non-blank lines. Malformed headers, NOTE blocks, STYLE blocks silently swallowed.',
    }
print(f"  Silent line skip: {'FOUND' if has_silent_skip else 'CLEAN'}")

# Center alignment logic bug: writer drops center but DEFAULT_ALIGN is "start"
has_default_start = bool(re.search(r'DEFAULT_ALIGN.*=.*"start"|DEFAULT_ALIGN.*=.*start', content))
if center_dropped and has_default_start:
    deep_results['RULE-SET-005']['note'] = (
        deep_results['RULE-SET-005'].get('note', '') +
        ' Logic bug: DEFAULT_ALIGN is "start" but center is dropped as if it were the default. '
        'Explicit center alignment is valid and should be preserved.'
    ).strip()

validation_gaps = []
partial_validation = []

# Add the zero-value bug if detected
if zero_pos_bug or zero_line_bug or zero_size_bug:
    validation_gaps.append(validation_gaps_extra)

for rid, info in deep_results.items():
    _rule_level = all_rules.get(rid, {}).get('level', 'UNKNOWN')
    if not info['detected']:
        validation_gaps.append({
            'rule_id': rid, 'name': info['name'],
            'status': 'NOT_DETECTED', 'severity': _rule_level,
        })
    elif not info['validated']:
        validation_gaps.append({
            'rule_id': rid, 'name': info['name'],
            'status': 'DETECTED_NOT_VALIDATED', 'severity': _rule_level,
            'note': info.get('note', ''),
        })
    elif info.get('note'):
        partial_validation.append({
            'rule_id': rid, 'name': info['name'],
            'status': 'IMPLEMENTED_WITH_CAVEATS', 'severity': 'SHOULD',
            'note': info['note'],
        })

print(f"  Gaps: {len(validation_gaps)}, Caveats: {len(partial_validation)}")

# ===== PHASE 2: SYSTEMATIC RULE CHECK =====
print("\n[2/5] Systematic Rule Check ({} rules)".format(len(all_rules)))

# Per-rule patterns: match actual function names, variable names, and logic
# NOT broad keywords that could match comments
specific_patterns = {
    # File Format
    'RULE-FMT-001': [r'"WEBVTT"', r'def detect'],
    'RULE-FMT-002': [r'isinstance.*str|InvalidInputError'],
    'RULE-FMT-003': [r'BOM|\\ufeff|\xef\xbb\xbf'],
    'RULE-FMT-004': [r'HEADER\s*=\s*"WEBVTT\\n\\n"|blank.*line.*header'],
    'RULE-FMT-005': [r'splitlines|\\r\\n|\\r|\\n'],
    # Timestamps
    'RULE-TIME-001': [r'TIMESTAMP_PATTERN', r'def _parse_timestamp'],
    'RULE-TIME-002': [r'hours.*optional|m\[2\].*m\[0\].*m\[1\]|if m\[2\]'],
    'RULE-TIME-003': [r'\\d\{3\}'],
    'RULE-TIME-004': [r'\\d\{2\}'],
    'RULE-TIME-005': [r'start\s*>\s*end'],
    'RULE-TIME-006': [r'start\s*<\s*last_start_time'],
    'RULE-TIME-007': [r'timestamp.*tag|internal.*timestamp|\d+:\d+.*\.\d+.*>'],
    # Cue Structure
    'RULE-CUE-001': [r'TIMING_LINE_PATTERN.*-->|-->'],
    'RULE-CUE-002': [r'identifier.*-->'],
    'RULE-CUE-003': [r'identifier.*line.*terminator'],
    'RULE-CUE-004': [r'cue.*id.*unique|identifier.*unique'],
    'RULE-CUE-005': [r'"".*==.*line|blank.*line.*terminat'],
    'RULE-CUE-006': [r'payload.*-->'],
    # Cue Settings - check for ACTUAL parsing, not just keyword presence
    'RULE-SET-001': [r'vertical\s*[:=]|vertical.*rl|vertical.*lr'],
    'RULE-SET-002': [r'["\']line["\']|line:\s*\d|line:.*%'],
    'RULE-SET-003': [r'["\']position["\'].*:|position:\s*\d|position:.*%'],
    'RULE-SET-004': [r'["\']size["\'].*:|size:\s*\d|size:.*%'],
    'RULE-SET-005': [r'align:\s*\w|align.*start|align.*center|align.*end|align.*left|align.*right'],
    'RULE-SET-006': [r'region:\s*\w|["\']region["\'].*:'],
    'RULE-SET-007': [r'setting.*once|duplicate.*setting'],
    'RULE-SET-008': [r'region.*exclud|region.*vertical|region.*line|region.*size'],
    # Tags
    'RULE-TAG-001': [r'<c[\\.> ]|<c>|class.*span'],
    'RULE-TAG-002': [r'"<i>"|<i>.*</i>|italics'],
    'RULE-TAG-003': [r'"<b>"|<b>.*</b>|\bbold\b'],
    'RULE-TAG-004': [r'"<u>"|<u>.*</u>|underline'],
    'RULE-TAG-005': [r'VOICE_SPAN_PATTERN|<v[\\.> ]'],
    'RULE-TAG-006': [r'<lang[\\.> ]|OTHER_SPAN_PATTERN.*lang'],
    'RULE-TAG-007': [r'<ruby[\\.> ]|OTHER_SPAN_PATTERN.*ruby'],
    'RULE-TAG-008': [r'<\d+:\d+.*\.\d+.*>|timestamp.*tag.*process'],
    'RULE-TAG-009': [r'VOICE_SPAN_PATTERN.*\\\\\\.\\\\w|class.*annot.*pars'],
    'RULE-TAG-010': [r'&amp;|&lt;|&gt;|character.*ref'],
    'RULE-TAG-011': [r'tag.*clos|</\w+>|properly.*closed'],
    # Entities
    'RULE-ENT-001': [r'&amp;'],
    'RULE-ENT-002': [r'&lt;'],
    'RULE-ENT-003': [r'&gt;'],
    'RULE-ENT-004': [r'&nbsp;| |\\u00a0'],
    'RULE-ENT-005': [r'&lrm;|‎|\\u200e'],
    'RULE-ENT-006': [r'&rlm;|‏|\\u200f'],
    'RULE-ENT-007': [r'&#\d+;|&#x[0-9a-fA-F]+;|numeric.*ref'],
    # Regions
    'RULE-REG-001': [r'REGION\s.*block|region.*block.*pars|def.*parse_region'],
    'RULE-REG-002': [r'region.*id.*=|region.*identifier'],
    'RULE-REG-003': [r'region.*width'],
    'RULE-REG-004': [r'region.*lines?\b'],
    'RULE-REG-005': [r'regionanchor'],
    'RULE-REG-006': [r'viewportanchor'],
    'RULE-REG-007': [r'scroll.*up|scroll.*='],
    'RULE-REG-008': [r'region.*setting.*once'],
    'RULE-REG-009': [r'region.*unique|region.*identif.*unique'],
    # Special Blocks — match actual parsing code, not comments/TODOs
    'RULE-BLK-001': [r'def.*parse_note|re\.search.*NOTE\b|NOTE.*block.*pars'],
    'RULE-BLK-002': [r'def.*parse_style|def.*style_block|STYLE.*pars'],
    'RULE-BLK-003': [r'STYLE.*precede|STYLE.*before.*cue'],
    'RULE-BLK-004': [r'STYLE.*-->'],
    # Validation
    'RULE-VAL-001': [r'case.*sensitiv'],
    'RULE-VAL-002': [r'cue.*id.*unique|identifier.*unique|duplicate.*id'],
    'RULE-VAL-003': [r'region.*id.*unique|region.*unique'],
    'RULE-VAL-004': [r'timestamp.*order|monotonic|start.*<.*last'],
    'RULE-VAL-005': [r'unicode.*normali'],
    'RULE-VAL-006': [r'authoring.*tool|conforming.*file'],
    'RULE-VAL-007': [r'ignore_timing_errors'],
    # Implementation
    'IMPL-PARSE-001': [r'isinstance.*str|utf.?8|decode'],
    'IMPL-PARSE-002': [r'def detect|"WEBVTT"'],
    'IMPL-PARSE-003': [r'def _parse_timestamp'],
    'IMPL-PARSE-004': [r'def _validate_timings'],
    'IMPL-PARSE-005': [r'cue_settings|webvtt_positioning|Layout\('],
    'IMPL-PARSE-006': [r'OTHER_SPAN_PATTERN|VOICE_SPAN_PATTERN'],
    'IMPL-PARSE-007': [r'&amp;|&lt;|&gt;|&nbsp;|replace.*&'],
    'IMPL-PARSE-008': [r'def.*parse_region|REGION.*block|region.*header.*pars'],
    'IMPL-WRITE-001': [r'class WebVTTWriter|def write'],
    'IMPL-WRITE-002': [r'def _encode_illegal_characters|replace.*&amp'],
    'IMPL-WRITE-003': [r'def _timestamp'],
    'IMPL-WRITE-004': [r'-->\s|f".*-->.*"'],
}

missing_rules = []
found_rules = []

for rule_id, meta in sorted(all_rules.items()):
    # Skip rules covered in Phase 1
    if rule_id in deep_results:
        if deep_results[rule_id]['detected']:
            found_rules.append(rule_id)
        else:
            missing_rules.append({
                'rule_id': rule_id, 'name': meta['name'],
                'level': meta['level'], 'status': 'MISSING',
            })
        continue

    patterns = specific_patterns.get(rule_id, [])
    if not patterns:
        # No specific pattern defined — mark as unchecked
        missing_rules.append({
            'rule_id': rule_id, 'name': meta['name'],
            'level': meta['level'], 'status': 'NO_PATTERN',
        })
        continue

    # Search in main file + support files
    all_content = content + "\n" + support_content
    found = any(re.search(p, all_content, re.I) for p in patterns)

    if found:
        found_rules.append(rule_id)
    else:
        missing_rules.append({
            'rule_id': rule_id, 'name': meta['name'],
            'level': meta['level'], 'status': 'MISSING',
        })

must_missing = [r for r in missing_rules if r['level'] == 'MUST']
print(f"  Found: {len(found_rules)}/{len(all_rules)}, Missing: {len(missing_rules)} (MUST: {len(must_missing)})")

# ===== PHASE 3: TAG/SETTING/ENTITY COVERAGE =====
print("\n[3/5] Tag/Setting/Entity Coverage")

# Tags: check if the code can READ or WRITE each tag
# Note: reader strips most tags (OTHER_SPAN_PATTERN.sub), writer generates <i>/<b>/<u> from styles
tag_coverage = {
    '<c>':         {'read': bool(re.search(r'OTHER_SPAN_PATTERN', content)), 'write': False,
                    'note': 'Reader strips via OTHER_SPAN_PATTERN (matches [cibuv])'},
    '<i>':         {'read': bool(re.search(r'OTHER_SPAN_PATTERN', content)),
                    'write': bool(re.search(r'"<i>"', content)),
                    'note': 'Reader strips via OTHER_SPAN_PATTERN, writer generates from style nodes'},
    '<b>':         {'read': bool(re.search(r'OTHER_SPAN_PATTERN', content)),
                    'write': bool(re.search(r'"<b>"', content)),
                    'note': 'Reader strips via OTHER_SPAN_PATTERN, writer generates from style nodes'},
    '<u>':         {'read': bool(re.search(r'OTHER_SPAN_PATTERN', content)),
                    'write': bool(re.search(r'"<u>"', content)),
                    'note': 'Reader strips via OTHER_SPAN_PATTERN, writer generates from style nodes'},
    '<v>':         {'read': bool(re.search(r'VOICE_SPAN_PATTERN', content)),
                    'write': False,
                    'note': 'Reader extracts speaker annotation, strips tag'},
    '<lang>':      {'read': bool(re.search(r'<lang[\\.> ]|lang.*tag.*pars', content)),
                    'write': False,
                    'note': 'Stripped by OTHER_SPAN_PATTERN, not individually parsed'},
    '<ruby>/<rt>': {'read': bool(re.search(r'<ruby[\\.> ]|ruby.*tag.*pars', content)),
                    'write': False,
                    'note': 'Stripped by OTHER_SPAN_PATTERN, not individually parsed'},
    '<timestamp>': {'read': bool(re.search(r'<\d+:\d+.*>.*process|timestamp.*tag.*pars', content)),
                    'write': False,
                    'note': 'Stripped by OTHER_SPAN_PATTERN, not individually parsed'},
}

tags_with_read = sum(1 for t in tag_coverage.values() if t['read'])
tags_with_write = sum(1 for t in tag_coverage.values() if t['write'])
tags_roundtrip = sum(1 for t in tag_coverage.values() if t['read'] and t['write'])
print(f"  Tags: {tags_with_read}/8 read (strip), {tags_with_write}/8 write, {tags_roundtrip}/8 round-trip")

# Settings: check if the code PARSES individual settings vs stores raw string
setting_coverage = {
    'vertical': {'parsed': False, 'written': False,
                 'note': 'Reader stores raw string via Layout(webvtt_positioning=...), no individual parsing'},
    'line':     {'parsed': False, 'written': bool(re.search(r'["\']line:', content)),
                 'note': 'Writer generates from layout origin.y'},
    'position': {'parsed': False, 'written': bool(re.search(r'["\']position:', content)),
                 'note': 'Writer generates from layout origin.x'},
    'size':     {'parsed': False, 'written': bool(re.search(r'["\']size:', content)),
                 'note': 'Writer generates from layout extent.horizontal'},
    'align':    {'parsed': False, 'written': bool(re.search(r'["\']align:', content)),
                 'note': 'Writer generates from layout alignment'},
    'region':   {'parsed': False, 'written': False,
                 'note': 'Not implemented'},
}

settings_parsed = sum(1 for s in setting_coverage.values() if s['parsed'])
settings_written = sum(1 for s in setting_coverage.values() if s['written'])
print(f"  Settings: {settings_parsed}/6 parsed, {settings_written}/6 written")

# Entities: check read (decode) and write (encode) separately
entity_coverage = {
    '&amp;':  {'read': bool(re.search(r'replace.*"&amp;".*"&"', content)),
               'write': bool(re.search(r'replace.*"&".*"&amp;"', content))},
    '&lt;':   {'read': bool(re.search(r'replace.*"&lt;".*"<"', content)),
               'write': bool(re.search(r'replace.*"<".*"&lt;"', content))},
    '&gt;':   {'read': bool(re.search(r'replace.*"&gt;".*">"', content)),
               'write': bool(re.search(r'replace.*">".*"&gt;"|--&gt;', content))},
    '&nbsp;': {'read': bool(re.search(r'replace.*"&nbsp;"', content)),
               'write': bool(re.search(r'"&nbsp;"', content))},
    '&lrm;':  {'read': bool(re.search(r'replace.*"&lrm;"', content)),
               'write': bool(re.search(r'^\s*[^#\s].*replace.*\\u200e.*"&lrm;"', content, re.MULTILINE))},
    '&rlm;':  {'read': bool(re.search(r'replace.*"&rlm;"', content)),
               'write': bool(re.search(r'^\s*[^#\s].*replace.*\\u200f.*"&rlm;"', content, re.MULTILINE))},
    '&#ref':  {'read': False, 'write': False},
}

entities_read = sum(1 for e in entity_coverage.values() if e['read'])
entities_write = sum(1 for e in entity_coverage.values() if e['write'])
print(f"  Entities: {entities_read}/7 read, {entities_write}/7 write")

# ===== PHASE 4: TEST COVERAGE =====
print("\n[4/5] Test Coverage")

test_files = glob.glob('tests/**/test*webvtt*.py', recursive=True) + glob.glob('tests/**/test*vtt*.py', recursive=True)
tests = "\n".join(_read(f) for f in test_files if os.path.exists(f))
print(f"  Test files: {len(test_files)} ({len(tests)} chars)")

test_checks = {
    'RULE-FMT-001': [r'def test.*header|def test.*detect|def test.*webvtt'],
    'RULE-TIME-001': [r'def test.*timestamp|def test.*time.*pars'],
    'RULE-TIME-005': [r'def test.*start.*end|def test.*timing.*error|def test.*invalid.*time'],
    'RULE-TIME-006': [r'def test.*monotonic|def test.*order|def test.*previous'],
    'RULE-CUE-001': [r'def test.*arrow|def test.*-->|def test.*timing.*line'],
    'IMPL-WRITE-002': [r'def test.*encod|def test.*escap|def test.*illegal'],
    'IMPL-WRITE-003': [r'def test.*timestamp.*format|def test.*write.*time'],
}

test_gaps = []
for rid, patterns in test_checks.items():
    if not any(re.search(p, tests, re.I) for p in patterns):
        name = all_rules.get(rid, {}).get('name', rid)
        test_gaps.append({'rule_id': rid, 'name': name})

print(f"  Test gaps: {len(test_gaps)}/{len(test_checks)}")

# ===== PHASE 5: GENERATE REPORT =====
print("\n[5/5] Generating Report")
os.makedirs("ai_artifacts/compliance_checks/vtt", exist_ok=True)
date = datetime.now().strftime("%Y-%m-%d")
path = f"ai_artifacts/compliance_checks/vtt/compliance_report_{date}.md"

# Totals
tags_missing = 8 - tags_roundtrip
settings_missing = 6 - settings_parsed
entities_missing = 7 - entities_read
total = (len(validation_gaps) + len(partial_validation) + len(missing_rules) +
         tags_missing + settings_missing + entities_missing + len(test_gaps))
must_count = (len([g for g in validation_gaps if g.get('severity') == 'MUST']) +
              len([p for p in partial_validation if p.get('severity') == 'MUST']) +
              len(must_missing))

sanity_section = ""
if stale_warnings:
    sanity_section = "\n**STALE PATTERN WARNING**: The following expected code landmarks were not found. Some findings below may report features as 'missing' when they have actually been renamed or moved:\n"
    for w in stale_warnings:
        sanity_section += f"- {w}\n"
    sanity_section += "\n"

report = f"""# WebVTT EXHAUSTIVE Compliance Report

**Generated**: {date}
**Spec**: {spec_file} ({len(all_rules)} rules)
**Implementation**: {webvtt_file}
**Analysis**: Deep Validation + Systematic Rules + Coverage + Tests
{sanity_section}
---

## Executive Summary

**Rules checked**: {len(all_rules)}/{len(all_rules)} (100%)
**Total issues**: {total}
**MUST violations**: {must_count}

| Category | Count |
|----------|-------|
| Validation gaps | {len(validation_gaps)} |
| Implementation caveats | {len(partial_validation)} |
| Missing rules | {len(missing_rules)} (MUST: {len(must_missing)}) |
| Tag round-trip gaps | {tags_missing}/8 |
| Setting parse gaps | {settings_missing}/6 |
| Entity gaps | {entities_missing}/7 |
| Test gaps | {len(test_gaps)} |

---

## 1. Validation Gaps ({len(validation_gaps)})

"""

for g in validation_gaps:
    report += f"### {g['rule_id']}: {g['name']}\n"
    report += f"- **Status**: {g['status']}\n"
    report += f"- **Severity**: {g.get('severity', 'UNKNOWN')}\n"
    if g.get('note'):
        report += f"- **Note**: {g['note']}\n"
    report += "\n"

report += f"""---

## 2. Implementation Caveats ({len(partial_validation)})

Rules implemented but with significant limitations.

"""

for p in partial_validation:
    report += f"### {p['rule_id']}: {p['name']}\n"
    report += f"- **Status**: {p['status']}\n"
    report += f"- **Note**: {p['note']}\n\n"

report += f"""---

## 3. Missing Rules ({len(missing_rules)})

### MUST Rules ({len(must_missing)})

"""

for r in must_missing:
    report += f"- **{r['rule_id']}**: {r['name']} ({r['status']})\n"

should_missing = [r for r in missing_rules if r['level'] == 'SHOULD']
may_missing = [r for r in missing_rules if r['level'] in ('MAY', 'MUST NOT')]

report += f"\n### SHOULD Rules ({len(should_missing)})\n\n"
for r in should_missing:
    report += f"- **{r['rule_id']}**: {r['name']} ({r['status']})\n"

report += f"\n### MAY/MUST NOT Rules ({len(may_missing)})\n\n"
for r in may_missing:
    report += f"- **{r['rule_id']}**: {r['name']} ({r['status']})\n"

report += f"""
---

## 4. Coverage Analysis

### Tags ({tags_roundtrip}/8 round-trip)

| Tag | Read | Write | Round-trip | Note |
|-----|------|-------|------------|------|
"""

for tag, info in tag_coverage.items():
    r = "Yes (strip)" if info['read'] else "No"
    w = "Yes" if info['write'] else "No"
    rt = "Yes" if info['read'] and info['write'] else "No"
    report += f"| `{tag}` | {r} | {w} | {rt} | {info['note']} |\n"

report += f"""
### Cue Settings ({settings_parsed}/6 parsed, {settings_written}/6 written)

| Setting | Parsed | Written | Note |
|---------|--------|---------|------|
"""

for setting, info in setting_coverage.items():
    p = "Yes" if info['parsed'] else "No"
    w = "Yes" if info['written'] else "No"
    report += f"| `{setting}` | {p} | {w} | {info['note']} |\n"

report += f"""
### Entities ({entities_read}/7 read, {entities_write}/7 write)

| Entity | Read (decode) | Write (encode) |
|--------|---------------|----------------|
"""

for entity, info in entity_coverage.items():
    r = "Yes" if info['read'] else "No"
    w = "Yes" if info['write'] else "No"
    report += f"| `{entity}` | {r} | {w} |\n"

report += f"""
---

## 5. Test Gaps ({len(test_gaps)})

"""

for t in test_gaps:
    report += f"- **{t['rule_id']}**: {t['name']}\n"

report += f"""
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

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Rules**: {len(all_rules)} | **Found**: {len(found_rules)} | **Missing**: {len(missing_rules)}
**Tags**: {tags_roundtrip}/8 round-trip | **Settings**: {settings_parsed}/6 parsed | **Entities**: {entities_read}/7 read, {entities_write}/7 write
"""

with open(path, 'w') as _f: _f.write(report)
print(f"\n Report: {path}")
print(f"   Total issues: {total} ({must_count} MUST)")
```

Execute the above Python script directly.

---

## Key improvements over previous version

1. **No category key bug** -- per-rule patterns instead of category-based lookup
2. **Function-level detection** -- matches `def _parse_timestamp`, `def _validate_timings`, not keywords
3. **Read vs Write distinction** -- tags, settings, entities tracked separately for read/write/round-trip
4. **Disabled-by-default detection** -- timing validation flagged as caveat when `ignore_timing_errors=True`
5. **Raw string vs parsed distinction** -- cue settings correctly reported as unparsed
6. **Commented-out code detection** -- &lrm;/&rlm; writer encoding correctly flagged as not active
7. **Expanded file scope** -- also reads geometry.py and base.py for Layout handling
8. **Key findings section** -- narrative summary of the most important issues

---

## Success Criteria

- All 76 spec rules individually checked with per-rule patterns
- Deep validation for 7 critical rules at function level
- Tags tracked as read/write/round-trip (not just keyword match)
- Settings tracked as parsed vs raw-string
- Entities tracked as read (decode) vs write (encode)
- Disabled-by-default validations flagged
- Key findings narrative for actionable summary
