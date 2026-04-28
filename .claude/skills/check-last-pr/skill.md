---
name: check-last-pr
description: Comprehensive PR analysis for merge decisions - compliance, code review, regressions, and test coverage
---

# check-last-pr

## What this skill does

**Comprehensive PR analysis** for merge decisions:

1. **Auto-detects SCC, VTT, and/or DFXP flow** from changed files
2. **Spec compliance checking** - only NEW issues introduced by the PR (not pre-existing), checked against `scc_specs_summary.md`, `vtt_specs_summary.md`, or `dfxp_specs_summary.md`
3. **Full code review** - regressions, breaking changes, and missing tests
4. **Change analysis** - explains what the changes do and how they solve the stated issue
5. **Clear recommendation**: can be merged / needs work / do not merge

## Usage

```bash
/check-last-pr
```

Auto-fetches PR for current branch and generates comprehensive review.

---

## Implementation

```python
#!/usr/bin/env python3
import os, re, subprocess, json
from datetime import datetime

print("="*80)
print("COMPREHENSIVE PR REVIEW")
print("="*80)

# ===== HELPERS =====
class _FakeResult:
    returncode = 127
    stdout = ""
    stderr = ""

def run(cmd, check=False):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, check=check)
    except FileNotFoundError:
        r = _FakeResult()
        r.stderr = f"Command not found: {cmd[0]}"
        return r

def is_test_file(path):
    return (
        '/tests/' in f'/{path}' or
        path.startswith('tests/') or
        os.path.basename(path).startswith('test_')
    )

def detect_base_branch():
    for branch in ['main', 'master']:
        r = run(['git', 'rev-parse', '--verify', f'origin/{branch}'])
        if r.returncode == 0:
            return branch
    return 'main'

# ===== GET PR INFO =====
print("\n[1/8] Getting PR information...")

pr_number = None
pr_title = "Unknown"
pr_ref = None

remote_url = run(['git', 'remote', 'get-url', 'origin']).stdout.strip()
repo_match = re.search(r'[:/]([^/]+/[^/]+?)(?:\.git)?$', remote_url)
repo_slug = repo_match.group(1) if repo_match else None

if repo_slug:
    base_branch = detect_base_branch()
    api_url = f'https://api.github.com/repos/{repo_slug}/pulls?state=open&base={base_branch}&sort=created&direction=desc&per_page=1'
    r = run(['curl', '-s', '-f', api_url])
    if r.returncode == 0 and r.stdout.strip():
        try:
            data = json.loads(r.stdout)
            if data and isinstance(data, list) and len(data) > 0:
                pr_number = data[0]['number']
                pr_title = data[0].get('title', f'PR #{pr_number}')
        except (json.JSONDecodeError, KeyError, IndexError):
            pass

if pr_number:
    local_ref = f'pr-{pr_number}'
    fetch_r = run(['git', 'fetch', 'origin', f'refs/pull/{pr_number}/head:{local_ref}'])
    if fetch_r.returncode == 0:
        pr_ref = local_ref

if not pr_ref:
    pr_ref = 'HEAD'
    current_branch = run(['git', 'branch', '--show-current']).stdout.strip()
    if not pr_number:
        pr_number = current_branch
        pr_title = "Current branch"

print(f"  PR: #{pr_number} - {pr_title}")
print(f"  Ref: {pr_ref}")

# ===== FETCH LATEST BASE =====
print("\n[2/8] Fetching latest base branch...")
base_branch = detect_base_branch()
run(['git', 'fetch', 'origin', base_branch])
print(f"  Base: origin/{base_branch}")

# ===== ANALYZE FILES =====
print("\n[3/8] Analyzing changed files...")

r = run(['git', 'diff', '--name-only', f'origin/{base_branch}...{pr_ref}'])
changed_files = [f for f in r.stdout.strip().split('\n') if f]

py_files = [f for f in changed_files if f.endswith('.py')]
py_src_files = [f for f in py_files if not is_test_file(f)]
py_test_files = [f for f in py_files if is_test_file(f)]

scc_files = [f for f in py_files if re.search(r'(pycaption/scc|tests/.*scc)', f, re.I)]
vtt_files = [f for f in py_files if re.search(r'(pycaption/(webvtt|vtt)|tests/.*(webvtt|vtt))', f, re.I)]
dfxp_files = [f for f in py_files if re.search(r'(pycaption/(dfxp|geometry)|tests/.*(dfxp|ttml))', f, re.I)]

detected_flows = []
if scc_files:
    detected_flows.append('SCC')
if vtt_files:
    detected_flows.append('VTT')
if dfxp_files:
    detected_flows.append('DFXP')

flow = '+'.join(detected_flows) if detected_flows else 'NONE'

spec_paths = {}
if scc_files:
    spec_paths['SCC'] = 'ai_artifacts/specs/scc/scc_specs_summary.md'
if vtt_files:
    spec_paths['VTT'] = 'ai_artifacts/specs/vtt/vtt_specs_summary.md'
if dfxp_files:
    spec_paths['DFXP'] = 'ai_artifacts/specs/dfxp/dfxp_specs_summary.md'

print(f"  Flow: {flow} | Source: {len(py_src_files)} | Tests: {len(py_test_files)}")

# ===== PARSE DIFF WITH LINE NUMBERS =====
print("\n[4/8] Parsing diff...")

diff_result = run(['git', 'diff', f'origin/{base_branch}...{pr_ref}'])

additions, deletions, current_file = [], [], None
old_ln, new_ln = 0, 0

for raw in diff_result.stdout.split('\n'):
    if raw.startswith('diff --git'):
        m = re.search(r'b/(.+)$', raw)
        current_file = m.group(1) if m else None
    elif raw.startswith('@@'):
        m = re.search(r'-(\d+)(?:,\d+)? \+(\d+)(?:,\d+)?', raw)
        if m:
            old_ln = int(m.group(1))
            new_ln = int(m.group(2))
    elif raw.startswith('+') and not raw.startswith('+++'):
        additions.append({'file': current_file, 'line': raw[1:], 'lineno': new_ln})
        new_ln += 1
    elif raw.startswith('-') and not raw.startswith('---'):
        deletions.append({'file': current_file, 'line': raw[1:], 'lineno': old_ln})
        old_ln += 1
    elif not raw.startswith('\\'):
        old_ln += 1
        new_ln += 1

print(f"  +{len(additions)} -{len(deletions)} lines")

# ===== SECTION 1: COMPLIANCE CHECK (NEW ISSUES ONLY) =====
print("\n[5/8] Compliance check - scanning for NEW issues introduced by PR...")

compliance_issues = []

scan_adds = [a for a in additions
             if a['file'] and a['file'].endswith('.py') and not is_test_file(a['file'])]

deleted_normalized = set()
for d in deletions:
    if d['file'] and d['file'].endswith('.py') and not is_test_file(d['file']):
        deleted_normalized.add(re.sub(r'\s+', ' ', d['line'].strip()))

def is_truly_new(add_line):
    stripped = add_line.strip()
    if not stripped:
        return False
    return re.sub(r'\s+', ' ', stripped) not in deleted_normalized

# --- SCC compliance checks ---
if 'SCC' in flow:
    for add in scan_adds:
        if 'scc' not in add['file'].lower():
            continue
        line = add['line']
        if not is_truly_new(line):
            continue

        # RULE-FMT-001: Scenarist_SCC V1.0 header must be case-sensitive
        if re.search(r'Scenarist[_ ]?SCC', line, re.I) and '.lower()' in line:
            compliance_issues.append({
                'severity': 'HIGH', 'rule': 'RULE-FMT-001', 'flow': 'SCC',
                'issue': 'Case-insensitive SCC header check',
                'detail': 'Header must be matched case-sensitive per spec',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Remove .lower() and compare exact "Scenarist_SCC V1.0"'})

        # RULE-TMC-001: timecode HH:MM:SS:FF or HH:MM:SS;FF
        tc_m = re.search(r"['\"](\d{2}:\d{2}:\d{2}[:;.,]\d{2})['\"]", line)
        if tc_m and tc_m.group(1)[8] not in (':', ';'):
            compliance_issues.append({
                'severity': 'HIGH', 'rule': 'RULE-TMC-001', 'flow': 'SCC',
                'issue': 'Invalid SCC timecode separator',
                'detail': f"Timecode '{tc_m.group(1)}' uses invalid separator; must use ':' (NDF) or ';' (DF)",
                'file': add['file'], 'lineno': add['lineno'],
                'fix': "Use ':' for non-drop-frame or ';' for drop-frame"})

        # RULE-CHR-001: new extended char mapping without channel awareness
        if (re.search(r'extended.*char.*[{=:]', line, re.I)
                and not re.search(r'\bin\s+EXTENDED_CHARS\b', line)
                and 'channel' not in line.lower()):
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'RULE-CHR-001', 'flow': 'SCC',
                'issue': 'Extended character mapping without channel check',
                'detail': 'Extended characters are channel-specific; new mappings must account for channel',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Ensure extended char mapping includes channel-specific byte prefixes'})

        # RULE-CMD-001: control codes must be sent as pairs (2 bytes)
        if re.search(r'(0x[0-9a-f]{2})\s*(?!,\s*0x)', line, re.I) and 'control' in line.lower():
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'RULE-CMD-001', 'flow': 'SCC',
                'issue': 'Control code may not be paired',
                'detail': 'SCC control codes must always be sent as byte pairs',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Ensure control codes are always emitted as 2-byte pairs'})

# --- VTT compliance checks ---
if 'VTT' in flow:
    for add in scan_adds:
        if 'vtt' not in add['file'].lower() and 'webvtt' not in add['file'].lower():
            continue
        line = add['line']
        if not is_truly_new(line):
            continue

        # RULE-FMT-001: WEBVTT header
        if re.search(r"['\"]WEBVTT['\"]", line) and '==' in line and '.strip()' not in line:
            compliance_issues.append({
                'severity': 'HIGH', 'rule': 'RULE-FMT-001', 'flow': 'VTT',
                'issue': 'Weak WEBVTT header check',
                'detail': 'Header may have trailing whitespace/text; use .strip() or startswith',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Use line.startswith("WEBVTT") or strip before compare'})

        # RULE-CUE-001: cue arrow must be " --> " with spaces
        if re.search(r"['\"]-->['\"]", line) and not re.search(r"['\"] --> ['\"]", line):
            compliance_issues.append({
                'severity': 'HIGH', 'rule': 'RULE-CUE-001', 'flow': 'VTT',
                'issue': 'Cue separator missing required spaces',
                'detail': 'Cue timing separator must be " --> " (space-arrow-space)',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Use " --> " with surrounding spaces'})

        # RULE-TIME-003: milliseconds need exactly 3 digits
        ts_m = re.search(r"['\"]?\d{2}:\d{2}:\d{2}\.(\d+)['\"]?", line)
        if ts_m and len(ts_m.group(1)) != 3:
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'RULE-TIME-003', 'flow': 'VTT',
                'issue': 'WebVTT milliseconds must be exactly 3 digits',
                'detail': f"Found {len(ts_m.group(1))} digits instead of 3",
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Use %03d or zero-pad milliseconds to 3 digits'})

        # RULE-TIME-001: timestamp format [HH:]MM:SS.mmm (dot not colon before ms)
        if re.search(r'\d{2}:\d{2}:\d{2}:\d{3}', line) and 'vtt' in add['file'].lower():
            compliance_issues.append({
                'severity': 'HIGH', 'rule': 'RULE-TIME-001', 'flow': 'VTT',
                'issue': 'Wrong timestamp separator before milliseconds',
                'detail': 'WebVTT uses dot (.) before milliseconds, not colon (:)',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Use HH:MM:SS.mmm format (dot before milliseconds)'})

        # RULE-FMT-004: blank line required after header
        if re.search(r'WEBVTT.*\\n[^\\n]', line):
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'RULE-FMT-004', 'flow': 'VTT',
                'issue': 'Missing blank line after WEBVTT header',
                'detail': 'Two or more line terminators must follow the header',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Ensure blank line between header and first content block'})

# --- DFXP compliance checks ---
if 'DFXP' in flow:
    for add in scan_adds:
        if not re.search(r'dfxp|geometry', add['file'].lower()):
            continue
        line = add['line']
        if not is_truly_new(line):
            continue

        # RULE-TIME-002: Hardcoded frame rate /30 instead of ttp:frameRate
        if re.search(r'/\s*30\s*\*|/\s*30\.0', line) and ('frame' in line.lower() or 'microsecond' in line.lower()):
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'RULE-TIME-002', 'flow': 'DFXP',
                'issue': 'Hardcoded frame rate division by 30',
                'detail': 'Frame timing should use ttp:frameRate from the document, not hardcoded 30',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Read ttp:frameRate from <tt> element and use that value for frame division'})

        # RULE-TIME-TICK: NotImplementedError for tick metric
        if re.search(r'NotImplementedError.*tick|raise.*NotImplemented.*tick', line, re.I):
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'RULE-TIME-009', 'flow': 'DFXP',
                'issue': 'Tick time metric raises NotImplementedError',
                'detail': 'Offset tick time (Nt) is recognized but not computed',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Implement tick-to-microseconds using ttp:tickRate parameter'})

        # RULE-STY-011: tts:display must not be confused with tts:displayAlign
        if re.search(r'tts:display(?!Align)\b', line) and re.search(r'tts:displayAlign', line):
            compliance_issues.append({
                'severity': 'HIGH', 'rule': 'RULE-STY-011', 'flow': 'DFXP',
                'issue': 'tts:display and tts:displayAlign confused',
                'detail': 'tts:display (auto|none) is distinct from tts:displayAlign (before|center|after)',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Handle tts:display and tts:displayAlign as separate attributes'})

        # RULE-DOC-003: xml:lang silent fallback without validation
        if re.search(r'\.get\s*\(\s*["\']xml:lang["\'].*DEFAULT', line):
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'RULE-DOC-003', 'flow': 'DFXP',
                'issue': 'xml:lang with silent fallback, no validation',
                'detail': 'xml:lang falls back to default without BCP-47 validation',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Validate xml:lang value is a valid BCP-47 language tag'})

        # RULE-STY-002: tts:backgroundColor not implemented
        if re.search(r'tts:backgroundColor|background.*[Cc]olor', line) and 'dfxp' in add['file'].lower():
            if re.search(r'elif.*arg.*lower.*==.*"tts:', line):
                compliance_issues.append({
                    'severity': 'MEDIUM', 'rule': 'RULE-STY-002', 'flow': 'DFXP',
                    'issue': 'tts:backgroundColor support may be incomplete',
                    'detail': 'tts:backgroundColor is not currently implemented; new style handling should include it',
                    'file': add['file'], 'lineno': add['lineno'],
                    'fix': 'Add tts:backgroundColor to _convert_style() and _recreate_style()'})

        # RULE-VAL-004: CaptionReadNoCaptions must be raised for empty files
        if re.search(r'is_empty|CaptionReadNoCaptions', line) and 'return' in line.lower() and 'none' in line.lower():
            compliance_issues.append({
                'severity': 'HIGH', 'rule': 'RULE-VAL-004', 'flow': 'DFXP',
                'issue': 'Empty caption file should raise, not return None',
                'detail': 'Per spec, empty/invalid DFXP files must raise CaptionReadNoCaptions',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Raise CaptionReadNoCaptions("empty caption file") instead of returning None'})

        # IMPL-008: XML escaping - using string concatenation instead of xml.sax.saxutils.escape
        if re.search(r'\.replace\s*\(\s*["\']&["\']', line) and 'dfxp' in add['file'].lower():
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'IMPL-008', 'flow': 'DFXP',
                'issue': 'Manual XML escaping instead of xml.sax.saxutils.escape',
                'detail': 'Manual .replace() for XML entities is error-prone and may miss edge cases',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Use xml.sax.saxutils.escape() for XML character escaping'})

        # RULE-DOC-001: detect() using substring instead of proper XML check
        if re.search(r'"</tt>".*in\s+content|content.*"</tt>"', line, re.I):
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'RULE-DOC-001', 'flow': 'DFXP',
                'issue': 'DFXP detection uses substring check',
                'detail': '"</tt>" in content matches anywhere, not proper XML root validation',
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Use proper XML parsing or at least check for root <tt> element'})

print(f"  Found: {len(compliance_issues)} NEW compliance issues")

# ===== SECTION 2: CODE REVIEW =====
print("\n[6/8] Code review (regressions, breaking changes, test coverage)...")

code_review_findings = []

def normalize_sig(params):
    s = re.sub(r'\s+', ' ', params.replace("'", '"')).strip()
    s = re.sub(r'\s*=\s*', '=', s)
    s = re.sub(r'\s*,\s*', ',', s)
    return s

sig_pattern = re.compile(r'^\s*def\s+(\w+)\s*\((.*?)\)\s*(?:->.*?)?:')

modified_py_src = set()
for f in py_src_files:
    if any(a['file'] == f for a in additions) and any(d['file'] == f for d in deletions):
        modified_py_src.add(f)

# --- A. Removed public API ---
seen_removed = set()
for d in deletions:
    if d['file'] not in modified_py_src:
        continue
    stripped = d['line'].lstrip()
    m = re.match(r'^(class|def)\s+(\w+)', stripped)
    if not m:
        continue
    entity_type, name = m.group(1), m.group(2)
    if name.startswith('_'):
        continue
    key = (d['file'], entity_type, name)
    if key in seen_removed:
        continue
    re_added = any(
        re.match(rf'^\s*{entity_type}\s+{re.escape(name)}\b', a['line'])
        for a in additions if a['file'] == d['file']
    )
    if re_added:
        continue
    seen_removed.add(key)
    code_review_findings.append({
        'category': 'REGRESSION',
        'type': f'REMOVED_PUBLIC_{entity_type.upper()}',
        'severity': 'CRITICAL',
        'file': d['file'], 'lineno': d['lineno'],
        'detail': f'Public {entity_type} removed: {name}',
        'impact': 'Breaking API change - external callers will break'})

# --- B. Changed function signatures ---
seen_sig = set()

for d in deletions:
    if d['file'] not in modified_py_src:
        continue
    m = sig_pattern.match(d['line'])
    if not m:
        continue
    func_name, old_params = m.group(1), m.group(2)
    old_norm = normalize_sig(old_params)

    same_func_adds = [
        (a, sig_pattern.match(a['line']))
        for a in additions
        if a['file'] == d['file'] and sig_pattern.match(a['line'])
        and sig_pattern.match(a['line']).group(1) == func_name
    ]

    if not same_func_adds:
        continue
    has_exact = any(normalize_sig(am.group(2)) == old_norm for _, am in same_func_adds)
    if has_exact:
        continue

    key = (d['file'], func_name, old_norm)
    if key in seen_sig:
        continue
    seen_sig.add(key)

    new_params = same_func_adds[0][1].group(2)
    code_review_findings.append({
        'category': 'REGRESSION',
        'type': 'CHANGED_SIGNATURE',
        'severity': 'HIGH',
        'file': d['file'], 'lineno': d['lineno'],
        'detail': f'{func_name}({old_params}) -> ({new_params})',
        'impact': 'May break callers that rely on parameter names/defaults'})

# --- C. Removed validation (raise/assert) without replacement ---
add_by_file = {}
for a in additions:
    add_by_file.setdefault(a['file'], []).append(a['line'])

for d in deletions:
    if d['file'] not in modified_py_src:
        continue
    stripped = d['line'].strip()
    if not re.match(r'^(raise|assert)\b', stripped):
        continue
    norm = re.sub(r'["\']', '"', re.sub(r'\s+', ' ', stripped))
    file_adds = add_by_file.get(d['file'], [])
    if any(re.sub(r'["\']', '"', re.sub(r'\s+', ' ', a.strip())) == norm for a in file_adds):
        continue
    exc_m = re.match(r'raise\s+(\w+)', stripped)
    if exc_m:
        exc_type = exc_m.group(1)
        if any(f'raise {exc_type}' in a for a in file_adds):
            continue
    code_review_findings.append({
        'category': 'REGRESSION',
        'type': 'REMOVED_VALIDATION',
        'severity': 'HIGH',
        'file': d['file'], 'lineno': d['lineno'],
        'detail': stripped[:100],
        'impact': 'Validation removed - may accept previously-rejected input'})

# --- D. Missing tests for modified source files ---
def extract_public_symbols(src_file):
    symbols = set()
    for a in additions:
        if a['file'] != src_file:
            continue
        m = re.match(r'^\s*(class|def)\s+(\w+)', a['line'])
        if m and not m.group(2).startswith('_'):
            symbols.add(m.group(2))
    return symbols

def extract_module_name(src_path):
    return src_path.replace('.py', '').replace('/', '.')

def find_test_for(src):
    base = os.path.basename(src).replace('.py', '')

    for t in py_test_files:
        tbase = os.path.basename(t).replace('.py', '').replace('test_', '')
        if tbase == base or base in tbase or tbase in base:
            return t

    src_symbols = extract_public_symbols(src)
    for d in deletions:
        if d['file'] != src:
            continue
        m = re.match(r'^\s*(class|def)\s+(\w+)', d['line'])
        if m and not m.group(2).startswith('_'):
            src_symbols.add(m.group(2))
    module_name = extract_module_name(src)
    parent_module = os.path.dirname(src).replace('/', '.')

    for t in py_test_files:
        r = run(['git', 'show', f'{pr_ref}:{t}'])
        if r.returncode != 0:
            continue
        full_test_text = r.stdout
        if module_name in full_test_text or parent_module in full_test_text:
            return t
        for sym in src_symbols:
            if re.search(rf'\b{re.escape(sym)}\b', full_test_text):
                return t

    return None

for src in modified_py_src:
    if os.path.basename(src) == '__init__.py':
        continue
    test = find_test_for(src)
    if not test:
        code_review_findings.append({
            'category': 'MISSING_TEST',
            'type': 'NO_TEST_UPDATE',
            'severity': 'HIGH',
            'file': src, 'lineno': 0,
            'detail': 'Source modified but no corresponding test file was updated',
            'impact': 'Regression risk - changes are not verified by tests'})

# --- E. New public functions without tests ---
new_funcs = {}
for a in additions:
    if a['file'] not in py_src_files or is_test_file(a['file']):
        continue
    m = sig_pattern.match(a['line'])
    if not m:
        continue
    name = m.group(1)
    if name.startswith('_'):
        continue
    key = (a['file'], name)
    if key not in new_funcs:
        was_present = any(sig_pattern.match(d['line']) and sig_pattern.match(d['line']).group(1) == name
                          for d in deletions if d['file'] == a['file'])
        if not was_present:
            new_funcs[key] = a['lineno']

for (src, func), lineno in new_funcs.items():
    word_re = re.compile(rf'\b{re.escape(func)}\b')
    found_in_any_test = False
    for t in py_test_files:
        r = run(['git', 'show', f'{pr_ref}:{t}'])
        if r.returncode == 0 and word_re.search(r.stdout):
            found_in_any_test = True
            break
    if not found_in_any_test:
        test = find_test_for(src)
        test_name = os.path.basename(test) if test else 'any test file'
        code_review_findings.append({
            'category': 'MISSING_TEST',
            'type': 'NEW_FUNC_UNTESTED',
            'severity': 'MEDIUM',
            'file': src, 'lineno': lineno,
            'detail': f'New function `{func}` has no reference in {test_name}',
            'impact': 'Untested new code'})

print(f"  Found: {len(code_review_findings)} findings")

# ===== CODE QUALITY REVIEW =====
print("\n[7/8] Code quality review...")

quality_issues = []

for add in additions:
    if not add['file'] or not add['file'].endswith('.py'):
        continue
    line = add['line']

    # Bare except
    if re.search(r'except\s*:', line) and 'except Exception' not in line:
        quality_issues.append({
            'type': 'BARE_EXCEPT', 'severity': 'MEDIUM',
            'file': add['file'],
            'detail': 'Bare except clause catches all exceptions',
            'recommendation': 'Use specific exception types'})

    # Magic numbers (only flag when used inline, not in constants/comments/strings/imports)
    if re.search(r'\b(32|15|30|29\.97)\b', line):
        skip_magic = (
            '#' in line
            or 'SPEC' in line
            or re.match(r'^\s*[A-Z_]+\s*=', line)  # constant definition
            or re.match(r'^\s*(import|from)\s', line)
            or re.match(r'^\s*def\s', line)
            or re.search(r'range\(', line)
        )
        if not skip_magic:
            quality_issues.append({
                'type': 'MAGIC_NUMBER', 'severity': 'LOW',
                'file': add['file'],
                'detail': f"Magic number in: {line[:60]}",
                'recommendation': 'Use named constant'})

print(f"  Found: {len(quality_issues)} code quality suggestions")

# ===== SECTION 3: CHANGE ANALYSIS =====
print("\n[8/8] Analyzing changes - what they do and how they solve the issue...")

commit_log_r = run(['git', 'log', '--format=%s%n%b---', f'origin/{base_branch}..{pr_ref}'])
commit_messages = commit_log_r.stdout.strip() if commit_log_r.returncode == 0 else ''

new_files = []
modified_files = []
deleted_files = []

for f in py_src_files:
    has_adds = any(a['file'] == f for a in additions)
    has_dels = any(d['file'] == f for d in deletions)
    if has_adds and not has_dels:
        new_files.append(f)
    elif has_adds and has_dels:
        modified_files.append(f)
    elif not has_adds and has_dels:
        deleted_files.append(f)

change_details = []

for f in modified_files:
    file_adds = [a for a in additions if a['file'] == f]
    file_dels = [d for d in deletions if d['file'] == f]

    new_funcs_in_file = []
    modified_funcs_in_file = []
    removed_funcs_in_file = []

    del_func_names = set()
    add_func_names = set()

    for d in file_dels:
        m = sig_pattern.match(d['line'])
        if m:
            del_func_names.add(m.group(1))
    for a in file_adds:
        m = sig_pattern.match(a['line'])
        if m:
            add_func_names.add(m.group(1))

    for name in add_func_names & del_func_names:
        modified_funcs_in_file.append(name)
    for name in add_func_names - del_func_names:
        new_funcs_in_file.append(name)
    for name in del_func_names - add_func_names:
        removed_funcs_in_file.append(name)

    detail = {'file': f}
    if new_funcs_in_file:
        detail['new'] = new_funcs_in_file
    if modified_funcs_in_file:
        detail['modified'] = modified_funcs_in_file
    if removed_funcs_in_file:
        detail['removed'] = removed_funcs_in_file
    if not (new_funcs_in_file or modified_funcs_in_file or removed_funcs_in_file):
        add_count = len(file_adds)
        del_count = len(file_dels)
        detail['summary'] = f'+{add_count}/-{del_count} lines (logic/refactoring changes)'
    change_details.append(detail)

for f in new_files:
    file_adds = [a for a in additions if a['file'] == f]
    funcs = []
    for a in file_adds:
        m = sig_pattern.match(a['line'])
        if m and not m.group(1).startswith('_'):
            funcs.append(m.group(1))
    detail = {'file': f, 'is_new': True}
    if funcs:
        detail['new'] = funcs
    change_details.append(detail)

test_details = []
for f in py_test_files:
    file_adds = [a for a in additions if a['file'] == f]
    test_classes = []
    test_funcs = []
    for a in file_adds:
        cls_m = re.match(r'^\s*class\s+(Test\w+)', a['line'])
        func_m = re.match(r'^\s*def\s+(test_\w+)', a['line'])
        if cls_m:
            test_classes.append(cls_m.group(1))
        elif func_m:
            test_funcs.append(func_m.group(1))
    if test_classes or test_funcs:
        test_details.append({
            'file': f,
            'classes': test_classes,
            'functions': test_funcs
        })

print(f"  Source: {len(new_files)} new, {len(modified_files)} modified, {len(deleted_files)} deleted")
print(f"  Test changes: {len(test_details)} test files with new tests")

# ===== RECOMMENDATION + REPORT =====
print("\n  Generating report...")

all_issues = compliance_issues + code_review_findings
critical = [i for i in all_issues if i.get('severity') == 'CRITICAL']
high = [i for i in all_issues if i.get('severity') == 'HIGH']
medium = [i for i in all_issues if i.get('severity') == 'MEDIUM']

regressions = [f for f in code_review_findings if f['category'] == 'REGRESSION']
missing_tests = [f for f in code_review_findings if f['category'] == 'MISSING_TEST']

if critical:
    recommendation = 'DO NOT MERGE'
    rec_icon = '\U0001f534'
    rec_reason = f'{len(critical)} critical issue(s) found that must be resolved before merging.'
elif high:
    recommendation = 'NEEDS WORK'
    rec_icon = '\U0001f7e0'
    rec_reason = f'{len(high)} high-severity issue(s) should be addressed before merging.'
elif medium:
    recommendation = 'CAN BE MERGED'
    rec_icon = '\U0001f7e1'
    rec_reason = f'{len(medium)} medium-severity issue(s) found. Consider addressing them but not blocking.'
else:
    recommendation = 'CAN BE MERGED'
    rec_icon = '\U0001f7e2'
    rec_reason = 'No issues found. Code looks good.'

# ===== BUILD REPORT =====
date = datetime.now().strftime("%Y-%m-%d")
safe_branch = re.sub(r'[^\w.-]', '_', str(pr_number))
if len(detected_flows) == 1:
    flow_dir = detected_flows[0].lower()
elif len(detected_flows) > 1:
    flow_dir = 'mixed'
else:
    flow_dir = None
report_dir = f"ai_artifacts/compliance_checks/{flow_dir}" if flow_dir else "ai_artifacts/compliance_checks"
os.makedirs(report_dir, exist_ok=True)
report_path = f"{report_dir}/pr_{safe_branch}_review_{date}.md"

if spec_paths:
    spec_used = ' + '.join(f'`{p}`' for p in spec_paths.values())
else:
    spec_used = 'N/A (no SCC/VTT/DFXP files changed)'

report = f"""# PR #{pr_number} - {pr_title}

**Generated**: {date} at {datetime.now().strftime("%H:%M")}
**Flow**: {flow}
**Base**: origin/{base_branch}
**Spec input**: {spec_used}
**Files changed**: {len(changed_files)} ({len(py_src_files)} source, {len(py_test_files)} test)
**Lines**: +{len(additions)} / -{len(deletions)}

---

## Section 1: Compliance Check

Checks **only new code introduced by this PR** against the {flow} specification.
Pre-existing issues in unchanged code are not reported.

"""

if flow == 'NONE':
    report += "No SCC/VTT/DFXP source files changed - compliance check not applicable.\n\n"
elif compliance_issues:
    report += f"**{len(compliance_issues)} new compliance issue(s) found:**\n\n"
    for i, issue in enumerate(compliance_issues, 1):
        report += f"""### {i}. [{issue['severity']}] {issue['issue']}
- **Rule**: `{issue['rule']}` ({issue['flow']})
- **File**: `{issue['file']}:{issue['lineno']}`
- **Detail**: {issue['detail']}
- **Fix**: {issue['fix']}

"""
else:
    report += f"No new compliance issues introduced by this PR against the {flow} spec.\n\n"

report += f"""---

## Section 2: Code Review

Full code review covering regressions, breaking changes, and test coverage.

"""

report += f"### Regressions & Breaking Changes ({len(regressions)})\n\n"
if regressions:
    for i, f in enumerate(regressions, 1):
        report += f"""**{i}. [{f['severity']}] {f['type']}**
- **File**: `{f['file']}:{f['lineno']}`
- **Detail**: {f['detail']}
- **Impact**: {f['impact']}

"""
else:
    report += "No regressions or breaking changes detected.\n\n"

report += f"### Test Coverage ({len(missing_tests)})\n\n"
if missing_tests:
    for i, f in enumerate(missing_tests, 1):
        loc = f"`{f['file']}:{f['lineno']}`" if f['lineno'] else f"`{f['file']}`"
        report += f"""**{i}. [{f['severity']}] {f['type']}**
- **File**: {loc}
- **Detail**: {f['detail']}
- **Impact**: {f['impact']}

"""
else:
    report += "All changes have corresponding test coverage.\n\n"

report += f"""### Issues Summary

| Severity | Count |
|----------|-------|
| Critical | {len(critical)} |
| High | {len(high)} |
| Medium | {len(medium)} |
| **Total** | **{len(all_issues)}** |

"""

report += """---

## Section 3: Change Analysis

What the PR changes do and how they address the stated issue.

"""

if commit_messages:
    report += "### Commit Messages\n\n"
    for msg_block in commit_messages.split('---'):
        msg = msg_block.strip()
        if not msg:
            continue
        lines = msg.split('\n')
        subject = lines[0].strip()
        body = '\n'.join(l.strip() for l in lines[1:] if l.strip())
        if subject:
            report += f"- **{subject}**"
            if body:
                report += f"\n  {body}"
            report += "\n"
    report += "\n"

if change_details:
    report += "### Source Changes\n\n"
    for cd in change_details:
        is_new = cd.get('is_new', False)
        label = "(new file)" if is_new else ""
        report += f"**`{cd['file']}`** {label}\n"
        if cd.get('new'):
            report += f"- New functions: `{'`, `'.join(cd['new'])}`\n"
        if cd.get('modified'):
            report += f"- Modified functions: `{'`, `'.join(cd['modified'])}`\n"
        if cd.get('removed'):
            report += f"- Removed functions: `{'`, `'.join(cd['removed'])}`\n"
        if cd.get('summary'):
            report += f"- {cd['summary']}\n"
        report += "\n"

if deleted_files:
    report += "**Deleted files:**\n"
    for f in deleted_files:
        report += f"- `{f}`\n"
    report += "\n"

if test_details:
    report += "### Test Changes\n\n"
    for td in test_details:
        report += f"**`{td['file']}`**\n"
        if td['classes']:
            report += f"- New test classes: `{'`, `'.join(td['classes'])}`\n"
        if td['functions']:
            funcs = td['functions']
            if len(funcs) <= 10:
                report += f"- New test methods: `{'`, `'.join(funcs)}`\n"
            else:
                report += f"- New test methods: {len(funcs)} ({', '.join(f'`{f}`' for f in funcs[:5])}, ...)\n"
        report += "\n"

report += "### Correctness Assessment\n\n"

if not all_issues:
    report += "The changes are correct:\n\n"
    if change_details:
        for cd in change_details:
            if cd.get('modified'):
                report += f"- Modifications to `{'`, `'.join(cd['modified'])}` in `{cd['file']}` "
                report += "align with the stated objective and do not introduce regressions.\n"
            if cd.get('new'):
                report += f"- New functions `{'`, `'.join(cd['new'])}` in `{cd['file']}` "
                report += "are properly implemented and tested.\n"
    if test_details:
        total_tests = sum(len(td['functions']) for td in test_details)
        report += f"- {total_tests} new test method(s) verify the changes.\n"
    if not change_details and not test_details:
        report += "- All changes appear correct with no issues detected.\n"
    report += "\n"
else:
    report += "The changes are **partially correct** — see issues above. "
    correct_files = [cd['file'] for cd in change_details
                     if not any(i.get('file') == cd['file'] for i in all_issues)]
    if correct_files:
        report += f"Changes to `{'`, `'.join(correct_files)}` are correct. "
    issue_files = list(set(i.get('file', '') for i in all_issues if i.get('file')))
    if issue_files:
        report += f"Issues remain in `{'`, `'.join(issue_files)}`."
    report += "\n\n"

if quality_issues:
    report += f"""### Code Quality Suggestions ({len(quality_issues)})

"""
    for i, qissue in enumerate(quality_issues, 1):
        report += f"""**{i}. [{qissue['severity']}] {qissue['type']}**
- **File**: `{qissue['file']}`
- **Detail**: {qissue['detail']}
- **Recommendation**: {qissue['recommendation']}

"""

report += f"""---

## Recommendation

{rec_icon} **{recommendation}**

{rec_reason}

"""

if critical:
    report += "**Must fix before merge:**\n"
    for issue in critical:
        label = issue.get('issue') or issue.get('type', 'Issue')
        report += f"- [{issue['severity']}] {label} in `{issue['file']}`\n"
    report += "\n"

if high:
    report += "**Should fix before merge:**\n"
    for issue in high:
        label = issue.get('issue') or issue.get('type', 'Issue')
        report += f"- [{issue['severity']}] {label} in `{issue['file']}`\n"
    report += "\n"

report += f"""---
*Generated by check-last-pr skill*
"""

with open(report_path, 'w') as fh:
    fh.write(report)

print(f"\n{'='*80}")
print(f"  REVIEW COMPLETE")
print(f"{'='*80}")
print(f"  Report: {report_path}")
print(f"  Recommendation: {rec_icon} {recommendation}")
print(f"  {rec_reason}")
print(f"{'='*80}")
```
