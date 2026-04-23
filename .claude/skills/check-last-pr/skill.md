---
name: check-last-pr
description: Comprehensive PR analysis for merge decisions - compliance, code review, regressions, and test coverage
---

# check-last-pr

## What this skill does

**Comprehensive PR analysis** for merge decisions:

1. **Auto-detects SCC or VTT flow** (DFXP support coming later)
2. **Spec compliance checking** against `scc_specs_summary.md` or `vtt_specs_summary.md`
3. **Full code review** - regressions, breaking changes, and missing tests in one section
4. **Risk scoring** with clear merge recommendation
5. **Actionable report** saved to compliance folder

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
    """Only files under a tests/ directory or starting with test_"""
    return (
        '/tests/' in f'/{path}' or
        path.startswith('tests/') or
        os.path.basename(path).startswith('test_')
    )

def detect_base_branch():
    """Prefer main, fall back to master"""
    for branch in ['main', 'master']:
        r = run(['git', 'rev-parse', '--verify', f'origin/{branch}'])
        if r.returncode == 0:
            return branch
    return 'main'

# ===== GET PR INFO =====
print("\n[1/7] Getting PR information...")

current_branch = run(['git', 'branch', '--show-current']).stdout.strip()
pr_number, pr_title = current_branch, "Current branch"

# Fetch PR by HEAD branch, not "newest open across repo"
r = run(['gh', 'pr', 'list', '--head', current_branch, '--state', 'open',
         '--limit', '1', '--json', 'number,title'])
if r.returncode == 0 and r.stdout.strip():
    try:
        data = json.loads(r.stdout)
        if data:
            pr_number, pr_title = data[0]['number'], data[0]['title']
    except json.JSONDecodeError:
        pass

print(f"  PR: #{pr_number} - {pr_title}")

# ===== FETCH LATEST BASE =====
print("\n[2/7] Fetching latest base branch...")
base_branch = detect_base_branch()
run(['git', 'fetch', 'origin', base_branch])
print(f"  Base: origin/{base_branch}")

# ===== ANALYZE FILES =====
print("\n[3/7] Analyzing changed files...")

r = run(['git', 'diff', '--name-only', f'origin/{base_branch}...HEAD'])
changed_files = [f for f in r.stdout.strip().split('\n') if f]

py_files = [f for f in changed_files if f.endswith('.py')]
py_src_files = [f for f in py_files if not is_test_file(f)]
py_test_files = [f for f in py_files if is_test_file(f)]

# Detect flow: SCC or VTT (DFXP excluded for now)
scc_files = [f for f in py_files if re.search(r'(pycaption/scc|tests/.*scc)', f, re.I)]
vtt_files = [f for f in py_files if re.search(r'(pycaption/(webvtt|vtt)|tests/.*(webvtt|vtt))', f, re.I)]

if scc_files and not vtt_files:
    flow, spec_path = 'SCC', 'pycaption/specs/scc/scc_specs_summary.md'
elif vtt_files and not scc_files:
    flow, spec_path = 'VTT', 'pycaption/specs/vtt/vtt_specs_summary.md'
elif scc_files and vtt_files:
    flow = 'SCC+VTT'
    spec_path = None  # Will check both
else:
    flow, spec_path = 'NONE', None

print(f"  Flow: {flow} | Source: {len(py_src_files)} | Tests: {len(py_test_files)}")
```

```python
# ===== PARSE DIFF WITH LINE NUMBERS =====
print("\n[4/7] Parsing diff...")

diff_result = run(['git', 'diff', f'origin/{base_branch}...HEAD'])

additions, deletions, current_file = [], [], None
old_ln, new_ln = 0, 0

for raw in diff_result.stdout.split('\n'):
    if raw.startswith('diff --git'):
        m = re.search(r'b/(.+)$', raw)
        current_file = m.group(1) if m else None
    elif raw.startswith('@@'):
        # @@ -old,count +new,count @@
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
# ===== COMPLIANCE CHECK AGAINST SPECS =====
print("\n[5/7] Compliance check against specs...")

compliance_issues = []

def load_spec_rules(path):
    """Extract rule IDs and levels from spec markdown.
    Returns dict of {rule_id: {'level': MUST/SHOULD/MAY, 'req': text}}
    """
    if not path or not os.path.exists(path):
        return {}
    text = open(path).read()
    rules = {}
    # Match: **[RULE-XXX-###]** description ... - **Level:** MUST
    pattern = re.compile(
        r'\*\*\[([A-Z]+-[A-Z]+-\d+|CTRL-\d+|IMPL-[A-Z]+-\d+)\]\*\*\s*(.+?)(?=\n\s*\*\*\[|\Z)',
        re.DOTALL
    )
    for m in pattern.finditer(text):
        rule_id = m.group(1)
        body = m.group(2)
        level_m = re.search(r'\*\*Level:\*\*\s*(MUST NOT|MUST|SHOULD|MAY)', body)
        req_m = re.search(r'\*\*Requirement:\*\*\s*(.+)', body)
        rules[rule_id] = {
            'level': level_m.group(1) if level_m else 'UNKNOWN',
            'req': req_m.group(1).strip() if req_m else body[:120].strip(),
        }
    return rules

