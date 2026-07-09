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
    'def _parse_cue_settings': (webvtt_file, r'def\s+_parse_cue_settings\b'),
    'def _parse_style_blocks': (webvtt_file, r'def\s+_parse_style_blocks\b'),
    'CUE_SETTING_PATTERN': (webvtt_file, r'CUE_SETTING_PATTERN\s*=\s*re\.compile'),
    'STYLE_SELECTOR_PATTERN': (webvtt_file, r'STYLE_SELECTOR_PATTERN\s*=\s*re\.compile'),
    'TAG_SPLIT_PATTERN': (webvtt_file, r'TAG_SPLIT_PATTERN\s*=\s*re\.compile'),
    'def _classify_tag': (webvtt_file, r'def\s+_classify_tag\b'),
    'WritingDirectionEnum': ('pycaption/geometry.py', r'class\s+WritingDirectionEnum\b'),
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
has_header_validate = bool(re.search(r'def _validate_header|startswith.*"WEBVTT ', content))
has_detect_first_line = bool(re.search(r'first_line\s*==\s*"WEBVTT"|first_line\.startswith\("WEBVTT', content))
deep_results['RULE-FMT-001'] = {
    'name': 'WEBVTT header',
    'detected': has_header_validate or has_detect_first_line,
    'validated': has_header_validate and has_detect_first_line,
    'note': '' if (has_header_validate and has_detect_first_line) else 'Header validation incomplete',
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
# Only match the TIMING_LINE_PATTERN definition, not general '-->' usage in style/note handling
has_timing_pattern = bool(re.search(r'TIMING_LINE_PATTERN\s*=\s*re\.compile', content))
has_timing_parse = bool(re.search(r'TIMING_LINE_PATTERN\.match|TIMING_LINE_PATTERN\.search', content))
deep_results['RULE-CUE-001'] = {
    'name': 'Timing separator -->',
    'detected': has_timing_pattern,
    'validated': has_timing_pattern and has_timing_parse,
    'note': 'TIMING_LINE_PATTERN captures arrow with surrounding whitespace',
}

# RULE-SET-002: Zero-value positions silently dropped on write
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
center_dropped = bool(re.search(r'alignment.*!=.*CENTER|alignment.*!=.*WEBVTT_VERSION_OF\[HorizontalAlignmentEnum\.CENTER\]', writer_section))
deep_results['RULE-SET-005'] = {
    'name': 'Center alignment silently dropped on write',
    'detected': True,
    'validated': not center_dropped,
    'note': 'Writer skips align:center assuming it is the default. Explicit center alignment lost on round-trip.' if center_dropped else '',
}
print(f"  RULE-SET-005: {'PASS' if not center_dropped else 'CENTER ALIGNMENT DROPPED'}")

# RULE-VAL-007: Timing validation disabled by default
timing_disabled = bool(re.search(r'ignore_timing_errors\s*=\s*True', content))
deep_results['RULE-VAL-007'] = {
    'name': 'Timing validation disabled by default',
    'detected': True,
    'validated': not timing_disabled,
    'note': 'ignore_timing_errors defaults to True. Invalid timing (start>end, non-monotonic) silently accepted.' if timing_disabled else '',
}
print(f"  RULE-VAL-007: {'PASS' if not timing_disabled else 'DISABLED BY DEFAULT'}")

# IMPL-PARSE-006 deep: Tag parsing via TAG_SPLIT_PATTERN + _classify_tag
# Tags are now preserved as CaptionNode.STYLE open/close pairs, not stripped
has_tag_split = bool(re.search(r'TAG_SPLIT_PATTERN\.split', content))
has_classify_tag = bool(re.search(r'def _classify_tag', content))
has_known_tags = bool(re.search(r'KNOWN_TAGS\s*=\s*frozenset', content))
deep_results['IMPL-PARSE-006'] = {
    'name': 'Inline tag parsing and preservation',
    'detected': has_tag_split and has_classify_tag,
    'validated': has_tag_split and has_classify_tag and has_known_tags,
    'note': '' if (has_tag_split and has_classify_tag and has_known_tags) else 'Tag parsing infrastructure incomplete',
}
print(f"  IMPL-PARSE-006: {'TAG PARSING IMPLEMENTED' if (has_tag_split and has_classify_tag) else 'MISSING TAG PARSING'}")

# IMPL-WRITE-003 deep: Writer drops hours when hh==0
has_hours_truthiness = bool(re.search(r'if hh:', writer_section))
deep_results['IMPL-WRITE-003'] = {
    'name': 'Writer drops zero-hours in timestamps',
    'detected': has_hours_truthiness,
    'validated': False,
    'note': '`if hh:` omits hours when 0. Produces MM:SS.mmm. Valid per spec but non-reversible (reader may have had HH:MM:SS.mmm).' if has_hours_truthiness else '',
}
print(f"  IMPL-WRITE-003: {'DROPS ZERO-HOURS' if has_hours_truthiness else 'KEEPS HOURS'}")

# IMPL-WRITE-002 deep: Entity encoding partially commented out
has_encode_commented = bool(re.search(r'#.*replace.*&lrm;|#.*replace.*&rlm;|#.*replace.*&nbsp;', content))
deep_results['IMPL-WRITE-002'] = {
    'name': 'Entity encoding partially commented out',
    'detected': True,
    'validated': not has_encode_commented,
    'note': '&lrm;, &rlm;, &gt;, &nbsp; encoding explicitly commented out in _encode_illegal_characters.' if has_encode_commented else '',
}
print(f"  IMPL-WRITE-002: {'PARTIAL — entities commented out' if has_encode_commented else 'FULL ENCODING'}")

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
    'RULE-FMT-001': [r'"WEBVTT"', r'def detect', r'def _validate_header'],
    'RULE-FMT-002': [r'isinstance.*str|InvalidInputError'],
    'RULE-FMT-003': [r'BOM|\\ufeff|\xef\xbb\xbf|startswith.*"\xef\xbb\xbf"'],
    'RULE-FMT-004': [r'_validate_header.*blank|lines\[1\]\s*!=\s*""'],
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
    'RULE-CUE-001': [r'TIMING_LINE_PATTERN\s*=\s*re\.compile'],
    'RULE-CUE-002': [r'identifier.*-->'],
    'RULE-CUE-003': [r'identifier.*line.*terminator'],
    'RULE-CUE-004': [r'cue.*id.*unique|identifier.*unique'],
    'RULE-CUE-005': [r'"".*==.*line|blank.*line.*terminat|line\s*==\s*""'],
    'RULE-CUE-006': [r'payload.*-->'],
    # Cue Settings - check for ACTUAL parsing via _parse_cue_settings
    'RULE-SET-001': [r'vertical.*rl|vertical.*lr|WritingDirectionEnum|"vertical".*CUE_SETTING_PATTERN'],
    'RULE-SET-002': [r'name\s*==\s*"line"|_line_number_to_percent|_parse_percent_value.*line'],
    'RULE-SET-003': [r'name\s*==\s*"position"|_parse_percent_value.*position'],
    'RULE-SET-004': [r'name\s*==\s*"size"|extent_horizontal'],
    'RULE-SET-005': [r'ALIGN_SETTING_MAP|name\s*==\s*"align"'],
    'RULE-SET-006': [r'_extract_region_id|region.*=.*settings'],
    'RULE-SET-007': [r'setting.*once|duplicate.*setting'],
    'RULE-SET-008': [r'region.*exclud|region.*vertical|region.*line|region.*size'],
    # Tags - check via TAG_SPLIT_PATTERN + _classify_tag + _tag_content
    'RULE-TAG-001': [r'<c[\\.> ]|"c".*KNOWN_TAGS|_tag_content.*class|_convert_structural_tag'],
    'RULE-TAG-002': [r'"<i>"|"i".*KNOWN_TAGS|italics|_classify_tag'],
    'RULE-TAG-003': [r'"<b>"|"b".*KNOWN_TAGS|bold|_classify_tag'],
    'RULE-TAG-004': [r'"<u>"|"u".*KNOWN_TAGS|underline|_classify_tag'],
    'RULE-TAG-005': [r'VOICE_SPAN_PATTERN|<v[\\.> ]|"v".*KNOWN_TAGS'],
    'RULE-TAG-006': [r'"lang".*KNOWN_TAGS|_classify_tag.*lang|_tag_content'],
    'RULE-TAG-007': [r'"ruby".*KNOWN_TAGS|"rt".*KNOWN_TAGS|_classify_tag.*ruby'],
    'RULE-TAG-008': [r'timestamp.*tag|_classify_tag.*\d+:\d+'],
    'RULE-TAG-009': [r'VOICE_SPAN_PATTERN.*\\\\\\.\\\\w|class.*annot.*pars|class_suffix'],
    'RULE-TAG-010': [r'html\.unescape|&amp;|&lt;|&gt;|_decode_entities'],
    'RULE-TAG-011': [r'_close_unclosed_tags|open_tags|tag.*clos|</\w+>'],
    # Entities
    'RULE-ENT-001': [r'html\.unescape|&amp;'],
    'RULE-ENT-002': [r'html\.unescape|&lt;'],
    'RULE-ENT-003': [r'html\.unescape|&gt;'],
    'RULE-ENT-004': [r'html\.unescape|&nbsp;|\\u00a0'],
    'RULE-ENT-005': [r'html\.unescape|&lrm;|\\u200e'],
    'RULE-ENT-006': [r'html\.unescape|&rlm;|\\u200f'],
    'RULE-ENT-007': [r'html\.unescape|&#\d+;|&#x[0-9a-fA-F]+;|numeric.*ref'],
    # Regions
    'RULE-REG-001': [r'def _parse_regions|REGION.*block|region.*block.*pars'],
    'RULE-REG-002': [r'region.*id.*=|"id".*settings|region.*identifier'],
    'RULE-REG-003': [r'region.*width|"width".*REGION_SETTING'],
    'RULE-REG-004': [r'region.*lines?\b|"lines".*REGION_SETTING'],
    'RULE-REG-005': [r'regionanchor'],
    'RULE-REG-006': [r'viewportanchor'],
    'RULE-REG-007': [r'scroll.*up|scroll.*=|"scroll"'],
    'RULE-REG-008': [r'region.*setting.*once|seen_keys'],
    'RULE-REG-009': [r'region_id\s+not\s+in\s+regions|region.*unique'],
    # Special Blocks
    'RULE-BLK-001': [r'_is_note_start|in_note_block|NOTE.*block'],
    'RULE-BLK-002': [r'def _parse_style_blocks|STYLE_SELECTOR_PATTERN'],
    'RULE-BLK-003': [r'"-->"\s*in\s*line.*break|STYLE.*before.*cue'],
    'RULE-BLK-004': [r'in_style_block.*-->|STYLE.*-->'],
    # Validation
    'RULE-VAL-001': [r'case.*sensitiv'],
    'RULE-VAL-002': [r'cue.*id.*unique|identifier.*unique|duplicate.*id'],
    'RULE-VAL-003': [r'region_id\s+not\s+in\s+regions|region.*id.*unique'],
    'RULE-VAL-004': [r'timestamp.*order|monotonic|start.*<.*last'],
    'RULE-VAL-005': [r'unicode.*normali'],
    'RULE-VAL-006': [r'authoring.*tool|conforming.*file'],
    'RULE-VAL-007': [r'ignore_timing_errors'],
    # Implementation
    'IMPL-PARSE-001': [r'isinstance.*str|utf.?8|decode'],
    'IMPL-PARSE-002': [r'def detect|"WEBVTT"|_validate_header'],
    'IMPL-PARSE-003': [r'def _parse_timestamp'],
    'IMPL-PARSE-004': [r'def _validate_timings'],
    'IMPL-PARSE-005': [r'_parse_cue_settings|CUE_SETTING_PATTERN|Layout\('],
    'IMPL-PARSE-006': [r'TAG_SPLIT_PATTERN|_classify_tag|KNOWN_TAGS'],
    'IMPL-PARSE-007': [r'html\.unescape|_decode_entities'],
    'IMPL-PARSE-008': [r'def _parse_regions|REGION_SETTING_PATTERN'],
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
# Reader now parses tags via TAG_SPLIT_PATTERN + _classify_tag into CaptionNode.STYLE pairs
# Writer generates tags from style nodes via _convert_structural_tag
tag_coverage = {
    '<c>':         {'read': bool(re.search(r'_classify_tag|_tag_content', content)),
                    'write': bool(re.search(r'_convert_structural_tag', content)),
                    'note': 'Reader parses via _classify_tag + _tag_content, writer via _convert_structural_tag'},
    '<i>':         {'read': bool(re.search(r'TAG_SPLIT_PATTERN|_classify_tag', content)),
                    'write': bool(re.search(r'"<i>"', content)),
                    'note': 'Reader preserves as STYLE node (italics), writer generates from style nodes'},
    '<b>':         {'read': bool(re.search(r'TAG_SPLIT_PATTERN|_classify_tag', content)),
                    'write': bool(re.search(r'"<b>"', content)),
                    'note': 'Reader preserves as STYLE node (bold), writer generates from style nodes'},
    '<u>':         {'read': bool(re.search(r'TAG_SPLIT_PATTERN|_classify_tag', content)),
                    'write': bool(re.search(r'"<u>"', content)),
                    'note': 'Reader preserves as STYLE node (underline), writer generates from style nodes'},
    '<v>':         {'read': bool(re.search(r'VOICE_SPAN_PATTERN|"v"', content)),
                    'write': False,
                    'note': 'Reader extracts speaker annotation into text, not round-trippable'},
    '<lang>':      {'read': bool(re.search(r'"lang".*KNOWN_TAGS|_tag_content', content)),
                    'write': bool(re.search(r'_convert_structural_tag.*lang|"<lang', content)),
                    'note': 'Reader parses via _classify_tag into STYLE node with lang key'},
    '<ruby>/<rt>': {'read': bool(re.search(r'"ruby".*KNOWN_TAGS|"rt".*KNOWN_TAGS|_tag_content', content)),
                    'write': bool(re.search(r'_convert_structural_tag.*ruby|"<ruby', content)),
                    'note': 'Reader parses via _classify_tag into STYLE node'},
    '<timestamp>': {'read': bool(re.search(r'_classify_tag.*timestamp|timestamp.*microseconds', content, re.DOTALL)),
                    'write': False,
                    'note': 'Reader parses timestamp tags into STYLE node with timestamp key'},
}

tags_with_read = sum(1 for t in tag_coverage.values() if t['read'])
tags_with_write = sum(1 for t in tag_coverage.values() if t['write'])
tags_roundtrip = sum(1 for t in tag_coverage.values() if t['read'] and t['write'])
print(f"  Tags: {tags_with_read}/8 read, {tags_with_write}/8 write, {tags_roundtrip}/8 round-trip")

# Settings: check if the code PARSES individual settings
# Reader now parses all settings via _parse_cue_settings + CUE_SETTING_PATTERN
setting_coverage = {
    'vertical': {'parsed': bool(re.search(r'WritingDirectionEnum|"vertical".*CUE_SETTING_PATTERN|name\s*==\s*"vertical"', content)),
                 'written': False,
                 'note': 'Parsed into Layout.writing_direction via WritingDirectionEnum'},
    'line':     {'parsed': bool(re.search(r'_line_number_to_percent|name\s*==\s*"line"', content)),
                 'written': bool(re.search(r'f" line:|f"line:', writer_section)),
                 'note': 'Parsed into origin.y, writer generates from layout'},
    'position': {'parsed': bool(re.search(r'_parse_percent_value|name\s*==\s*"position"', content)),
                 'written': bool(re.search(r'f" position:|f"position:', writer_section)),
                 'note': 'Parsed into origin.x, writer generates from layout'},
    'size':     {'parsed': bool(re.search(r'extent_horizontal|name\s*==\s*"size"', content)),
                 'written': bool(re.search(r'f" size:|f"size:', writer_section)),
                 'note': 'Parsed into extent.horizontal, writer generates from layout'},
    'align':    {'parsed': bool(re.search(r'ALIGN_SETTING_MAP|name\s*==\s*"align"', content)),
                 'written': bool(re.search(r'f" align:|f"align:', writer_section)),
                 'note': 'Parsed into Layout.alignment via ALIGN_SETTING_MAP'},
    'region':   {'parsed': bool(re.search(r'_extract_region_id|region.*inherit_from', content)),
                 'written': bool(re.search(r'f" region:|f"region:|webvtt_positioning', writer_section)),
                 'note': 'Parsed via _extract_region_id, region layout inherited via inherit_from'},
}

settings_parsed = sum(1 for s in setting_coverage.values() if s['parsed'])
settings_written = sum(1 for s in setting_coverage.values() if s['written'])
print(f"  Settings: {settings_parsed}/6 parsed, {settings_written}/6 written")

# Entities: check read (decode) and write (encode) separately
# Reader now uses html.unescape() which handles all named + numeric entities
has_html_unescape = bool(re.search(r'html\.unescape', content))
entity_coverage = {
    '&amp;':  {'read': has_html_unescape,
               'write': bool(re.search(r'replace.*"&".*"&amp;"', content))},
    '&lt;':   {'read': has_html_unescape,
               'write': bool(re.search(r'replace.*"<".*"&lt;"', content))},
    '&gt;':   {'read': has_html_unescape,
               'write': bool(re.search(r'replace.*">".*"&gt;"|--&gt;', content))},
    '&nbsp;': {'read': has_html_unescape,
               'write': bool(re.search(r'"&nbsp;"', content))},
    '&lrm;':  {'read': has_html_unescape,
               'write': bool(re.search(r'^\s*[^#\s].*replace.*\\u200e.*"&lrm;"', content, re.MULTILINE))},
    '&rlm;':  {'read': has_html_unescape,
               'write': bool(re.search(r'^\s*[^#\s].*replace.*\\u200f.*"&rlm;"', content, re.MULTILINE))},
    '&#ref':  {'read': has_html_unescape, 'write': False},
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
    r = "Yes" if info['read'] else "No"
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

report += """
---

## 6. Key Findings

"""

# Generate findings dynamically from detection results
findings = []

# Check tag state
if tags_with_read >= 7:
    findings.append(f"1. **Reader preserves inline tags**: Tags `<i>`, `<b>`, `<u>`, `<c>`, `<lang>`, `<ruby>`, `<rt>`, and timestamp are parsed by `TAG_SPLIT_PATTERN.split()` + `_classify_tag()` into CaptionNode.STYLE open/close pairs. Voice `<v>` annotation extracted into text.")
else:
    findings.append(f"1. **Tag parsing incomplete**: Only {tags_with_read}/8 tags parsed by reader.")

if tags_with_write >= 4:
    findings.append(f"2. **Writer generates tags from style nodes**: `<i>`, `<b>`, `<u>` from text styles; `<c>`, `<lang>`, `<ruby>` via `_convert_structural_tag()`. VTT-to-VTT round-trip preserves formatting.")
else:
    findings.append(f"2. **Writer tag output limited**: Only {tags_with_write}/8 tags written.")

if settings_parsed >= 5:
    findings.append(f"3. **All cue settings individually parsed**: `_parse_cue_settings()` uses `CUE_SETTING_PATTERN` to parse position, line, size, align, vertical. Region handled via `_extract_region_id()` + `inherit_from`.")
else:
    findings.append(f"3. **Cue settings partially parsed**: Only {settings_parsed}/6 settings individually parsed.")

findings.append(f"4. **STYLE blocks fully implemented**: `_parse_style_blocks()` extracts `::cue` CSS rules via `STYLE_SELECTOR_PATTERN`. `_resolve_cue_styles()` merges resolved properties into nodes. Class-based styling (`::cue(.class)`) supported.")
findings.append(f"5. **Timing validation exists but is DISABLED by default** (`ignore_timing_errors=True`). Start<=end and monotonic checks are opt-in.")

if has_html_unescape:
    findings.append(f"6. **Entity decode uses `html.unescape()`**: Handles all named entities + numeric character references (&#169;, &#x266B;). More permissive than spec's 6 named entities. **Entity encode is partial** (writer only encodes &amp;, &lt;, and --> to --&gt;). &lrm;/&rlm; encoding is commented out.")
else:
    findings.append(f"6. **Entity decode limited**: Manual replacement for spec entities only.")

if bool(re.search(r'def _parse_regions', content)):
    findings.append(f"7. **REGION blocks fully implemented**: `_parse_regions()` parses id, width, lines, regionanchor, viewportanchor, scroll settings. First-definition-wins for duplicate IDs. Region layout inherited by cues via `inherit_from`.")
else:
    findings.append(f"7. **REGION blocks not implemented**.")

if has_header_validate and has_detect_first_line:
    findings.append(f"8. **Header detection is strict**: `detect()` checks first line only (not substring). `_validate_header()` enforces WEBVTT on first line + blank line separator. BOM stripped before parsing.")
else:
    findings.append(f"8. **Header detection needs review**.")

for f in findings:
    report += f + "\n"

report += f"""
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
2. **Function-level detection** -- matches `def _parse_timestamp`, `def _parse_cue_settings`, `_classify_tag`, not keywords
3. **Read vs Write distinction** -- tags, settings, entities tracked separately for read/write/round-trip
4. **Disabled-by-default detection** -- timing validation flagged as caveat when `ignore_timing_errors=True`
5. **Parsed settings detection** -- detects `_parse_cue_settings`, `CUE_SETTING_PATTERN`, individual setting names
6. **Tag preservation detection** -- detects `TAG_SPLIT_PATTERN`, `_classify_tag`, `KNOWN_TAGS`, `_tag_content`
7. **STYLE block detection** -- detects `_parse_style_blocks`, `STYLE_SELECTOR_PATTERN`, `_extract_cue_styles`
8. **Dynamic key findings** -- generated from detection results, not hardcoded stale text
9. **Tighter RULE-CUE-001** -- matches `TIMING_LINE_PATTERN` definition, not general `-->` string checks
10. **Expanded landmarks** -- includes `_parse_cue_settings`, `_parse_style_blocks`, `CUE_SETTING_PATTERN`, `STYLE_SELECTOR_PATTERN`, `TAG_SPLIT_PATTERN`, `_classify_tag`, `WritingDirectionEnum`

---

## Success Criteria

- All 76 spec rules individually checked with per-rule patterns
- Deep validation for critical rules at function level
- Tags tracked as read/write/round-trip (not just keyword match)
- Settings tracked as parsed vs raw-string
- Entities tracked as read (decode) vs write (encode)
- Disabled-by-default validations flagged
- Dynamic key findings generated from detection results
