---
name: run-all-compliance
description: Runs all 4 compliance checks (SCC, VTT, DFXP, SAMI) in sequence, produces 4 dated reports.
---

# run-all-compliance

## What this skill does

Runs **all four compliance checks** (SCC, VTT, DFXP, SAMI) in sequence against the current spec summaries and pycaption implementation. Produces four dated compliance reports.

**Prerequisites**: Spec summaries must exist in `ai_artifacts/specs/`. If missing, run the analyze-docs skills first (`/analyze-scc-docs`, `/analyze-vtt-docs`, `/analyze-dfxp-docs`, `/analyze-sami-docs`).

**Output**: Four reports in `ai_artifacts/compliance_checks/`:
- `scc/compliance_report_YYYY-MM-DD.md`
- `vtt/compliance_report_YYYY-MM-DD.md`
- `dfxp/compliance_report_YYYY-MM-DD.md`
- `sami/compliance_report_YYYY-MM-DD.md`

**Usage:** `/run-all-compliance`

---

## Implementation

Extract and run the Python script from each compliance skill. Execute all four sequentially via Bash:

```bash
echo "=========================================="
echo "  RUNNING ALL COMPLIANCE CHECKS"
echo "=========================================="
echo ""

TMPDIR=$(mktemp -d)
trap 'rm -rf "$TMPDIR"' EXIT

echo "[1/4] SCC Compliance Check"
echo "-------------------------------------------"
sed -n '/^```python/,/^```/{ /^```/d; p; }' .claude/skills/check-scc-compliance/skill.md > "$TMPDIR/scc.py"
python3 "$TMPDIR/scc.py" && SCC_EXIT=0 || SCC_EXIT=$?
echo ""

echo "[2/4] VTT Compliance Check"
echo "-------------------------------------------"
sed -n '/^```python/,/^```/{ /^```/d; p; }' .claude/skills/check-vtt-compliance/skill.md > "$TMPDIR/vtt.py"
python3 "$TMPDIR/vtt.py" && VTT_EXIT=0 || VTT_EXIT=$?
echo ""

echo "[3/4] DFXP Compliance Check"
echo "-------------------------------------------"
sed -n '/^```python/,/^```/{ /^```/d; p; }' .claude/skills/check-dfxp-compliance/skill.md > "$TMPDIR/dfxp.py"
python3 "$TMPDIR/dfxp.py" && DFXP_EXIT=0 || DFXP_EXIT=$?
echo ""

echo "[4/4] SAMI Compliance Check"
echo "-------------------------------------------"
sed -n '/^```python/,/^```/{ /^```/d; p; }' .claude/skills/check-sami-compliance/skill.md > "$TMPDIR/sami.py"
python3 "$TMPDIR/sami.py" && SAMI_EXIT=0 || SAMI_EXIT=$?
echo ""

echo "=========================================="
echo "  ALL COMPLIANCE CHECKS COMPLETE"
echo "=========================================="
echo ""
echo "  SCC:  $([ $SCC_EXIT -eq 0 ] && echo 'OK' || echo 'FAILED')"
echo "  VTT:  $([ $VTT_EXIT -eq 0 ] && echo 'OK' || echo 'FAILED')"
echo "  DFXP: $([ $DFXP_EXIT -eq 0 ] && echo 'OK' || echo 'FAILED')"
echo "  SAMI: $([ $SAMI_EXIT -eq 0 ] && echo 'OK' || echo 'FAILED')"
echo ""
echo "  Reports:"
echo "    $(ls -t ai_artifacts/compliance_checks/scc/compliance_report_*.md 2>/dev/null | head -1)"
echo "    $(ls -t ai_artifacts/compliance_checks/vtt/compliance_report_*.md 2>/dev/null | head -1)"
echo "    $(ls -t ai_artifacts/compliance_checks/dfxp/compliance_report_*.md 2>/dev/null | head -1)"
echo "    $(ls -t ai_artifacts/compliance_checks/sami/compliance_report_*.md 2>/dev/null | head -1)"
```