# Load spec rules for active flow
scc_rules = load_spec_rules('pycaption/specs/scc/scc_specs_summary.md') if 'SCC' in flow else {}
vtt_rules = load_spec_rules('pycaption/specs/vtt/vtt_specs_summary.md') if 'VTT' in flow else {}

print(f"  Loaded rules: SCC={len(scc_rules)}, VTT={len(vtt_rules)}")

# Added source lines (non-test) for pattern scanning
scan_adds = [a for a in additions
             if a['file'] and a['file'].endswith('.py') and not is_test_file(a['file'])]

# --- SCC checks (anchored to spec rule IDs) ---
if 'SCC' in flow:
    for add in scan_adds:
        if 'scc' not in add['file'].lower():
            continue
        line = add['line']

        # CTRL-008 RU4 hex
        if re.search(r"['\"]94a7['\"]", line):
            compliance_issues.append({
                'severity': 'CRITICAL', 'rule': 'CTRL-008', 'flow': 'SCC',
                'issue': 'Incorrect RU4 hex code',
                'detail': "Found '94a7'; correct code for Roll-Up 4 rows is '9427'",
                'file': add['file'], 'lineno': add['lineno'],
                'fix': "Replace '94a7' with '9427'"})

        # RULE-FMT-001: Scenarist_SCC V1.0 header - case-sensitive exact match
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
                'detail': f"Timecode '{tc_m.group(1)}' - must use ':' (NDF) or ';' (DF)",
                'file': add['file'], 'lineno': add['lineno'],
                'fix': "Use ':' for non-drop-frame or ';' for drop-frame"})

# --- VTT checks (anchored to spec rule IDs) ---
if 'VTT' in flow:
    for add in scan_adds:
        if 'vtt' not in add['file'].lower() and 'webvtt' not in add['file'].lower():
            continue
        line = add['line']

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

        # RULE-TIME-003: milliseconds need exactly 3 digits - check format strings
        ts_m = re.search(r"['\"]?\d{2}:\d{2}:\d{2}\.(\d+)['\"]?", line)
        if ts_m and len(ts_m.group(1)) != 3:
            compliance_issues.append({
                'severity': 'MEDIUM', 'rule': 'RULE-TIME-003', 'flow': 'VTT',
                'issue': 'WebVTT milliseconds must be exactly 3 digits',
                'detail': f"Found {len(ts_m.group(1))} digits",
                'file': add['file'], 'lineno': add['lineno'],
                'fix': 'Use %03d or zero-pad milliseconds to 3 digits'})

print(f"  Found: {len(compliance_issues)} compliance issues")
```

```python
# ===== CODE REVIEW: REGRESSIONS + BREAKING CHANGES + MISSING TESTS =====
print("\n[6/7] Code review (regressions + test coverage)...")

code_review_findings = []

def normalize_sig(params):
    """Normalize function signature for comparison - preserves param identity."""
    s = re.sub(r'\s+', ' ', params.replace("'", '"')).strip()
    s = re.sub(r'\s*=\s*', '=', s)
    s = re.sub(r'\s*,\s*', ',', s)
    return s

# Files modified (both additions and deletions exist)
modified_py_src = set()
for f in py_src_files:
    if any(a['file'] == f for a in additions) and any(d['file'] == f for d in deletions):
        modified_py_src.add(f)

# --- A. Removed public API (class/def at module level or indented methods) ---
# Use indent-preserving check
deletion_raw = {}  # (file, lineno) -> original line
for d in deletions:
    deletion_raw[(d['file'], d['lineno'])] = d['line']

seen_removed = set()
for d in deletions:
    if d['file'] not in modified_py_src:
        continue
    # Use original line (not stripped) to detect top-level vs method
    line = d['line']
    stripped = line.lstrip()
    m = re.match(r'^(class|def)\s+(\w+)', stripped)
    if not m:
        continue
    entity_type, name = m.group(1), m.group(2)
    if name.startswith('_'):
        continue
    key = (d['file'], entity_type, name)
    if key in seen_removed:
        continue
    # Look for same entity re-added in same file
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

