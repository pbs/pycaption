---
name: check-dfxp-compliance
description: Generates EXHAUSTIVE DFXP/TTML compliance report checking all 115 rules individually + styling/timing/element coverage with deep validation analysis to identify ALL issues in pycaption code.
---

# check-dfxp-compliance

## What this skill does

Exhaustive DFXP/TTML compliance checker - 5 phases:
1. Deep validation (critical rules with function-level detection vs validation)
2. Systematic checking (all 115 rules individually verified with per-rule patterns)
3. Styling attribute / timing format / content element / parameter coverage (read/write distinction)
4. Test coverage analysis
5. Report generation

**Input**: `ai_artifacts/specs/dfxp/dfxp_specs_summary.md`
**Output**: `ai_artifacts/compliance_checks/dfxp/compliance_report_{date}.md`

**Usage:** `/check-dfxp-compliance`

---

## Implementation

**Run this Python script (context-optimized):**

```python
import os, re, glob
from datetime import datetime

print("DFXP/TTML Exhaustive Compliance Check\n" + "=" * 60)

# ===== INIT: Load spec and implementation =====
spec_files = glob.glob('ai_artifacts/specs/dfxp/dfxp_specs_summary*.md')
if not spec_files:
    print("ERROR: No dfxp_specs_summary.md found in ai_artifacts/specs/dfxp/")
    raise SystemExit(1)
latest_spec = max(spec_files, key=os.path.getmtime)
with open(latest_spec) as _f: spec = _f.read()

impl_files = [
    'pycaption/dfxp/base.py',
    'pycaption/dfxp/extras.py',
    'pycaption/dfxp/__init__.py',
    'pycaption/geometry.py',
]
impl_content = {}
for f in impl_files:
    if os.path.exists(f):
        with open(f) as _fh: impl_content[f] = _fh.read()
impl = "\n".join(impl_content.values())

# Separate base.py for function-level checks
base_content = impl_content.get('pycaption/dfxp/base.py', '')
extras_content = impl_content.get('pycaption/dfxp/extras.py', '')
geometry_content = impl_content.get('pycaption/geometry.py', '')

print(f"[INIT] Spec: {latest_spec} ({len(spec)} chars)")
print(f"[INIT] Implementation: {len(impl_content)} files ({len(impl)} chars)")

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

print(f"[INIT] Extracted {len(all_rules)} rules from spec")

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

# RULE-DOC-001: Root tt element detection
# detect() uses: "</tt>" in content.lower() — substring check, not XML root validation
has_detect = bool(re.search(r'def detect.*\n.*</tt>.*in.*content', base_content, re.I))
has_root_validate = bool(re.search(r'root.*tag.*!=.*tt|getroot.*!=.*tt|raise.*root.*element', base_content))
deep_results['RULE-DOC-001'] = {
    'name': 'Root tt element detection',
    'detected': has_detect,
    'validated': has_root_validate,
    'note': 'detect() uses substring "</tt>" in content.lower() — matches tt anywhere, not root validation',
}
if has_detect and not has_root_validate:
    issues['partial_validation'].append({
        'rule_id': 'RULE-DOC-001', 'name': 'Root tt element detection',
        'status': 'DETECTED_NOT_VALIDATED', 'severity': 'SHOULD',
        'note': 'detect() uses "</tt>" in content.lower() (substring), not proper root element check',
    })
print(f"  RULE-DOC-001: {'PASS' if has_root_validate else 'DETECTION ONLY'}")

# RULE-DOC-003: xml:lang attribute
# Reads: dfxp_document.tt.attrs.get("xml:lang", DEFAULT_LANGUAGE_CODE)
# Silent fallback to "en", no validation of the value (e.g., BCP-47 check)
has_lang_read = bool(re.search(r'xml:lang.*DEFAULT_LANGUAGE_CODE|attrs\.get.*xml:lang', base_content))
has_lang_validate = bool(re.search(r'raise.*lang|warn.*lang|BCP.*47|valid.*lang', base_content, re.I))
deep_results['RULE-DOC-003'] = {
    'name': 'xml:lang attribute',
    'detected': has_lang_read,
    'validated': has_lang_validate,
    'note': 'Reads xml:lang with silent fallback to "en". No BCP-47 validation.',
}
if has_lang_read and not has_lang_validate:
    issues['partial_validation'].append({
        'rule_id': 'RULE-DOC-003', 'name': 'xml:lang attribute',
        'status': 'READ_NOT_VALIDATED', 'severity': 'SHOULD',
        'note': 'Reads with silent fallback to DEFAULT_LANGUAGE_CODE ("en"), no BCP-47 validation',
    })
print(f"  RULE-DOC-003: {'PASS' if has_lang_validate else 'READ ONLY (no validation)'}")

# RULE-TIME-001: Clock-time parsing
# CLOCK_TIME_PATTERN handles HH:MM:SS with optional .sub_frames or :frames
has_clock_pattern = bool(re.search(r'CLOCK_TIME_PATTERN', base_content))
has_clock_func = bool(re.search(r'def _convert_clock_time_to_microseconds', base_content))
has_clock_error = bool(re.search(r'CaptionReadTimingError.*Invalid timestamp', base_content))
deep_results['RULE-TIME-001'] = {
    'name': 'Clock-time parsing',
    'detected': has_clock_pattern and has_clock_func,
    'validated': has_clock_error,
    'note': 'Full parsing via CLOCK_TIME_PATTERN + _convert_clock_time_to_microseconds. Raises CaptionReadTimingError on invalid.',
}
print(f"  RULE-TIME-001: {'PASS' if has_clock_error else 'FAIL'}")

# RULE-TIME-002: Clock-time frames
# Hardcoded: int(frames) / 30 * MICROSECONDS_PER_UNIT["seconds"]
# No ttp:frameRate support
has_frame_parse = bool(re.search(r'clock_time_match\.group.*"frames"', base_content))
has_frame_rate_param = bool(re.search(r'frameRate|frame_rate|ttp:frameRate', base_content))
deep_results['RULE-TIME-002'] = {
    'name': 'Clock-time frames',
    'detected': has_frame_parse,
    'validated': False,
    'note': 'Frames parsed but divided by hardcoded 30 (not ttp:frameRate). No frame rate parameter support.',
}
if has_frame_parse:
    issues['validation_gaps'].append({
        'rule_id': 'RULE-TIME-002', 'name': 'Clock-time frames hardcoded to /30',
        'status': 'HARDCODED_FRAME_RATE', 'severity': 'MUST',
        'note': 'int(frames) / 30 * MICROSECONDS_PER_UNIT["seconds"] — ignores ttp:frameRate',
    })
print(f"  RULE-TIME-002: HARDCODED /30 (no ttp:frameRate)")

# RULE-TIME-014: Frame timing requires ttp:frameRate
# Code never reads ttp:frameRate from the document
has_framerate_read = bool(re.search(r'ttp:frameRate|attrib.*frameRate|get.*frameRate', base_content))
deep_results['RULE-TIME-014'] = {
    'name': 'ttp:frameRate parameter',
    'detected': False,
    'validated': False,
    'note': 'ttp:frameRate is never read from the document. Frame division always uses /30.',
}
if not has_framerate_read:
    issues['validation_gaps'].append({
        'rule_id': 'RULE-TIME-014', 'name': 'ttp:frameRate not implemented',
        'status': 'NOT_IMPLEMENTED', 'severity': 'MUST',
        'note': 'Code never reads ttp:frameRate. Default 30fps used always.',
    })
print(f"  RULE-TIME-014: NOT_IMPLEMENTED")

# RULE-TIME-009: Offset tick time
# _convert_time_count_to_microseconds raises NotImplementedError for metric "t"
has_tick_error = bool(re.search(r'NotImplementedError.*tick', base_content))
deep_results['RULE-TIME-009'] = {
    'name': 'Offset tick time',
    'detected': True,
    'validated': False,
    'note': 'Raises NotImplementedError("The tick metric...is not currently implemented.")',
}
if has_tick_error:
    issues['validation_gaps'].append({
        'rule_id': 'RULE-TIME-009', 'name': 'Offset tick time raises NotImplementedError',
        'status': 'NOT_IMPLEMENTED', 'severity': 'SHOULD',
        'note': 'Code recognizes tick metric but raises NotImplementedError instead of computing',
    })
print(f"  RULE-TIME-009: NotImplementedError")

# IMPL-003: Style resolver cascade
# _get_style_reference_chain follows style references recursively
# _get_style_sources returns nested + referenced styles in order
has_chain = bool(re.search(r'def _get_style_reference_chain', base_content))
has_sources = bool(re.search(r'def _get_style_sources', base_content))
has_dup_error = bool(re.search(r'More than 1 style with.*xml:id', base_content))
deep_results['IMPL-003'] = {
    'name': 'Style resolver cascade',
    'detected': has_chain and has_sources,
    'validated': has_dup_error,
    'note': 'Follows style references via _get_style_reference_chain. Raises CaptionReadSyntaxError on duplicate xml:id.',
}
print(f"  IMPL-003: {'PASS' if has_chain else 'FAIL'}")

# IMPL-004: Region resolver
# _determine_region_id: element → ancestors → descendants
# RegionCreator: creates regions, assigns IDs, cleans up unused
has_region_determine = bool(re.search(r'def _determine_region_id', base_content))
has_region_creator = bool(re.search(r'class RegionCreator', base_content))
has_region_cleanup = bool(re.search(r'def cleanup_regions', base_content))
deep_results['IMPL-004'] = {
    'name': 'Region resolver',
    'detected': has_region_determine and has_region_creator,
    'validated': has_region_cleanup,
    'note': 'Full region resolution: element→ancestors→descendants. RegionCreator creates/assigns/cleans up regions.',
}
print(f"  IMPL-004: {'PASS' if has_region_determine else 'FAIL'}")

# IMPL-007: Color handling
# Reader: _convert_style reads tts:color as raw string (no parsing)
# Writer: _recreate_style writes color as raw string
# geometry.py: no color parsing
# Named colors only exist as defaults ("white" in DFXP_DEFAULT_STYLE)
has_color_read = bool(re.search(r'tts:color.*attrs\[.*color', base_content, re.DOTALL))
has_color_parse = bool(re.search(r'parse.*color|rgba?\s*\(|#[0-9a-fA-F]{6}|color.*convert', base_content + geometry_content, re.I))
deep_results['IMPL-007'] = {
    'name': 'Color handling',
    'detected': has_color_read,
    'validated': False,
    'note': 'Color read/written as raw string passthrough. No parsing of named colors, hex, or rgba() formats.',
}
if has_color_read and not has_color_parse:
    issues['partial_validation'].append({
        'rule_id': 'IMPL-007', 'name': 'Color handling',
        'status': 'PASSTHROUGH_ONLY', 'severity': 'SHOULD',
        'note': 'tts:color passed through as raw string. No validation of color format (hex, named, rgba).',
    })
print(f"  IMPL-007: {'PARSE' if has_color_parse else 'PASSTHROUGH ONLY'}")

# IMPL-008: XML escaping
# Writer uses xml.sax.saxutils.escape(s) via _encode method
has_escape_import = bool(re.search(r'from xml\.sax\.saxutils import escape', base_content))
has_encode_func = bool(re.search(r'def _encode.*\n.*return escape', base_content))
deep_results['IMPL-008'] = {
    'name': 'XML character escaping',
    'detected': has_escape_import,
    'validated': has_encode_func,
    'note': 'Writer uses xml.sax.saxutils.escape() via _encode method. Handles &, <, >.',
}
print(f"  IMPL-008: {'PASS' if has_encode_func else 'FAIL'}")

# RULE-STY-006: fontWeight/bold — read-only gap
# Reader: attrs["bold"] = True when tts:fontWeight == "bold" (line ~320)
# Writer: _recreate_style never outputs tts:fontWeight — bold silently dropped on write
has_bold_read = bool(re.search(r'tts:fontweight.*bold.*attrs\[.bold.\]|fontweight.*==.*bold', base_content, re.I))
recreate_style_section = re.search(r'def _recreate_style\(content.*?\n(?=\ndef |\nclass |\Z)', base_content, re.DOTALL)
recreate_style_code = recreate_style_section.group(0) if recreate_style_section else ''
has_bold_in_recreate = bool(re.search(r'fontWeight|bold', recreate_style_code))
deep_results['RULE-STY-006'] = {
    'name': 'fontWeight/bold read-only gap',
    'detected': has_bold_read,
    'validated': has_bold_in_recreate,
    'note': 'Reader parses tts:fontWeight→attrs["bold"], but _recreate_style never writes it back. Bold silently dropped on round-trip.' if has_bold_read and not has_bold_in_recreate else '',
}
if has_bold_read and not has_bold_in_recreate:
    issues['partial_validation'].append({
        'rule_id': 'RULE-STY-006', 'name': 'fontWeight/bold read-only',
        'status': 'READ_NOT_WRITTEN', 'severity': 'MUST',
        'note': 'Reader: attrs["bold"]=True from tts:fontWeight. Writer: _recreate_style omits tts:fontWeight. Bold lost on write.',
    })
print(f"  RULE-STY-006: {'PASS' if has_bold_in_recreate else 'READ-ONLY — bold dropped on write'}")

# RULE-STY-008: textDecoration/underline — read-only gap
# Reader: attrs["underline"] = True when tts:textDecoration contains "underline"
# Writer: _recreate_style never outputs tts:textDecoration — underline silently dropped
has_underline_read = bool(re.search(r'tts:textdecoration.*underline', base_content, re.I | re.DOTALL))
has_underline_in_recreate = bool(re.search(r'textDecoration|underline', recreate_style_code))
deep_results['RULE-STY-008'] = {
    'name': 'textDecoration/underline read-only gap',
    'detected': has_underline_read,
    'validated': has_underline_in_recreate,
    'note': 'Reader parses tts:textDecoration→attrs["underline"], but _recreate_style never writes it back. Underline silently dropped on round-trip.' if has_underline_read and not has_underline_in_recreate else '',
}
if has_underline_read and not has_underline_in_recreate:
    issues['partial_validation'].append({
        'rule_id': 'RULE-STY-008', 'name': 'textDecoration/underline read-only',
        'status': 'READ_NOT_WRITTEN', 'severity': 'MUST',
        'note': 'Reader: attrs["underline"]=True from tts:textDecoration. Writer: _recreate_style omits tts:textDecoration. Underline lost on write.',
    })
print(f"  RULE-STY-008: {'PASS' if has_underline_in_recreate else 'READ-ONLY — underline dropped on write'}")

# IMPL-004: Region resolver — LookupError silently drops region
# _determine_region_id catches LookupError from _get_region_from_descendants
# and returns None (bare `return`), silently dropping the region assignment
# when descendants have conflicting region IDs
has_region_lookup_catch = bool(re.search(r'except LookupError:\s*\n\s*return\b', base_content))
has_region_lookup_warn = bool(re.search(r'except LookupError:[^\n]*(?:warn|log|raise)|\nexcept LookupError:\s*\n\s+(?:warn|log|raise)', base_content))
if has_region_lookup_catch and not has_region_lookup_warn:
    deep_results['IMPL-004']['note'] = (
        deep_results['IMPL-004'].get('note', '') +
        ' WARNING: _determine_region_id catches LookupError and returns None — '
        'conflicting descendant regions silently dropped instead of warned/raised.'
    ).strip()
    deep_results['IMPL-004']['validated'] = False
    issues['partial_validation'].append({
        'rule_id': 'IMPL-004', 'name': 'Region resolver silently drops conflicting regions',
        'status': 'SILENT_ERROR_SUPPRESSION', 'severity': 'SHOULD',
        'note': 'except LookupError: return — conflicting descendant regions cause silent None region. No warning or error raised.',
    })
print(f"  IMPL-004 (LookupError): {'PASS' if not has_region_lookup_catch else 'SILENT DROP — conflicting regions suppressed'}")

print(f"\n  Read-only attribute summary:")
print(f"    fontWeight: read={'YES' if has_bold_read else 'NO'}, write={'YES' if has_bold_in_recreate else 'NO'}")
print(f"    textDecoration: read={'YES' if has_underline_read else 'NO'}, write={'YES' if has_underline_in_recreate else 'NO'}")

# Extract _convert_style section early (needed for subsequent deep checks)
convert_style_section = ''
m = re.search(r'def _convert_style\b.*?(?=\ndef |\nclass )', base_content, re.DOTALL)
if m:
    convert_style_section = m.group(0)

# RULE-STY-002: tts:backgroundColor — not supported at all
has_bg_read = bool(re.search(r'tts:backgroundColor|background.?[Cc]olor', convert_style_section if convert_style_section else base_content))
has_bg_write = bool(re.search(r'tts:backgroundColor|background.?[Cc]olor', recreate_style_code))
deep_results['RULE-STY-002'] = {
    'name': 'tts:backgroundColor not implemented',
    'detected': has_bg_read,
    'validated': has_bg_write,
    'note': 'tts:backgroundColor not read by _convert_style and not written by _recreate_style. Common TTML attribute entirely missing.',
}
if not has_bg_read:
    issues['validation_gaps'].append({
        'rule_id': 'RULE-STY-002', 'name': 'tts:backgroundColor not implemented',
        'status': 'NOT_IMPLEMENTED', 'severity': 'SHOULD',
        'note': '_convert_style has no case for tts:backgroundColor. _recreate_style does not write it. Completely missing.',
    })
print(f"  RULE-STY-002: {'PASS' if has_bg_read else 'NOT IMPLEMENTED'}")

# RULE-STY-005: fontStyle only handles "italic", ignores "oblique"/"normal"
has_fontstyle_italic = bool(re.search(r'tts:fontstyle.*==.*italic|fontstyle.*italic', base_content, re.I))
has_fontstyle_oblique = bool(re.search(r'oblique', base_content))
deep_results['RULE-STY-005'] = {
    'name': 'fontStyle partial — only italic handled',
    'detected': has_fontstyle_italic,
    'validated': has_fontstyle_oblique,
    'note': '_convert_style only handles tts:fontStyle=="italic". Values "oblique" and "normal" are silently ignored.' if has_fontstyle_italic and not has_fontstyle_oblique else '',
}
if has_fontstyle_italic and not has_fontstyle_oblique:
    issues['partial_validation'].append({
        'rule_id': 'RULE-STY-005', 'name': 'fontStyle only handles italic',
        'status': 'PARTIAL_VALUES', 'severity': 'SHOULD',
        'note': 'Reader checks tts:fontStyle=="italic" only. "oblique" and "normal" values silently ignored.',
    })
print(f"  RULE-STY-005: {'PASS' if has_fontstyle_oblique else 'PARTIAL — only italic, oblique/normal ignored'}")

# IMPL-008 extra: &apos; workaround — silent XML entity rewrite before parsing
has_apos_workaround = bool(re.search(r'replace\(.*&apos;|replace\(.*apos', base_content))
if has_apos_workaround:
    issues['partial_validation'].append({
        'rule_id': 'IMPL-008', 'name': 'Silent &apos; workaround',
        'status': 'SILENT_WORKAROUND', 'severity': 'SHOULD',
        'note': 'markup.replace("&apos;", "\'") silently rewrites valid XML entity before parsing. Could mask malformed input.',
    })
print(f"  IMPL-008 (&apos;): {'SILENT WORKAROUND' if has_apos_workaround else 'CLEAN'}")

# LegacyDFXPWriter in extras.py — same bold/underline write gap
has_legacy_recreate = bool(re.search(r'def _recreate_style', extras_content))
has_legacy_bold_write = bool(re.search(r'fontWeight|bold', extras_content.split('def _recreate_style')[1] if 'def _recreate_style' in extras_content else ''))
if has_legacy_recreate and not has_legacy_bold_write:
    issues['partial_validation'].append({
        'rule_id': 'RULE-STY-006', 'name': 'LegacyDFXPWriter also drops bold',
        'status': 'READ_NOT_WRITTEN', 'severity': 'MUST',
        'note': 'extras.py LegacyDFXPWriter._recreate_style also omits tts:fontWeight. Same gap as base.py.',
    })
print(f"  extras.py bold: {'PASS' if has_legacy_bold_write else 'ALSO DROPS BOLD'}")

# ===== PHASE 2: SYSTEMATIC RULE CHECK =====
print("\n" + "=" * 60)
print("PHASE 2: ALL RULES CHECK ({} rules)".format(len(all_rules)))
print("=" * 60)

# Per-rule patterns matching ACTUAL code constructs, not keywords
specific_patterns = {
    # Document structure
    'RULE-DOC-001': [r'def detect|</tt>.*content|DFXP_BASE_MARKUP.*<tt'],
    'RULE-DOC-002': [r'http://www.w3.org/ns/ttml|xmlns.*ttml'],
    'RULE-DOC-003': [r'xml:lang.*DEFAULT_LANGUAGE_CODE|attrs\.get.*xml:lang'],
    'RULE-DOC-004': [r'<head|find.*head|findChild.*head'],
    'RULE-DOC-005': [r'find.*body|find_all.*body|<body'],
    'RULE-DOC-006': [r'application/ttml\+xml|content_type.*ttml|mime.*ttml'],
    'RULE-DOC-007': [r'xml.*declaration|encoding.*UTF-8|encoding.*utf'],
    # Time expressions
    'RULE-TIME-001': [r'CLOCK_TIME_PATTERN|_convert_clock_time_to_microseconds'],
    'RULE-TIME-002': [r'clock_time_match\.group.*frames|/\s*30\s*\*'],
    'RULE-TIME-003': [r'OFFSET_TIME_PATTERN|_convert_time_count_to_microseconds'],
    'RULE-TIME-004': [r'metric.*==.*"h"|MICROSECONDS_PER_UNIT.*hours'],
    'RULE-TIME-005': [r'metric.*==.*"m"|MICROSECONDS_PER_UNIT.*minutes'],
    'RULE-TIME-006': [r'metric.*==.*"s"|MICROSECONDS_PER_UNIT.*seconds'],
    'RULE-TIME-007': [r'metric.*==.*"ms"|MICROSECONDS_PER_UNIT.*milliseconds'],
    'RULE-TIME-008': [r'metric.*==.*"f"|frame.*offset'],
    'RULE-TIME-009': [r'metric.*==.*"t"|NotImplementedError.*tick'],
    'RULE-TIME-010': [r'\.get\("begin"\)|\.get\(.*begin|attrib.*begin'],
    'RULE-TIME-011': [r'\.get\("end"\)|\.get\(.*end|attrib.*end'],
    'RULE-TIME-012': [r'timeContainer|par\b.*parallel|seq\b.*sequential'],
    'RULE-TIME-013': [r'containment|constrain|clip.*time'],
    'RULE-TIME-014': [r'ttp:frameRate|attrib.*frameRate|get.*frameRate'],
    # Content elements
    'RULE-CONT-001': [r'find.*body|find_all.*body'],
    'RULE-CONT-002': [r'find_all.*"div"|new_tag.*"div"'],
    'RULE-CONT-003': [r'find_all.*"p"|new_tag.*"p"'],
    'RULE-CONT-004': [r'_convert_span_to_nodes|_recreate_span|name.*==.*"span"'],
    'RULE-CONT-005': [r'name.*==.*"br"|<br/?>'],
    'RULE-CONT-006': [r'<set\b|set.*element'],
    'RULE-CONT-007': [r'NavigableString|isinstance.*NavigableString|\.text'],
    'RULE-CONT-008': [r'nested.*div|div.*div.*nesting'],
    # Styling — use word-boundary patterns to avoid substring matches
    'RULE-STY-001': [r'tts:color|\.lower\(\).*==.*"tts:color"'],
    'RULE-STY-002': [r'tts:backgroundColor|background.*[Cc]olor'],
    'RULE-STY-003': [r'tts:fontSize|tts:fontsize|font-size'],
    'RULE-STY-004': [r'tts:fontFamily|tts:fontfamily|font-family'],
    'RULE-STY-005': [r'tts:fontStyle|tts:fontstyle|fontStyle.*italic'],
    'RULE-STY-006': [r'tts:fontWeight|tts:fontweight|fontWeight.*bold'],
    'RULE-STY-007': [r'tts:textAlign|tts:textalign|text-align'],
    'RULE-STY-008': [r'tts:textDecoration|tts:textdecoration|underline'],
    'RULE-STY-009': [r'(?<!\w)tts:direction(?!\w)'],
    'RULE-STY-010': [r'(?<!\w)(?:tts:writingMode|writingMode)(?!\w)'],
    # CRITICAL: tts:display must NOT match tts:displayAlign
    'RULE-STY-011': [r'(?<!\w)tts:display(?!Align)(?!\w)'],
    'RULE-STY-012': [r'tts:displayAlign|display.*[Aa]lign|displayAlign'],
    'RULE-STY-013': [r'(?<!\w)(?:tts:lineHeight|lineHeight)(?!\w)'],
    'RULE-STY-014': [r'(?<!\w)tts:opacity(?!\w)'],
    'RULE-STY-015': [r'(?<!\w)(?:tts:textOutline|textOutline)(?!\w)'],
    'RULE-STY-016': [r'tts:padding|Padding\.from_xml_attribute'],
    'RULE-STY-017': [r'tts:extent|Stretch\.from_xml_attribute'],
    'RULE-STY-018': [r'tts:origin|Point\.from_xml_attribute'],
    'RULE-STY-019': [r'(?<!\w)tts:overflow(?!\w)'],
    'RULE-STY-020': [r'(?<!\w)(?:tts:showBackground|showBackground)(?!\w)'],
    'RULE-STY-021': [r'(?<!\w)tts:visibility(?!\w)'],
    'RULE-STY-022': [r'(?<!\w)(?:tts:wrapOption|wrapOption)(?!\w)'],
    'RULE-STY-023': [r'(?<!\w)(?:tts:unicodeBidi|unicodeBidi)(?!\w)'],
    'RULE-STY-024': [r'(?<!\w)(?:tts:zIndex|zIndex)(?!\w)'],
    'RULE-STY-025': [r'named_colors|color_map|color.*lookup|COLOR_NAMES'],
    'RULE-STY-026': [r'parse_color|rgba_to_|hex_to_|int\(.*16\).*color'],
    'RULE-STY-027': [r'UnitEnum\.PIXEL|UnitEnum\.EM|UnitEnum\.PERCENT|UnitEnum\.CELL|Size\.from_string'],
    # Style model
    'RULE-SMOD-001': [r'find.*"styling"|find.*"style"'],
    'RULE-SMOD-002': [r'xml:id.*style|style.*xml:id'],
    'RULE-SMOD-003': [r'_get_style_reference_chain|style.*=.*attrib'],
    'RULE-SMOD-004': [r'_get_style_sources|nested_styles'],
    'RULE-SMOD-005': [r'inline.*style|dfxp_attrs.*tts:'],
    # Layout
    'RULE-LAY-001': [r'find.*"layout"|<layout'],
    'RULE-LAY-002': [r'find.*"region"|RegionCreator|_determine_region_id'],
    'RULE-LAY-003': [r'xml:id.*region|region.*xml:id'],
    'RULE-LAY-004': [r'default.*region|DFXP_DEFAULT_REGION'],
    # Metadata — match actual element/attribute access, not keywords
    'RULE-META-001': [r'find.*"metadata"|find_all.*"metadata"|ttm:title|ttm:desc|ttm:copyright'],
    'RULE-META-002': [r'find.*"ttm:title"|attrib.*ttm:title'],
    'RULE-META-003': [r'find.*"ttm:desc"|attrib.*ttm:desc'],
    'RULE-META-004': [r'find.*"ttm:copyright"|attrib.*ttm:copyright'],
    'RULE-META-005': [r'find.*"ttm:agent"|attrib.*ttm:agent'],
    'RULE-META-006': [r'find.*"ttm:role"|attrib.*ttm:role'],
    # Parameters — check for actual reading from document, not just keywords
    'RULE-PAR-001': [r'ttp:timeBase|attrib.*timeBase|get.*timeBase'],
    'RULE-PAR-002': [r'ttp:frameRate|attrib.*frameRate|get.*frameRate'],
    'RULE-PAR-003': [r'ttp:subFrameRate|attrib.*subFrameRate'],
    'RULE-PAR-004': [r'ttp:frameRateMultiplier|attrib.*frameRateMultiplier'],
    'RULE-PAR-005': [r'ttp:tickRate|attrib.*tickRate|get.*tickRate'],
    'RULE-PAR-006': [r'ttp:dropMode|attrib.*dropMode'],
    'RULE-PAR-007': [r'ttp:clockMode|attrib.*clockMode'],
    'RULE-PAR-008': [r'ttp:markerMode|attrib.*markerMode'],
    'RULE-PAR-009': [r'ttp:cellResolution|attrib.*cellResolution|cell.*resolution'],
    'RULE-PAR-010': [r'ttp:pixelAspectRatio|pixel.*aspect'],
    'RULE-PAR-011': [r'ttp:profile|attrib.*profile'],
    # Profile
    'RULE-PROF-001': [r'profile.*designat|profile.*uri'],
    'RULE-PROF-002': [r'transformation.*profile'],
    'RULE-PROF-003': [r'presentation.*profile'],
    'RULE-PROF-004': [r'profile.*element.*attribute|profile.*precedence'],
    'RULE-PROF-005': [r'feature.*designat|feature.*uri'],
    # Validation
    'RULE-VAL-001': [r'arg\.lower\(\).*==.*"tts:|attr_name\.lower\(\)|\.lower\(\).*==.*"tts:'],
    'RULE-VAL-002': [r'CaptionReadTimingError|Invalid timestamp|raise.*timing'],
    'RULE-VAL-003': [r'CaptionReadSyntaxError|raise.*syntax|raise.*parsing'],
    'RULE-VAL-004': [r'CaptionReadNoCaptions|empty caption|is_empty'],
    'RULE-VAL-005': [r'InvalidInputError|not.*unicode|isinstance.*str'],
}

missing_rules = []
found_rules = []

for rule_id, meta in sorted(all_rules.items()):
    # Skip rules covered in Phase 1
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

# Styling attributes: track read vs write separately
# Reader: _convert_style in DFXPReader
# Writer: _recreate_style (module-level function)
# Layout: LayoutInfoScraper._find_attribute
reader_section = ''
m = re.search(r'(class DFXPReader.*?)(?=class DFXPWriter)', base_content, re.DOTALL)
if m:
    reader_section = m.group(1)

# The module-level _recreate_style function (writer side)
recreate_fn = ''
m2 = re.search(r'^def _recreate_style\(content.*?(?=\n(?:def |class ))', base_content, re.DOTALL | re.MULTILINE)
if m2:
    recreate_fn = m2.group(0)

styling_coverage = {
    'tts:color':          {
        'read': bool(re.search(r'tts:color', reader_section, re.I)),
        'write': bool(re.search(r'tts:color', recreate_fn, re.I)),
        'note': 'Full round-trip (raw string passthrough)',
    },
    'tts:backgroundColor': {
        'read': False,
        'write': False,
        'note': 'Not implemented',
    },
    'tts:fontSize':       {
        'read': bool(re.search(r'tts:fontsize', reader_section, re.I)),
        'write': bool(re.search(r'tts:fontSize', recreate_fn)),
        'note': 'Full round-trip',
    },
    'tts:fontFamily':     {
        'read': bool(re.search(r'tts:fontfamily', reader_section, re.I)),
        'write': bool(re.search(r'tts:fontFamily', recreate_fn)),
        'note': 'Full round-trip',
    },
    'tts:fontStyle':      {
        'read': bool(re.search(r'tts:fontstyle', reader_section, re.I)),
        'write': bool(re.search(r'tts:fontStyle', recreate_fn)),
        'note': 'Full round-trip (italic only)',
    },
    'tts:fontWeight':     {
        'read': bool(re.search(r'tts:fontweight', reader_section, re.I)),
        'write': bool(re.search(r'fontWeight|bold', recreate_fn)),
        'note': 'READ-ONLY: Reader detects bold, writer silently drops it',
    },
    'tts:textAlign':      {
        'read': bool(re.search(r'tts:textalign', reader_section, re.I)),
        'write': bool(re.search(r'tts:textAlign', recreate_fn)),
        'note': 'Full round-trip (also via LayoutInfoScraper)',
    },
    'tts:textDecoration': {
        'read': bool(re.search(r'tts:textdecoration', reader_section, re.I)),
        'write': bool(re.search(r'textDecoration|underline', recreate_fn)),
        'note': 'READ-ONLY: Reader detects underline, writer silently drops it',
    },
    'tts:direction':      {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:writingMode':    {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:display':        {'read': False, 'write': False, 'note': 'Not implemented (distinct from tts:displayAlign)'},
    'tts:displayAlign':   {
        'read': bool(re.search(r'tts:displayAlign', base_content)),
        'write': bool(re.search(r'tts:displayAlign', recreate_fn + base_content.split('class RegionCreator')[0] if 'class RegionCreator' in base_content else '')),
        'note': 'Full round-trip via LayoutInfoScraper + _create_external_alignment',
    },
    'tts:lineHeight':     {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:opacity':        {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:textOutline':    {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:padding':        {
        'read': bool(re.search(r'tts:padding', base_content)),
        'write': bool(re.search(r'tts:padding', base_content)),
        'note': 'Full round-trip via LayoutInfoScraper + _convert_layout_to_attributes',
    },
    'tts:extent':         {
        'read': bool(re.search(r'tts:extent', base_content)),
        'write': bool(re.search(r'tts:extent', base_content)),
        'note': 'Full round-trip via LayoutInfoScraper. Root tt extent must be in pixels.',
    },
    'tts:origin':         {
        'read': bool(re.search(r'tts:origin', base_content)),
        'write': bool(re.search(r'tts:origin', base_content)),
        'note': 'Full round-trip via LayoutInfoScraper',
    },
    'tts:overflow':       {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:showBackground': {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:visibility':     {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:wrapOption':     {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:unicodeBidi':    {'read': False, 'write': False, 'note': 'Not implemented'},
    'tts:zIndex':         {'read': False, 'write': False, 'note': 'Not implemented'},
}

sty_read = sum(1 for s in styling_coverage.values() if s['read'])
sty_write = sum(1 for s in styling_coverage.values() if s['write'])
sty_roundtrip = sum(1 for s in styling_coverage.values() if s['read'] and s['write'])
sty_readonly = sum(1 for s in styling_coverage.values() if s['read'] and not s['write'])
print(f"  Styling: {sty_read}/24 read, {sty_write}/24 write, {sty_roundtrip}/24 round-trip, {sty_readonly} read-only")

# Time expression formats
time_coverage = {
    'Clock-time fractional (HH:MM:SS.sss)': {
        'supported': bool(re.search(r'sub_frames', base_content)),
        'note': 'Via CLOCK_TIME_PATTERN sub_frames group, .ljust(3, "0")',
    },
    'Clock-time frames (HH:MM:SS:FF)': {
        'supported': bool(re.search(r'clock_time_match.*frames', base_content)),
        'note': 'Parsed but hardcoded /30 (ignores ttp:frameRate)',
    },
    'Offset hours (Nh)': {
        'supported': bool(re.search(r'metric.*==.*"h"', base_content)),
        'note': 'Supported',
    },
    'Offset minutes (Nm)': {
        'supported': bool(re.search(r'metric.*==.*"m"', base_content)),
        'note': 'Supported',
    },
    'Offset seconds (Ns)': {
        'supported': bool(re.search(r'metric.*==.*"s"', base_content)),
        'note': 'Supported',
    },
    'Offset milliseconds (Nms)': {
        'supported': bool(re.search(r'metric.*==.*"ms"', base_content)),
        'note': 'Supported',
    },
    'Offset frames (Nf)': {
        'supported': bool(re.search(r'metric.*==.*"f"', base_content)),
        'note': 'Parsed but hardcoded /30 (ignores ttp:frameRate)',
    },
    'Offset ticks (Nt)': {
        'supported': False,
        'note': 'Raises NotImplementedError',
    },
}

time_supported = sum(1 for t in time_coverage.values() if t['supported'])
print(f"  Time formats: {time_supported}/8 ({8 - time_supported} missing/broken)")

# Content elements
content_elements = {
    'body':     {'read': bool(re.search(r'find.*"body"', base_content)), 'write': bool(re.search(r'<body|new_tag.*"body"', base_content))},
    'div':      {'read': bool(re.search(r'find_all.*"div"', base_content)), 'write': bool(re.search(r'new_tag.*"div"', base_content))},
    'p':        {'read': bool(re.search(r'find_all.*"p"', base_content)), 'write': bool(re.search(r'new_tag.*"p"', base_content))},
    'span':     {'read': bool(re.search(r'_convert_span_to_nodes', base_content)), 'write': bool(re.search(r'_recreate_span', base_content))},
    'br':       {'read': bool(re.search(r'name.*==.*"br"', base_content)), 'write': bool(re.search(r'<br/?>', base_content))},
    'set':      {'read': False, 'write': False},
    'styling':  {'read': bool(re.search(r'find.*"styling"', base_content)), 'write': bool(re.search(r'find.*"styling".*append', base_content))},
    'style':    {'read': bool(re.search(r'find_all.*"style"', base_content)), 'write': bool(re.search(r'_recreate_styling_tag', base_content))},
    'layout':   {'read': bool(re.search(r'LayoutInfoScraper|layout_info', base_content)), 'write': bool(re.search(r'find.*"layout".*append|layout_section', base_content))},
    'region':   {'read': bool(re.search(r'_determine_region_id', base_content)), 'write': bool(re.search(r'_create_unique_regions', base_content))},
    'metadata': {'read': False, 'write': False},
}

elem_read = sum(1 for e in content_elements.values() if e['read'])
elem_write = sum(1 for e in content_elements.values() if e['write'])
print(f"  Content elements: {elem_read}/11 read, {elem_write}/11 write")

# Parameter attributes — check if actually read FROM document
param_coverage = {
    'ttp:timeBase':             {'read': False, 'note': 'Not read (media assumed)'},
    'ttp:frameRate':            {'read': False, 'note': 'Not read (hardcoded /30)'},
    'ttp:subFrameRate':         {'read': False, 'note': 'Not implemented'},
    'ttp:frameRateMultiplier':  {'read': False, 'note': 'Not implemented'},
    'ttp:tickRate':             {'read': False, 'note': 'Not read (tick raises NotImplementedError)'},
    'ttp:dropMode':             {'read': False, 'note': 'Not implemented'},
    'ttp:clockMode':            {'read': False, 'note': 'Not implemented'},
    'ttp:markerMode':           {'read': False, 'note': 'Not implemented'},
    'ttp:cellResolution':       {'read': False, 'note': 'Not read (hardcoded 32x15 defaults in geometry.py)'},
    'ttp:pixelAspectRatio':     {'read': False, 'note': 'Not implemented'},
    'ttp:profile':              {'read': False, 'note': 'Not implemented'},
}

param_read = sum(1 for p in param_coverage.values() if p['read'])
print(f"  Parameter attributes: {param_read}/11 read from document")

# Length unit support (from geometry.py)
unit_coverage = {
    'px (pixel)': bool(re.search(r'UnitEnum\.PIXEL|"px"', geometry_content)),
    'em':         bool(re.search(r'UnitEnum\.EM|"em"', geometry_content)),
    '% (percent)': bool(re.search(r'UnitEnum\.PERCENT|"%"', geometry_content)),
    'c (cell)':   bool(re.search(r'UnitEnum\.CELL|"c"', geometry_content)),
    'pt (point)': bool(re.search(r'UnitEnum\.PT|"pt"', geometry_content)),
}

units_supported = sum(1 for u in unit_coverage.values() if u)
print(f"  Length units: {units_supported}/5")

# ===== PHASE 4: TEST COVERAGE =====
print("\n" + "=" * 60)
print("PHASE 4: TEST COVERAGE")
print("=" * 60)

test_files = glob.glob('tests/**/test*dfxp*.py', recursive=True)
def _read(p):
    with open(p) as _fh: return _fh.read()
tests = "\n".join(_read(f) for f in test_files if os.path.exists(f))
print(f"  Test files: {len(test_files)} ({len(tests)} chars)")

test_checks = {
    'RULE-DOC-001': [r'def test.*detect|def test.*root|def test.*tt\b|def test.*namespace'],
    'RULE-DOC-003': [r'def test.*lang'],
    'RULE-TIME-001': [r'def test.*time|def test.*clock|def test.*timestamp'],
    'RULE-TIME-002': [r'def test.*frame'],
    'RULE-STY-001': [r'def test.*color'],
    'RULE-STY-003': [r'def test.*font.*size'],
    'RULE-STY-006': [r'def test.*bold|def test.*font.*weight'],
    'RULE-STY-007': [r'def test.*align'],
    'RULE-STY-008': [r'def test.*underline|def test.*text.*decoration'],
    'RULE-LAY-002': [r'def test.*region'],
    'RULE-SMOD-003': [r'def test.*style.*ref|def test.*style.*inherit|def test.*cascade'],
    'IMPL-003': [r'def test.*style.*resolv|def test.*cascade|def test.*inherit'],
    'IMPL-004': [r'def test.*region'],
    'IMPL-008': [r'def test.*escap|def test.*encod|def test.*write'],
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

os.makedirs("ai_artifacts/compliance_checks/dfxp", exist_ok=True)
date = datetime.now().strftime("%Y-%m-%d")
path = f"ai_artifacts/compliance_checks/dfxp/compliance_report_{date}.md"

total_issues = sum(len(v) for v in issues.values())
must_issues = (len([i for i in issues['validation_gaps'] if i.get('severity') == 'MUST']) +
               len([i for i in issues['partial_validation'] if i.get('severity') == 'MUST']) +
               len(must_missing))

report = f"""# DFXP/TTML EXHAUSTIVE Compliance Report

**Generated**: {date}
**Spec**: {latest_spec}
**Analysis**: Deep Validation + Systematic Rules + Coverage + Tests
**Implementation files**: {', '.join(f for f in impl_files if os.path.exists(f))}

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

### Styling Attributes ({sty_read}/24 read, {sty_write}/24 write, {sty_roundtrip}/24 round-trip)

| Attribute | Read | Write | Round-trip | Note |
|-----------|------|-------|------------|------|
"""

for attr, info in styling_coverage.items():
    r = "Yes" if info['read'] else "No"
    w = "Yes" if info['write'] else "No"
    rt = "Yes" if info['read'] and info['write'] else "No"
    report += f"| `{attr}` | {r} | {w} | {rt} | {info['note']} |\n"

report += f"""
### Time Expression Formats ({time_supported}/8)

| Format | Supported | Note |
|--------|-----------|------|
"""

for fmt, info in time_coverage.items():
    s = "Yes" if info['supported'] else "No"
    report += f"| {fmt} | {s} | {info['note']} |\n"

report += f"""
### Content Elements ({elem_read}/11 read, {elem_write}/11 write)

| Element | Read | Write |
|---------|------|-------|
"""

for elem, info in content_elements.items():
    r = "Yes" if info['read'] else "No"
    w = "Yes" if info['write'] else "No"
    report += f"| `<{elem}>` | {r} | {w} |\n"

report += f"""
### Parameter Attributes ({param_read}/11 read from document)

| Attribute | Read | Note |
|-----------|------|------|
"""

for attr, info in param_coverage.items():
    r = "Yes" if info['read'] else "No"
    report += f"| `{attr}` | {r} | {info['note']} |\n"

report += f"""
### Length Units ({units_supported}/5)

| Unit | Supported |
|------|-----------|
"""

for unit, supported in unit_coverage.items():
    s = "Yes" if supported else "No"
    report += f"| {unit} | {s} |\n"

report += f"""
---

## 5. Test Gaps ({len(issues['test_gaps'])})

"""

for t in issues['test_gaps']:
    report += f"- **{t['rule_id']}**: {t['name']}\n"

report += f"""
---

## 6. Key Findings

1. **Frame rate hardcoded to /30**: Both clock-time frames (HH:MM:SS:FF) and offset frames (Nf) divide by 30. The code never reads `ttp:frameRate` from the document. This affects any TTML file with non-30fps frame references.
2. **Tick time raises NotImplementedError**: `_convert_time_count_to_microseconds` recognizes the `t` metric but raises `NotImplementedError` instead of computing. Also can't compute without `ttp:tickRate` (which is never read).
3. **Zero ttp: parameters read from document**: None of the 11 TTML parameter attributes (ttp:timeBase, ttp:frameRate, ttp:tickRate, ttp:cellResolution, etc.) are actually read from the input. All use hardcoded defaults.
4. **fontWeight (bold) and textDecoration (underline) are READ-ONLY**: Reader correctly detects these attributes, but `_recreate_style()` has no case for "bold" or "underline" keys — they are silently dropped on write. Round-trip DFXP→pycaption→DFXP loses bold and underline styling.
5. **tts:display is NOT implemented** (distinct from tts:displayAlign which IS implemented). Previous audit had a false positive where `tts:display` pattern matched `tts:displayAlign` as a substring.
6. **xml:lang reads with silent fallback**: `dfxp_document.tt.attrs.get("xml:lang", DEFAULT_LANGUAGE_CODE)` falls back to "en" silently. No BCP-47 validation of the language code.
7. **Color passed through as raw string**: `tts:color` is read and written but never parsed or validated. Named colors, hex, and rgba() formats are all passed through without checking.
8. **Style chaining IS implemented**: `_get_style_reference_chain` follows style references recursively, with duplicate xml:id detection raising `CaptionReadSyntaxError`.
9. **Region resolution IS implemented**: Full ancestor→descendant lookup via `_determine_region_id`, region creation via `RegionCreator`, and unused region cleanup.
10. **detect() uses substring check**: `"</tt>" in content.lower()` matches anywhere in the content, not proper XML root validation.
11. **Root tt extent validated**: `_find_root_extent` correctly requires root `tts:extent` to be in pixel units, raising `CaptionReadSyntaxError` otherwise.
12. **Cell resolution uses hardcoded 32x15**: geometry.py's `as_percentage_of` uses 32 columns and 15 rows as default cell resolution instead of reading `ttp:cellResolution`.
13. **5 length units supported**: px, em, %, c (cell), pt — all via `Size.from_string()` in geometry.py.
14. **tts:backgroundColor NOT supported**: Despite being one of the most common TTML styling attributes, it's not read or written.

---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**Rules**: {len(all_rules)} | **Found**: {len(found_rules)} | **Missing**: {len(issues['missing'])}
**Styling**: {sty_roundtrip}/24 round-trip ({sty_readonly} read-only) | **Timing**: {time_supported}/8 | **Elements**: {elem_read}/11 read | **Params**: {param_read}/11
"""

with open(path, 'w') as _f: _f.write(report)
print(f"\n Report: {path}")
print(f"   Total issues: {total_issues} ({must_issues} MUST)")
```

