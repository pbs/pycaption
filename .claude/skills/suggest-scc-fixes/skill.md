---
name: suggest-scc-fixes
description: Analyzes the latest SCC compliance report and generates detailed Python code suggestions for fixing the most critical issue.
---

# suggest-scc-fixes

## What this skill does

Focused fix generation for SCC compliance issues:

1. **Finds** latest compliance report in `pycaption/compliance_checks/scc/`
2. **Identifies** the MOST CRITICAL issue (highest priority)
3. **Generates** detailed fix with:
   - Exact Python code to implement
   - File locations and line numbers
   - Test cases for the fix
   - Implementation notes
4. **Saves** to `pycaption/compliance_checks/scc/suggested_scc_fixes.md`

**Key optimization**: Focuses on ONE critical issue at a time to avoid context overflow.

## Usage

```bash
/suggest-scc-fixes
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

### Step 1: Find Latest Compliance Report

**Find most recent report:**
```bash
# Get latest compliance report
LATEST_REPORT=$(ls -t pycaption/compliance_checks/scc/compliance_report_*.md 2>/dev/null | head -1)

if [ -z "$LATEST_REPORT" ]; then
    echo "❌ No compliance report found"
    echo "   Run /check-scc-compliance first"
    exit 1
fi

echo "📄 Using report: $LATEST_REPORT"
```

---

### Step 2: Extract Critical Issue List (Targeted Read)

**Don't read entire report - extract summary only:**

```bash
# Extract just Section 7 (Issue Summary by Priority)
# This section has all issues ranked by priority

# Find the section
sed -n '/^## 7. Issue Summary by Priority/,/^## /p' "$LATEST_REPORT" > /tmp/issue_summary.txt

# Or grep for critical issues section
grep -A 50 "### 🔴 CRITICAL" "$LATEST_REPORT" > /tmp/critical_issues.txt
```

**Parse to find #1 issue:**
```python
import re

# Read just the critical issues section (not full report)
critical_section = read("/tmp/critical_issues.txt")

# Extract first issue
# Format: 1. **[RULE-XXX-###]** Issue Title
first_issue_match = re.search(
    r'1\.\s+\*\*\[(RULE-[A-Z]+-\d{3}|CTRL-\d{3})\]\*\*\s+(.+?)(?:\n|$)',
    critical_section
)

if not first_issue_match:
    print("✅ No critical issues found in report!")
    print("   All MUST-level requirements are met.")
    exit(0)

issue_id = first_issue_match.group(1)
issue_title = first_issue_match.group(2).strip()

print(f"🎯 Focusing on: {issue_id} - {issue_title}")
```

---

### Step 3: Get Full Details for THIS Issue Only

**Targeted grep for specific issue:**
```bash
# Extract just this issue's details from report
grep -A 30 "\[$ISSUE_ID\]" "$LATEST_REPORT" > /tmp/issue_details.txt
```

**Parse details:**
```python
issue_details = read("/tmp/issue_details.txt")

# Extract key information
issue_info = {
    'id': issue_id,
    'title': issue_title,
    'severity': extract_field(issue_details, 'Severity'),
    'file': extract_field(issue_details, 'File'),
    'current': extract_field(issue_details, 'Current'),
    'expected': extract_field(issue_details, 'Expected'),
    'impact': extract_field(issue_details, 'Impact'),
    'fix': extract_field(issue_details, 'Fix')
}

def extract_field(text, field_name):
    """Extract value after field name"""
    match = re.search(f'\\*\\*{field_name}\\*\\*:?\\s*(.+?)(?=\\n\\*\\*|\\n\\n|$)', 
                     text, re.DOTALL)
    return match.group(1).strip() if match else "Not specified"
```

---

### Step 4: Read Relevant Source Code (Targeted)

**Only read the file(s) mentioned in the issue:**
```python
if issue_info['file'] != 'Not found':
    # Extract file path and line number
    file_match = re.match(r'(.+?):(\d+)', issue_info['file'])
    
    if file_match:
        file_path = file_match.group(1)
        line_num = int(file_match.group(2))
        
        # Read ONLY around the problem area (not entire file)
        context = read(file_path, offset=max(0, line_num - 10), limit=30)
        
        print(f"📖 Read {file_path} lines {line_num-10} to {line_num+20}")
    else:
        # Missing code - read header/relevant section only
        file_path = issue_info['file']
        context = read(file_path, limit=50)  # Just first 50 lines
