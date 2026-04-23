---
name: check-last-pr
description: Comprehensive PR analysis for merge decisions - compliance, code review, regressions, and test coverage
---

# check-last-pr

## What this skill does

**Comprehensive PR analysis** for merge decisions:

1. **Auto-detects SCC or VTT flow** from changed files
2. **Spec compliance checking** - only NEW issues introduced by the PR (not pre-existing), checked against `scc_specs_summary.md` or `vtt_specs_summary.md`
3. **Full code review** - regressions, breaking changes, and missing tests
4. **Clear recommendation**: can be merged / needs work / do not merge

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
print("\n[1/6] Getting PR information...")

pr_number = None
pr_title = "Unknown"
pr_ref = None  # The git ref to diff (PR head commit)

# Detect repo owner/name from git remote
remote_url = run(['git', 'remote', 'get-url', 'origin']).stdout.strip()
repo_match = re.search(r'[:/]([^/]+/[^/]+?)(?:\.git)?$', remote_url)
repo_slug = repo_match.group(1) if repo_match else None

# Get the latest open PR targeting main via GitHub API
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

# Fetch the PR ref so we diff the actual PR, not the current branch
if pr_number:
    local_ref = f'pr-{pr_number}'
    fetch_r = run(['git', 'fetch', 'origin', f'refs/pull/{pr_number}/head:{local_ref}'])
    if fetch_r.returncode == 0:
        pr_ref = local_ref

# Fallback: use current branch HEAD
if not pr_ref:
    pr_ref = 'HEAD'
    current_branch = run(['git', 'branch', '--show-current']).stdout.strip()
    if not pr_number:
        pr_number = current_branch
        pr_title = "Current branch"

print(f"  PR: #{pr_number} - {pr_title}")
print(f"  Ref: {pr_ref}")

# ===== FETCH LATEST BASE =====
print("\n[2/6] Fetching latest base branch...")
base_branch = detect_base_branch()
run(['git', 'fetch', 'origin', base_branch])
print(f"  Base: origin/{base_branch}")

# ===== ANALYZE FILES =====
print("\n[3/6] Analyzing changed files...")

r = run(['git', 'diff', '--name-only', f'origin/{base_branch}...{pr_ref}'])
changed_files = [f for f in r.stdout.strip().split('\n') if f]

py_files = [f for f in changed_files if f.endswith('.py')]
py_src_files = [f for f in py_files if not is_test_file(f)]
py_test_files = [f for f in py_files if is_test_file(f)]

# Detect flow: SCC or VTT
scc_files = [f for f in py_files if re.search(r'(pycaption/scc|tests/.*scc)', f, re.I)]
vtt_files = [f for f in py_files if re.search(r'(pycaption/(webvtt|vtt)|tests/.*(webvtt|vtt))', f, re.I)]

if scc_files and not vtt_files:
    flow, spec_path = 'SCC', 'pycaption/specs/scc/scc_specs_summary.md'
elif vtt_files and not scc_files:
    flow, spec_path = 'VTT', 'pycaption/specs/vtt/vtt_specs_summary.md'
elif scc_files and vtt_files:
    flow, spec_path = 'SCC+VTT', None
else:
    flow, spec_path = 'NONE', None

print(f"  Flow: {flow} | Source: {len(py_src_files)} | Tests: {len(py_test_files)}")
```

```python
# ===== PARSE DIFF WITH LINE NUMBERS =====
print("\n[4/6] Parsing diff...")

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
```

```python
# ===== SECTION 1: COMPLIANCE CHECK (NEW ISSUES ONLY) =====
print("\n[5/6] Compliance check - scanning for NEW issues introduced by PR...")

compliance_issues = []

# Only scan additions in source files (not tests) - these are NEW code from the PR
scan_adds = [a for a in additions
             if a['file'] and a['file'].endswith('.py') and not is_test_file(a['file'])]

# Collect deleted lines for comparison - if a pattern existed before and was just moved, skip it
deleted_lines_set = set()
for d in deletions:
    if d['file'] and d['file'].endswith('.py') and not is_test_file(d['file']):
        deleted_lines_set.add(d['line'].strip())

def is_truly_new(add_line):
    """Return True only if this line is genuinely new, not just moved/reformatted."""
    stripped = add_line.strip()
    if not stripped:
        return False
    normalized = re.sub(r'\s+', ' ', stripped)
    for d in deleted_lines_set:
        if re.sub(r'\s+', ' ', d) == normalized:
            return False
    return True

# --- SCC compliance checks ---
if 'SCC' in flow:
    for add in scan_adds:
        if 'scc' not in add['file'].lower():
            continue
        line = add['line']
        if not is_truly_new(line):
            continue

        # CTRL-008: RU4 hex code
        if re.search(r"['\"]94a7['\"]", line):
            compliance_issues.append({
                'severity': 'CRITICAL', 'rule': 'CTRL-008', 'flow': 'SCC',
                'issue': 'Incorrect RU4 hex code',
                'detail': "Found '94a7'; correct code for Roll-Up 4 rows is '9427'",
                'file': add['file'], 'lineno': add['lineno'],
                'fix': "Replace '94a7' with '9427'"})

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
        # Only flag lines that define or assign extended char mappings (not dict lookups or comments)
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