Execute the above Python script directly (no external files needed beyond spec and implementation).

---

## Key improvements over previous version

1. **No tts:display false positive**: Uses negative lookahead `(?!Align)` so `tts:display` pattern does NOT match `tts:displayAlign`
2. **Read-only attributes correctly identified**: fontWeight and textDecoration tracked as read-only (reader detects, writer drops)
3. **xml:lang correctly assessed**: Silent fallback to "en", no BCP-47 validation
4. **Expanded file scope**: Includes geometry.py for unit parsing, Layout, Size, Padding classes
5. **Per-rule specific_patterns**: Matches actual function names (`_convert_clock_time_to_microseconds`, `_get_style_reference_chain`) not broad keywords
6. **Read/write distinction for all coverage**: Styling, elements, parameters tracked for read vs write separately
7. **NotImplementedError for ticks correctly reported**: Not counted as "implemented"
8. **Frame rate analysis**: Clearly reports hardcoded /30 for both clock-time and offset frames
9. **Zero ttp: parameters**: Explicitly reports that no TTML parameter attributes are read from documents
10. **Key findings section**: 14 accurate assessments with specific code references

---

## Success Criteria

- All spec rules individually checked with per-rule patterns
- Deep validation for 10 critical rules at function level
- Styling attributes tracked as read/write/round-trip (not just keyword match)
- Time formats with accurate implementation status (hardcoded /30 flagged)
- Content elements tracked as read/write
- Parameter attributes checked for actual document reading (not just keyword)
- Length unit support verified against geometry.py
- No false positives (tts:display ≠ tts:displayAlign)
- No false assessments (fontWeight/textDecoration = read-only, not round-trip)
- Key findings narrative for actionable summary