else:
    # New feature needed
    context = "Code needs to be added"
    file_path = "pycaption/scc/__init__.py"  # Default location
```

---

### Step 5: Generate Fix (Focused on ONE Issue)

**Generate detailed fix with spec references for this specific issue:**
```python
from datetime import datetime

fix_content = f"""# SCC Compliance Fix Suggestions

**Generated**: {datetime.now().strftime("%Y-%m-%d")}
**Source Report**: {latest_report_file}
**Focus**: Most Critical Issue Only

---

## Issue Being Fixed

**Issue ID**: {issue_info['id']}  
**Title**: {issue_info['title']}  
**Severity**: {issue_info['severity']}  
**Priority**: 🔴 CRITICAL (Issue #1)

**Current State**: {issue_info['current']}  
**Required**: {issue_info['expected']}  
**Impact**: {issue_info['impact']}

**Specification Context**: This issue violates **{issue_info['id']}** in the SCC/CEA-608 specification.
See `pycaption/specs/scc/scc_specs_summary.md` for complete specification text, validation criteria, 
and compliance requirements.

---

## Proposed Fix

### Location
**File**: `{file_path}`  
**Line**: {line_num if 'line_num' in locals() else 'N/A'}

### Implementation

{generate_code_fix(issue_info, context)}

---

## Testing

### Test Cases Required

{generate_test_cases(issue_info)}

---

## Verification Steps

1. **Apply the fix** above
2. **Run tests**: `pytest tests/test_scc.py -v`
3. **Verify against spec**: 
   - Open `pycaption/specs/scc/scc_specs_summary.md`
   - Search for `[{issue_info['id']}]`
   - Confirm fix meets all requirements in:
     * **Requirement** section (what must be true)
     * **Validation** section (how to verify)
     * **Expected Behavior** (input → output examples)
4. **Test with real SCC file** (if applicable)
5. **Check interoperability**: Verify output works with standard tools (e.g., FFmpeg, AWS MediaConvert)

---

## Specification Details

**Rule**: {issue_info['id']}
**Level**: {issue_info['severity']} (mandatory compliance)
**Location in Spec**: `pycaption/specs/scc/scc_specs_summary.md`

**What the spec says**:
Review the complete specification section for:
- Full requirement text from CEA-608 standard
- Validation criteria and patterns
- Common violations and correct patterns
- Test coverage requirements

---

## Additional Notes

{generate_implementation_notes(issue_info)}

---

## Next Steps

After fixing this issue:
1. ✅ Mark {issue_info['id']} as resolved
2. 🔄 Run `/suggest-scc-fixes` again for next critical issue
3. 📊 Re-run `/check-scc-compliance` to verify fix and get updated report
4. 📖 If unclear, review full spec section in `pycaption/specs/scc/scc_specs_summary.md`

---

**Generated by**: suggest-scc-fixes skill  
**Fix complexity**: {estimate_complexity(issue_info)}  
**Estimated time**: {estimate_time(issue_info)}  
**Spec-backed**: ✅ All fixes reference specification requirements
"""