# --- B. Changed signature (not just formatting) ---
# Group deletions/additions by (file, func_name) to avoid cross-method matching
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

    # Find matching additions for same func in same file
    same_func_adds = [
        (a, sig_pattern.match(a['line']))
        for a in additions
        if a['file'] == d['file'] and sig_pattern.match(a['line'])
        and sig_pattern.match(a['line']).group(1) == func_name
    ]

    if not same_func_adds:
        continue  # Function was removed, handled above

    # If ANY addition has matching normalized sig, it's just formatting
    has_exact = any(normalize_sig(am.group(2)) == old_norm for _, am in same_func_adds)
    if has_exact:
        continue

    key = (d['file'], func_name, old_norm)
    if key in seen_sig:
        continue
    seen_sig.add(key)

    # Report with first addition
    new_params = same_func_adds[0][1].group(2)
    code_review_findings.append({
        'category': 'REGRESSION',
        'type': 'CHANGED_SIGNATURE',
        'severity': 'HIGH',
        'file': d['file'], 'lineno': d['lineno'],
        'detail': f'{func_name}({old_params}) → ({new_params})',
        'impact': 'May break callers that rely on parameter names/defaults'})

# --- C. Removed validation (raise / assert) without equivalent ---
add_by_file = {}
for a in additions:
    add_by_file.setdefault(a['file'], []).append(a['line'])

for d in deletions:
    if d['file'] not in modified_py_src:
        continue
    stripped = d['line'].strip()
    if not re.match(r'^(raise|assert)\b', stripped):
        continue
    # Check if equivalent raise/assert exists in additions
    norm = re.sub(r'["\']', '"', re.sub(r'\s+', ' ', stripped))
    file_adds = add_by_file.get(d['file'], [])
    if any(re.sub(r'["\']', '"', re.sub(r'\s+', ' ', a.strip())) == norm for a in file_adds):
        continue
    # Look for same exception type
    exc_m = re.match(r'raise\s+(\w+)', stripped)
    if exc_m:
        exc_type = exc_m.group(1)
        if any(f'raise {exc_type}' in a for a in file_adds):
            continue  # Same exception type still raised somewhere
    code_review_findings.append({
        'category': 'REGRESSION',
        'type': 'REMOVED_VALIDATION',
        'severity': 'HIGH',
        'file': d['file'], 'lineno': d['lineno'],
        'detail': stripped[:100],
        'impact': 'Validation removed - may accept previously-rejected input'})

# --- D. Missing tests for modified source files ---
def find_test_for(src):
    """Find a test file that likely tests this source file."""
    base = os.path.basename(src).replace('.py', '')
    for t in py_test_files:
        tbase = os.path.basename(t).replace('.py', '').replace('test_', '')
        if tbase == base or base in tbase or tbase in base:
            return t
    return None

for src in modified_py_src:
    # Skip __init__.py and pure type/constant modules
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
# Use first addition line per function (indent-aware)
new_funcs = {}  # (file, name) -> lineno
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
        # Only flag if not in deletions (truly new)
        was_present = any(sig_pattern.match(d['line']) and sig_pattern.match(d['line']).group(1) == name
                          for d in deletions if d['file'] == a['file'])
        if not was_present:
            new_funcs[key] = a['lineno']

for (src, func), lineno in new_funcs.items():
    test = find_test_for(src)
    if not test:
        continue  # Already flagged above
    # Look for reference to function name in the matching test file's additions
    # Require word-boundary match, not substring
    word_re = re.compile(rf'\b{re.escape(func)}\b')
    test_adds = [a['line'] for a in additions if a['file'] == test]
    if not any(word_re.search(ta) for ta in test_adds):
        code_review_findings.append({
            'category': 'MISSING_TEST',
            'type': 'NEW_FUNC_UNTESTED',
            'severity': 'MEDIUM',
            'file': src, 'lineno': lineno,
            'detail': f'New function `{func}` has no reference in {os.path.basename(test)}',
            'impact': 'Untested new code'})

print(f"  Found: {len(code_review_findings)} findings")
```

```python
# ===== RISK SCORING + REPORT =====
print("\n[7/7] Risk scoring & report...")

all_issues = compliance_issues + code_review_findings
critical = [i for i in all_issues if i.get('severity') == 'CRITICAL']
high = [i for i in all_issues if i.get('severity') == 'HIGH']
medium = [i for i in all_issues if i.get('severity') == 'MEDIUM']

risk_score = min(len(critical)*25 + len(high)*10 + len(medium)*3, 100)

if critical or risk_score >= 50:
    risk_level, rec, safe = 'CRITICAL', '🔴 **DO NOT MERGE**', False
elif risk_score >= 25 or len(high) > 2:
    risk_level, rec, safe = 'HIGH', '🟠 **REVIEW REQUIRED**', False
elif risk_score >= 10:
    risk_level, rec, safe = 'MEDIUM', '🟡 **CAUTION**', True
else:
    risk_level, rec, safe = 'LOW', '🟢 **SAFE TO MERGE**', True

print(f"  Score: {risk_score}/100 ({risk_level})")

