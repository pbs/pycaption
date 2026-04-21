---
name: check-last-pr
description: Analyzes latest PR for compliance issues, regressions, and code quality. Detects SCC/VTT/DFXP changes automatically.
---

# check-last-pr

## What this skill does

Simplified PR analysis focused on **new compliance issues** and **regressions**:

1. **Auto-detects** which formats changed (SCC/VTT/DFXP)
2. **Finds new compliance issues** in PR changes
3. **Detects regressions** (removed validations, breaking changes)
4. **Code quality review** (bare excepts, magic numbers, missing docstrings)
5. **Generates focused report** in format-specific folder

**Report saved to:**
- SCC only → `pycaption/compliance_checks/scc/pr_{number}_review_{date}.md`
- VTT only → `pycaption/compliance_checks/vtt/pr_{number}_review_{date}.md`
- DFXP only → `pycaption/compliance_checks/dfxp/pr_{number}_review_{date}.md`
- Multiple formats → `pycaption/compliance_checks/pr_{number}_review_{date}.md`

## Usage

```bash
/check-last-pr
```

Auto-fetches latest PR and generates report.

---

## Implementation

```python
import os, re, subprocess, glob
from datetime import datetime

print("="*80)
print("PR COMPLIANCE & CODE REVIEW")
print("="*80)

# ===== STEP 1: GET PR INFO =====
print("\n[1/5] Getting PR information...")

# Try gh CLI
try:
    result = subprocess.run(
        ['gh', 'pr', 'list', '--state', 'open', '--limit', '1', '--json', 'number,title'],
        capture_output=True, text=True, check=True
    )
    import json
    pr_data = json.loads(result.stdout)
    if pr_data:
        pr_number = pr_data[0]['number']
        pr_title = pr_data[0]['title']
        print(f"  PR #{pr_number}: {pr_title}")
    else:
        print("  No open PRs found - using current branch")
        pr_number = subprocess.run(['git', 'branch', '--show-current'],
                                  capture_output=True, text=True).stdout.strip()
except:
    print("  gh CLI not available - using current branch")
    pr_number = subprocess.run(['git', 'branch', '--show-current'],
                              capture_output=True, text=True).stdout.strip()

# ===== STEP 2: DETECT FORMAT CHANGES =====
print("\n[2/5] Detecting format changes...")

# Get changed files
base_branch = 'main'
result = subprocess.run(
    ['git', 'diff', '--name-only', f'origin/{base_branch}...HEAD'],
    capture_output=True, text=True
)
changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

formats = {
    'scc': {'changed': False, 'files': []},
    'vtt': {'changed': False, 'files': []},
    'dfxp': {'changed': False, 'files': []},
}

patterns = {
    'scc': r'(pycaption/scc/|tests/.*scc)',
    'vtt': r'(pycaption/(webvtt|vtt)|tests/.*(webvtt|vtt))',
    'dfxp': r'(pycaption/dfxp/|tests/.*dfxp)',
}

for file in changed_files:
    for fmt, pattern in patterns.items():
        if re.search(pattern, file, re.I):
            formats[fmt]['changed'] = True
            formats[fmt]['files'].append(file)

any_changed = any(f['changed'] for f in formats.values())

if not any_changed:
    print("  ✅ No caption format changes - skipping analysis")
    exit(0)

for fmt, data in formats.items():
    if data['changed']:
        print(f"  ✅ {fmt.upper()}: {len(data['files'])} files")

# ===== STEP 3: GET DIFF & PARSE =====
print("\n[3/5] Analyzing code changes...")

diff_result = subprocess.run(
    ['git', 'diff', f'origin/{base_branch}...HEAD'],
    capture_output=True, text=True
)
diff_content = diff_result.stdout

additions = []
deletions = []
current_file = None

for line in diff_content.split('\n'):
    if line.startswith('diff --git'):
        match = re.search(r'b/(.+)$', line)
        current_file = match.group(1) if match else None
    elif line.startswith('+') and not line.startswith('+++'):
        additions.append({'file': current_file, 'line': line[1:].strip()})
    elif line.startswith('-') and not line.startswith('---'):
        deletions.append({'file': current_file, 'line': line[1:].strip()})

print(f"  Additions: {len(additions)} lines")
print(f"  Deletions: {len(deletions)} lines")

# ===== STEP 4: COMPLIANCE CHECKS =====
print("\n[4/5] Checking compliance...")

compliance_issues = []

# SCC checks
if formats['scc']['changed']:
    print("  Checking SCC...")
    
    for add in additions:
        if not add['file'] or 'scc' not in add['file']:
            continue
        
        line = add['line']
        
        # Check 1: Incorrect RU4 hex
        if "'94a7'" in line or '"94a7"' in line:
            compliance_issues.append({
                'format': 'SCC',
                'severity': 'CRITICAL',
                'rule': 'CTRL-008',
                'issue': 'Incorrect RU4 hex value',
                'detail': "Found '94a7', should be '9427'",
                'file': add['file'],
                'line': line[:80]
            })
        
        # Check 2: Missing validation in parse functions
        if 'def ' in line and any(kw in line.lower() for kw in ['parse', 'read', 'decode']):
            # Check if validation exists in next 10 lines
            idx = additions.index(add)
            has_validation = any(
                'raise' in additions[i]['line'] or 'if ' in additions[i]['line']
                for i in range(idx, min(idx+10, len(additions)))
                if additions[i]['file'] == add['file']
            )
            if not has_validation:
                compliance_issues.append({
                    'format': 'SCC',
                    'severity': 'MEDIUM',
                    'rule': 'VALIDATION',
                    'issue': 'Parse function without validation',
                    'detail': 'Should validate input format',
                    'file': add['file'],
                    'line': line[:80]
                })

# VTT checks
if formats['vtt']['changed']:
    print("  Checking VTT...")
    
    for add in additions:
        if not add['file'] or 'vtt' not in add['file'].lower():
            continue
        
        line = add['line']
        
        # Check 1: WEBVTT header validation
        if 'WEBVTT' in line and '!=' not in line:
            if 'strip()' not in line or '==' not in line:
                compliance_issues.append({
                    'format': 'VTT',
                    'severity': 'HIGH',
                    'rule': 'RULE-FMT-001',
                    'issue': 'WEBVTT header validation incorrect',
                    'detail': 'Should use exact match with strip()',
                    'file': add['file'],
                    'line': line[:80]
                })
        
        # Check 2: Timestamp format validation
        if 'timestamp' in line.lower() and 'def ' in line:
            idx = additions.index(add)
            has_regex = any(
                'regex' in additions[i]['line'] or 'match' in additions[i]['line']
                for i in range(idx, min(idx+15, len(additions)))
                if additions[i]['file'] == add['file']
            )
            if not has_regex:
                compliance_issues.append({
                    'format': 'VTT',
                    'severity': 'MEDIUM',
                    'rule': 'RULE-TIME-001',
                    'issue': 'Timestamp needs format validation',
                    'detail': 'Should validate HH:MM:SS.mmm',
                    'file': add['file'],
                    'line': line[:80]
                })

print(f"  Found: {len(compliance_issues)} compliance issues")

# ===== STEP 5: REGRESSION ANALYSIS =====
print("\n[5/5] Checking regressions...")

regressions = []

for deletion in deletions:
    if not deletion['file']:
        continue
    
    line = deletion['line']
    
    # Check 1: Removed validation
    if 'raise' in line or 'assert' in line:
        is_moved = any(line in a['line'] for a in additions if a['file'] == deletion['file'])
        if not is_moved:
            regressions.append({
                'type': 'REMOVED_VALIDATION',
                'severity': 'HIGH',
                'file': deletion['file'],
                'detail': f"Validation removed: {line[:60]}",
                'impact': 'May accept invalid input'
            })
    
    # Check 2: Removed public function
    if 'def ' in line:
        func_match = re.search(r'def\s+(\w+)', line)
        if func_match:
            func_name = func_match.group(1)
            is_moved = any(f'def {func_name}' in a['line'] for a in additions)
            if not is_moved and not func_name.startswith('_'):
                regressions.append({
                    'type': 'REMOVED_FUNCTION',
                    'severity': 'CRITICAL',
                    'file': deletion['file'],
                    'detail': f"Public function removed: {func_name}",
                    'impact': 'Breaking change'
                })
    
    # Check 3: Changed control codes
    old_hex = re.findall(r"['\"]([0-9a-fA-F]{4})['\"]", line)
    if old_hex:
        for hex_val in old_hex:
            new_hex = None
            for add in additions:
                if add['file'] == deletion['file']:
                    new_match = re.findall(r"['\"]([0-9a-fA-F]{4})['\"]", add['line'])
                    if new_match and new_match[0] != hex_val:
                        new_hex = new_match[0]
                        break
            
            if new_hex and new_hex != hex_val:
                regressions.append({
                    'type': 'CHANGED_CONTROL_CODE',
                    'severity': 'CRITICAL',
                    'file': deletion['file'],
                    'detail': f"Control code: {hex_val} → {new_hex}",
                    'impact': 'May break captions'
                })

print(f"  Found: {len(regressions)} regressions")

# ===== STEP 6: CODE QUALITY =====
print("\n[6/6] Code quality review...")

quality_issues = []

for add in additions:
    if not add['file'] or not add['file'].endswith('.py'):
        continue
    
    line = add['line']
    
    # Check 1: Bare except
    if re.search(r'except\s*:', line) and 'except Exception' not in line:
        quality_issues.append({
            'type': 'BARE_EXCEPT',
            'severity': 'MEDIUM',
            'file': add['file'],
            'detail': 'Bare except catches all',
            'fix': 'Use specific exception'
        })
    
    # Check 2: Magic numbers
    if re.search(r'\b(32|15|30|29\.97)\b', line):
        if 'SPEC' not in line and '#' not in line:
            quality_issues.append({
                'type': 'MAGIC_NUMBER',
                'severity': 'LOW',
                'file': add['file'],
                'detail': f"Magic number: {line[:60]}",
                'fix': 'Use named constant'
            })
    
    # Check 3: Missing docstrings
    if re.search(r'^\s*def\s+[a-z]\w+\(', line):
        idx = additions.index(add)
        has_docstring = any(
            '"""' in additions[i]['line'] or "'''" in additions[i]['line']
            for i in range(idx+1, min(idx+5, len(additions)))
            if additions[i]['file'] == add['file']
        )
        if not has_docstring:
            quality_issues.append({
                'type': 'MISSING_DOCSTRING',
                'severity': 'LOW',
                'file': add['file'],
                'detail': f"Function: {line[:60]}",
                'fix': 'Add docstring'
            })

print(f"  Found: {len(quality_issues)} quality issues")

# ===== STEP 7: GENERATE REPORT =====
print("\n[7/7] Generating report...")

date = datetime.now().strftime("%Y-%m-%d")

# Determine folder
primary_format = None
changed_count = sum(1 for f in formats.values() if f['changed'])

if changed_count == 1:
    for fmt, data in formats.items():
        if data['changed']:
            primary_format = fmt
            break

if primary_format:
    report_dir = f"pycaption/compliance_checks/{primary_format}"
    report_path = f"{report_dir}/pr_{pr_number}_review_{date}.md"
else:
    report_dir = "pycaption/compliance_checks"
    report_path = f"{report_dir}/pr_{pr_number}_review_{date}.md"

os.makedirs(report_dir, exist_ok=True)

# Calculate severity counts
critical_count = sum(1 for i in compliance_issues + regressions if i.get('severity') == 'CRITICAL')
high_count = sum(1 for i in compliance_issues + regressions if i.get('severity') == 'HIGH')

risk_level = 'HIGH' if critical_count > 0 else 'MEDIUM' if high_count > 0 else 'LOW'

# Generate report
report = f"""# PR #{pr_number} Compliance & Code Review

**Generated**: {date}
**Formats Changed**: {', '.join(f.upper() for f, d in formats.items() if d['changed'])}

## Executive Summary

**Compliance Issues**: {len(compliance_issues)} ({critical_count} critical, {high_count} high)
**Regressions**: {len(regressions)}
**Code Quality**: {len(quality_issues)} suggestions

**Overall Risk**: {'🔴 HIGH' if risk_level == 'HIGH' else '🟡 MEDIUM' if risk_level == 'MEDIUM' else '🟢 LOW'}

---

## 1. Compliance Issues ({len(compliance_issues)})

"""

if compliance_issues:
    for i, issue in enumerate(compliance_issues, 1):
        report += f"""### {i}. [{issue['severity']}] {issue['issue']}

- **Format**: {issue['format']}
- **Rule**: {issue['rule']}
- **File**: `{issue['file']}`
- **Detail**: {issue['detail']}
- **Line**: `{issue['line']}`

"""
else:
    report += "✅ No compliance issues detected\n\n"

report += f"""---

## 2. Regression Analysis ({len(regressions)})

"""

if regressions:
    for i, reg in enumerate(regressions, 1):
        report += f"""### {i}. [{reg['severity']}] {reg['type']}

- **File**: `{reg['file']}`
- **Detail**: {reg['detail']}
- **Impact**: {reg['impact']}

"""
else:
    report += "✅ No regressions detected\n\n"

report += f"""---

## 3. Code Quality Review ({len(quality_issues)})

"""

if quality_issues:
    for i, qissue in enumerate(quality_issues, 1):
        report += f"""### {i}. [{qissue['severity']}] {qissue['type']}

- **File**: `{qissue['file']}`
- **Detail**: {qissue['detail']}
- **Fix**: {qissue['fix']}

"""
else:
    report += "✅ Code quality looks good\n\n"

report += f"""---

## Recommendation

"""

if critical_count > 0:
    report += "🔴 **DO NOT MERGE** - Critical issues must be fixed\n"
elif high_count > 0 or len(regressions) > 0:
    report += "🟡 **REVIEW REQUIRED** - Address issues before merge\n"
else:
    report += "🟢 **SAFE TO MERGE** - No critical issues\n"

report += f"\n---\n**Generated by**: check-last-pr skill\n"

with open(report_path, 'w') as f:
    f.write(report)

print(f"\n✅ Report saved: {report_path}")
print(f"   Risk: {risk_level}")
print(f"   Compliance: {len(compliance_issues)}, Regressions: {len(regressions)}")
```

---

## What Gets Checked

### Compliance Issues
**SCC:**
- ❌ Incorrect hex values (e.g., `'94a7'` should be `'9427'`)
- ❌ Parse functions without validation

**VTT:**
- ❌ Incorrect WEBVTT header validation
- ❌ Missing timestamp format validation

### Regressions
- ❌ Removed validations (`raise`, `assert`)
- ❌ Removed public functions (breaking changes)
- ❌ Changed control codes (hex values)

### Code Quality
- ⚠️ Bare except clauses
- ⚠️ Magic numbers (32, 15, 30, 29.97)
- ⚠️ Missing docstrings

---

## Report Structure

```
PR #123 Compliance & Code Review
├── Executive Summary (risk level, counts)
├── 1. Compliance Issues (new violations)
├── 2. Regression Analysis (breaking changes)
├── 3. Code Quality Review (suggestions)
└── Recommendation (merge decision)
```

---

## Success Criteria

✅ **Focused** - Only checks changed code
✅ **Fast** - Analyzes PR in <2 minutes
✅ **Actionable** - Clear issues with fixes
✅ **Risk-based** - HIGH/MEDIUM/LOW levels
✅ **Format-aware** - Saves to correct folder