# Save the fix
write("pycaption/compliance_checks/scc/suggested_scc_fixes.md", fix_content)
```

---

### Helper Functions for Fix Generation

```python
def generate_code_fix(issue_info, context):
    """Generate actual Python code fix with spec references"""
    
    # Load spec file to extract rule details
    spec_path = "pycaption/specs/scc/scc_specs_summary.md"
    spec_content = None
    try:
        # Extract just the relevant rule section
        rule_id = issue_info['id']
        spec_section = grep(f"\\[{rule_id}\\]", path=spec_path, 
                           output_mode="content", context=15)
        spec_content = spec_section if spec_section else None
    except:
        spec_content = None
    
    # Example: RU4 hex value fix
    if 'RU4' in issue_info['title'] or '94a7' in str(issue_info):
        spec_ref = extract_spec_reference(spec_content, 'RU4') if spec_content else \
                   "CEA-608 Section 6.4.2 (Roll-Up Captions)"
        
        return f'''
#### Change Required

```python
# File: pycaption/scc/__init__.py
# Line: 437 (approximate)

# BEFORE (incorrect):
elif word in ("9425", "9426", "94a7"):  # RU2, RU3, RU4

# AFTER (correct):
elif word in ("9425", "9426", "9427"):  # RU2, RU3, RU4
```

**What**: Change `"94a7"` to `"9427"` (single character: `a` → `2`)

**Why**: According to **{spec_ref}**, RU4 (Roll-Up 4 rows) control code is 
specified as hex value `0x9427`. The current incorrect value `0x94a7` is not 
a valid CEA-608 control code and won't be recognized by spec-compliant decoders, 
causing captions to fail on compliant devices/players.

**Impact**: Without this fix, SCC files using RU4 will not display correctly 
on devices that strictly follow CEA-608 specification.

**Spec Reference**: See `pycaption/specs/scc/scc_specs_summary.md` → Search for `[CTRL-RU4]` 
or `[RULE-ROLLUP-001]` for complete control code table.
'''
    
    # Example: Missing header validation
    elif 'header' in issue_info['title'].lower() or 'RULE-FMT-001' in issue_info['id']:
        spec_ref = extract_spec_reference(spec_content, 'RULE-FMT-001') if spec_content else \
                   "RULE-FMT-001 and IMPL-FMT-001"
        
        return f'''
#### Code to Add

```python
# File: pycaption/scc/__init__.py
# Location: At start of SCCReader.read() method (around line 214)

def read(self, content, lang="en-US", simulate_roll_up=False, offset=0):
    """
    Read SCC file content and convert to CaptionSet.
    
    :param content: SCC file content as string
    :param lang: Language code
    :param simulate_roll_up: Whether to simulate roll-up
    :param offset: Time offset in microseconds
    """
    # ADD THIS VALIDATION BLOCK:
    lines = content.splitlines()
    
    # Validate SCC header (RULE-FMT-001)
    if not lines or lines[0].strip() != "Scenarist_SCC V1.0":
        raise CaptionReadNoCaptions(
            "Invalid SCC file: Header must be exactly 'Scenarist_SCC V1.0'"
        )
    
    # Continue with existing parsing logic...
    self.caption_stash = CaptionStash()
    # ... rest of existing code
```

**What**: Add 4-line header validation at the start of `read()` method.

**Why**: This is required by **{spec_ref}** in the SCC specification. 
The specification states: "First line must be exactly 'Scenarist_SCC V1.0'" 
(case-sensitive, exact spacing). This is a **MUST-level requirement**.

Without this validation:
- Parser accepts invalid SCC files
- Files may fail on compliant decoders/encoders
- Interoperability issues with other tools (e.g., AWS MediaConvert, CCExtractor)
- No clear error message when files are malformed

**Spec Justification**: 
- CEA-608-E standard defines this as the mandatory file signature
- Industry tools reject files without correct header
- This validation ensures early failure with clear error messages

**Import needed**: Ensure `CaptionReadNoCaptions` is imported:
```python
from pycaption.exceptions import CaptionReadNoCaptions
```

**Spec Reference**: See `pycaption/specs/scc/scc_specs_summary.md` → Section 1.1 "File Header" 
→ `[RULE-FMT-001]` and `[IMPL-FMT-001]` for complete validation requirements.
'''
    
    # Generic template
    else:
        rule_id = issue_info['id']
        spec_ref = extract_spec_reference(spec_content, rule_id) if spec_content else rule_id
        
        return f'''
#### Fix Template

```python
# File: {issue_info.get("file", "pycaption/scc/__init__.py")}

# Based on issue: {issue_info["title"]}
# Current: {issue_info["current"]}
# Expected: {issue_info["expected"]}

# TODO: Implement fix here
# See issue details above for specific requirements
```

**What**: Fix for {issue_info["title"]}

**Why**: This is required by **{spec_ref}** in the SCC specification.
- **Current state**: {issue_info["current"]}
- **Required state**: {issue_info["expected"]}
- **Severity**: {issue_info.get("severity", "MUST")} (mandatory for spec compliance)

**Impact**: {issue_info.get("impact", "May cause interoperability issues or incorrect caption rendering")}

**Spec Reference**: See `pycaption/specs/scc/scc_specs_summary.md` → Search for `[{rule_id}]` 
for complete specification details, validation criteria, and test patterns.

**Note**: Review the spec section for exact implementation requirements and edge cases.
'''