# ===== BUILD REPORT =====
date = datetime.now().strftime("%Y-%m-%d")
safe_branch = re.sub(r'[^\w.-]', '_', str(pr_number))
flow_dir = flow.lower().replace('+', '_') if flow not in ('NONE', 'SCC+VTT') else 'mixed'
report_dir = f"pycaption/compliance_checks/{flow_dir}" if flow != 'NONE' else "pycaption/compliance_checks"
os.makedirs(report_dir, exist_ok=True)
report_path = f"{report_dir}/pr_{safe_branch}_review_{date}.md"

# Group code review findings by category for clearer reporting
regressions = [f for f in code_review_findings if f['category'] == 'REGRESSION']
missing_tests = [f for f in code_review_findings if f['category'] == 'MISSING_TEST']

report = f"""# PR #{pr_number} - {pr_title}

**Generated**: {date} at {datetime.now().strftime("%H:%M")}
**Flow**: {flow}
**Base**: origin/{base_branch}

---

## Executive Summary

**Risk Score**: {risk_score}/100 **({risk_level})**

| Metric | Count |
|--------|-------|
| Critical Issues | {len(critical)} |
| High Issues | {len(high)} |
| Medium Issues | {len(medium)} |
| Compliance Issues | {len(compliance_issues)} |
| Regressions | {len(regressions)} |
| Missing Tests | {len(missing_tests)} |

### Recommendation

{rec}

"""

if critical or (high and not safe):
    report += "**Key Blockers:**\n"
    for issue in (critical + high)[:5]:
        label = issue.get('issue') or issue.get('type', 'Issue')
        report += f"- [{issue['severity']}] {label} in `{issue['file']}`\n"
    report += "\n"

# ===== SECTION 1: COMPLIANCE =====
report += f"---\n\n## 1. Spec Compliance ({len(compliance_issues)})\n\n"
if flow == 'NONE':
    report += "ℹ️ No SCC/VTT files changed - spec compliance check skipped\n\n"
elif compliance_issues:
    report += f"Checked against: `pycaption/specs/{flow.lower().replace('+','_')}/..._specs_summary.md`\n\n"
    for i, issue in enumerate(compliance_issues, 1):
        report += f"""### {i}. [{issue['severity']}] {issue['issue']}
- **Rule**: `{issue['rule']}` ({issue['flow']})
- **File**: `{issue['file']}:{issue['lineno']}`
- **Detail**: {issue['detail']}
- **Fix**: {issue['fix']}

"""
else:
    report += f"✅ No compliance issues found against {flow} spec\n\n"

# ===== SECTION 2: CODE REVIEW (regressions + missing tests) =====
report += f"---\n\n## 2. Code Review ({len(code_review_findings)})\n\n"
report += "Full code review covering regressions, breaking changes, and test coverage gaps.\n\n"

# 2A. Regressions
report += f"### 2A. Regressions & Breaking Changes ({len(regressions)})\n\n"
if regressions:
    report += "⚠️ **WARNING**: May break existing code\n\n"
    for i, f in enumerate(regressions, 1):
        report += f"""**{i}. [{f['severity']}] {f['type']}**
- **File**: `{f['file']}:{f['lineno']}`
- **Detail**: {f['detail']}
- **Impact**: {f['impact']}

"""
else:
    report += "✅ No regressions or breaking changes detected\n\n"

# 2B. Missing tests
report += f"### 2B. Test Coverage Gaps ({len(missing_tests)})\n\n"
if missing_tests:
    report += f"📊 **{len(missing_tests)} coverage gap(s)**\n\n"
    for i, f in enumerate(missing_tests, 1):
        loc = f"`{f['file']}:{f['lineno']}`" if f['lineno'] else f"`{f['file']}`"
        report += f"""**{i}. [{f['severity']}] {f['type']}**
- **File**: {loc}
- **Detail**: {f['detail']}
- **Impact**: {f['impact']}

"""
else:
    report += "✅ All changes have test coverage\n\n"

# ===== SUMMARY =====
report += f"""---

## Summary

**Files changed**: {len(changed_files)} ({len(py_src_files)} src, {len(py_test_files)} test)
**Lines**: +{len(additions)} / -{len(deletions)}
**Modified src files with tests updated**: {sum(1 for s in modified_py_src if find_test_for(s))}/{len(modified_py_src)}
**Risk**: {risk_level} ({risk_score}/100)

---

**Generated by**: check-last-pr skill
"""

with open(report_path, 'w') as fh:
    fh.write(report)

print(f"\n{'='*80}")
print(f"✅ REVIEW COMPLETE")
print(f"{'='*80}")
print(f"Report: {report_path}")
print(f"Risk: {risk_level} ({risk_score}/100)")
print(f"Merge: {'✅ SAFE' if safe else '❌ NOT SAFE'}")
print(f"{'='*80}")
```