print(f"  Found: {len(compliance_issues)} NEW compliance issues")
```

```python
# ===== SECTION 2: CODE REVIEW =====
print("\n[6/6] Code review (regressions, breaking changes, test coverage)...")

code_review_findings = []

def normalize_sig(params):
    s = re.sub(r'\s+', ' ', params.replace("'", '"')).strip()
    s = re.sub(r'\s*=\s*', '=', s)
    s = re.sub(r'\s*,\s*', ',', s)
    return s

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
sig_pattern = re.compile(r'^\s*def\s+(\w+)\s*\((.*?)\)\s*(?:->.*?)?:')
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
    """Extract public class/function names defined in a source file's additions."""
    symbols = set()
    for a in additions:
        if a['file'] != src_file:
            continue
        m = re.match(r'^\s*(class|def)\s+(\w+)', a['line'])
        if m and not m.group(2).startswith('_'):
            symbols.add(m.group(2))
    return symbols

def extract_module_name(src_path):
    """Get the importable module name from a source path (e.g. pycaption.scc.state_machines)."""
    parts = src_path.replace('.py', '').replace('/', '.')
    return parts

def find_test_for(src):
    """Find a test file that covers this source file.
    Strategy: 1) filename match, 2) check if any test file imports/references
    symbols from the source file or its module path."""
    base = os.path.basename(src).replace('.py', '')

    # Strategy 1: direct filename match (e.g. utils.py -> test_utils.py)
    for t in py_test_files:
        tbase = os.path.basename(t).replace('.py', '').replace('test_', '')
        if tbase == base or base in tbase or tbase in base:
            return t

    # Strategy 2: check if any test file references symbols from this source
    # We check the FULL content of test files (not just additions) because
    # tests may already exist and just not have been modified in this PR.
    src_symbols = extract_public_symbols(src)
    # Also extract symbols from deletions (modified functions still exist)
    for d in deletions:
        if d['file'] != src:
            continue
        m = re.match(r'^\s*(class|def)\s+(\w+)', d['line'])
        if m and not m.group(2).startswith('_'):
            src_symbols.add(m.group(2))
    module_name = extract_module_name(src)
    parent_module = os.path.dirname(src).replace('/', '.')

    for t in py_test_files:
        # Read test file content from the PR ref (not working tree)
        r = run(['git', 'show', f'{pr_ref}:{t}'])
        if r.returncode != 0:
            continue
        full_test_text = r.stdout
        # Check for import of the module
        if module_name in full_test_text or parent_module in full_test_text:
            return t
        # Check for references to symbols from the source file
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
    # Search across ALL test files in the PR for the function name
    # Read from the PR ref (not working tree) to avoid false positives
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
```

```python
# ===== RECOMMENDATION + REPORT =====
print("\n  Generating report...")

all_issues = compliance_issues + code_review_findings
critical = [i for i in all_issues if i.get('severity') == 'CRITICAL']
high = [i for i in all_issues if i.get('severity') == 'HIGH']
medium = [i for i in all_issues if i.get('severity') == 'MEDIUM']

regressions = [f for f in code_review_findings if f['category'] == 'REGRESSION']
missing_tests = [f for f in code_review_findings if f['category'] == 'MISSING_TEST']

# Recommendation logic
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
flow_dir = flow.lower().replace('+', '_') if flow not in ('NONE', 'SCC+VTT') else 'mixed'
report_dir = f"pycaption/compliance_checks/{flow_dir}" if flow != 'NONE' else "pycaption/compliance_checks"
os.makedirs(report_dir, exist_ok=True)
report_path = f"{report_dir}/pr_{safe_branch}_review_{date}.md"

# Spec file used
if flow == 'SCC':
    spec_used = '`pycaption/specs/scc/scc_specs_summary.md`'
elif flow == 'VTT':
    spec_used = '`pycaption/specs/vtt/vtt_specs_summary.md`'
elif flow == 'SCC+VTT':
    spec_used = '`pycaption/specs/scc/scc_specs_summary.md` + `pycaption/specs/vtt/vtt_specs_summary.md`'
else:
    spec_used = 'N/A (no SCC/VTT files changed)'

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
    report += "No SCC/VTT source files changed - compliance check not applicable.\n\n"
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

# ===== SECTION 2: CODE REVIEW =====
report += f"""---

## Section 2: Code Review

Full code review covering regressions, breaking changes, and test coverage.

"""

# 2.1 Regressions & Breaking Changes
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

# 2.2 Test Coverage
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

# 2.3 Summary table
report += f"""### Issues Summary

| Severity | Count |
|----------|-------|
| Critical | {len(critical)} |
| High | {len(high)} |
| Medium | {len(medium)} |
| **Total** | **{len(all_issues)}** |

"""

# ===== RECOMMENDATION =====
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