def generate_test_cases(issue_info):
    """Generate test cases for the fix"""
    
    # RU4 fix test
    if 'RU4' in issue_info['title'] or '94a7' in str(issue_info):
        return '''
```python
# File: tests/test_scc.py

def test_ru4_control_code_correct_hex():
    """Test RU4 uses correct hex value 9427 (not 94a7)"""
    from pycaption.scc import SCCReader
    
    scc_content = """Scenarist_SCC V1.0

00:00:00:00	9427 9427 94ad 94ad

"""
    
    reader = SCCReader()
    caption_set = reader.read(scc_content)
    
    # Should parse successfully with correct RU4 code
    assert caption_set is not None
    # Verify roll-up mode is set correctly
    # Add specific assertions based on expected behavior


def test_ru4_roll_up_functionality():
    """Test RU4 creates 4-row roll-up window"""
    from pycaption.scc import SCCReader
    
    # Create SCC with RU4 command and verify 4 rows
    scc_content = """Scenarist_SCC V1.0

00:00:00:00	9427 9427
00:00:01:00	5468 6973 2069 7320 726f 7720 31

"""
    
    reader = SCCReader()
    caption_set = reader.read(scc_content)
    
    # Verify behavior
    assert len(caption_set.get_captions('en-US')) > 0
```
'''
    
    # Header validation test
    elif 'header' in issue_info['title'].lower():
        return '''
```python
# File: tests/test_scc.py

def test_header_validation_rejects_invalid():
    """Test parser rejects files without correct header"""
    from pycaption.scc import SCCReader
    from pycaption.exceptions import CaptionReadNoCaptions
    import pytest
    
    reader = SCCReader()
    
    # Test 1: Wrong header
    invalid_scc = """scenarist_scc v1.0

00:00:00:00	9420 9420
"""
    
    with pytest.raises(CaptionReadNoCaptions, match="Invalid SCC file"):
        reader.read(invalid_scc)
    
    # Test 2: Missing header
    no_header = """00:00:00:00	9420 9420"""
    
    with pytest.raises(CaptionReadNoCaptions, match="Invalid SCC file"):
        reader.read(no_header)
    
    # Test 3: Valid header (should pass)
    valid_scc = """Scenarist_SCC V1.0

00:00:00:00	9420 9420
"""
    
    result = reader.read(valid_scc)  # Should not raise
    assert result is not None


def test_header_validation_case_sensitive():
    """Test header validation is case-sensitive"""
    from pycaption.scc import SCCReader
    from pycaption.exceptions import CaptionReadNoCaptions
    import pytest
    
    reader = SCCReader()
    
    # Wrong case should fail
    wrong_case = """SCENARIST_SCC V1.0

00:00:00:00	9420 9420
"""
    
    with pytest.raises(CaptionReadNoCaptions):
        reader.read(wrong_case)
```
'''
    
    # Generic
    else:
        return '''
```python
# File: tests/test_scc.py

def test_{issue_id_lower}():
    """Test fix for {issue_id}"""
    from pycaption.scc import SCCReader
    
    # Create test SCC content that exercises the fix
    scc_content = """Scenarist_SCC V1.0

00:00:00:00	9420 9420

"""
    
    reader = SCCReader()
    result = reader.read(scc_content)
    
    # Add assertions to verify fix works correctly
    assert result is not None
    # TODO: Add specific assertions for this issue
```
'''.format(
            issue_id_lower=issue_info['id'].lower().replace('-', '_')
        )


def generate_implementation_notes(issue_info):
    """Generate implementation notes with spec references"""
    
    notes = []
    rule_id = issue_info['id']
    
    # Add severity note with spec justification
    if issue_info['severity'] == 'MUST':
        notes.append(f"⚠️  **MUST-level requirement**: This is mandatory per **{rule_id}** in the CEA-608/SCC specification. "
                    "Non-compliance will cause interoperability failures with spec-compliant tools.")
    elif issue_info['severity'] == 'SHOULD':
        notes.append(f"⚡ **SHOULD-level requirement**: Recommended by **{rule_id}** for best practices and compatibility.")
    
    # Add impact note with spec context
    if 'interoperability' in issue_info.get('impact', '').lower():
        notes.append("🔗 **Interoperability impact**: This fix is required for compatibility with industry-standard "
                    "tools (AWS MediaConvert, CCExtractor, FFmpeg) that strictly follow CEA-608 specification.")
    
    # Add complexity note
    if 'character' in issue_info.get('fix', '').lower() or 'line' in issue_info.get('fix', '').lower():
        notes.append("✅ **Simple fix**: Minimal code change required (single line or character)")
    
    # Add detailed spec reference
    notes.append(f"📖 **Specification reference**:")
    notes.append(f"   - Primary: `pycaption/specs/scc/scc_specs_summary.md` → Search for `[{rule_id}]`")
    notes.append(f"   - This section contains:")
    notes.append(f"     * Complete requirement text from CEA-608 standard")
    notes.append(f"     * Validation criteria and test patterns")
    notes.append(f"     * Common violations and correct implementations")
    notes.append(f"     * Expected behavior examples")
    
    # Add related rules if applicable
    if 'RULE-FMT' in rule_id:
        notes.append(f"   - Related: See also `[IMPL-FMT-001]` for implementation requirements")
    elif 'RULE-TMC' in rule_id:
        notes.append(f"   - Related: See also `[IMPL-TMC-xxx]` sections for timing validation")
    elif 'RULE-ROLLUP' in rule_id or 'RU' in issue_info.get('title', ''):
        notes.append(f"   - Related: See control code table for all roll-up codes (RU2/RU3/RU4)")
    
    return '\n'.join(f'- {note}' if not note.startswith('   ') else note for note in notes)


def estimate_complexity(issue_info):
    """Estimate fix complexity"""
    
    if any(word in issue_info.get('fix', '').lower() for word in ['change', 'character', 'single']):
        return "🟢 Low (simple change)"
    elif any(word in issue_info.get('fix', '').lower() for word in ['add', 'line', 'validation']):
        return "🟡 Medium (add code)"
    else:
        return "🔴 High (complex implementation)"


def estimate_time(issue_info):
    """Estimate time to fix"""
    
    fix_text = issue_info.get('fix', '').lower()
    
    if 'character' in fix_text or '30 second' in fix_text:
        return "< 1 minute"
    elif 'line' in fix_text or '5 minute' in fix_text:
        return "5-10 minutes"
    else:
        return "15-30 minutes"


def extract_spec_reference(spec_content, search_term):
    """
    Extract spec reference from spec content.
    Returns formatted spec reference string.
    """
    if not spec_content:
        return search_term
    
    # Try to find the rule section
    import re
    
    # Look for rule ID
    rule_match = re.search(r'\[(RULE-[A-Z]+-\d{3})\]', spec_content)
    if rule_match:
        rule_id = rule_match.group(1)
        
        # Look for CEA reference
        cea_match = re.search(r'CEA-608[^,\n]*', spec_content)
        if cea_match:
            return f"{rule_id} (per {cea_match.group(0)})"
        
        return rule_id
    
    # Fallback to search term
    return search_term
```

---

### Step 6: Display Summary

```python
print(f"""
✅ Fix suggestion generated!

🎯 Issue Fixed: {issue_info['id']} - {issue_info['title']}
📄 Saved to: pycaption/compliance_checks/scc/suggested_scc_fixes.md

📊 Fix Summary:
   Severity: {issue_info['severity']}
   File: {file_path}
   Complexity: {estimate_complexity(issue_info)}
   Time: {estimate_time(issue_info)}

💡 Next Steps:
   1. Review the suggested fix in the report
   2. Apply the code changes
   3. Run the test cases
   4. Run /suggest-scc-fixes again for next issue

""")
```

---

## Success Criteria

✅ **Context-efficient** - Uses ~20K tokens (vs 90K+ for all issues)  
✅ **Focused** - One issue at a time with complete fix  
✅ **Actionable** - Exact code, not generic advice  
✅ **Testable** - Includes test cases  
✅ **Iterative** - Run multiple times for multiple issues  
✅ **Fast** - Completes in ~1-2 minutes

---

## Important Notes

**Why one issue at a time:**
- Keeps context window manageable
- Allows detailed, specific fixes
- User can review and apply incrementally
- Can re-run for next issue after first is fixed

**Priority order:**
1. First run: Fix issue #1 (most critical)
2. Second run: Fix issue #2 (next critical)
3. Continue until all critical issues resolved

**Token usage breakdown:**
- Find report: 1K tokens
- Extract summary: 2K tokens
- Get issue details: 3K tokens
- Read source context: 5K tokens
- Generate fix: 8K tokens
- **Total: ~20K tokens** (safe for any context window)

**Error handling:**
- No report found → Tell user to run check-scc-compliance
- No issues found → Celebrate! All compliant
- Can't parse issue → Use generic template
