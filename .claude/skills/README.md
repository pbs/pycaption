# Caption Compliance Skills

Custom Claude Code skills for managing SCC and WebVTT compliance in pycaption. Automates specification analysis, compliance checking, and fix generation per CEA-608/708 and W3C standards.

## Workflow

```
analyze-*-docs → check-*-compliance → suggest-*-fixes → check-last-pr
(specs)          (find issues)        (generate fixes)  (PR review)
```

## Skills

### analyze-scc-docs
Generates comprehensive SCC specification from CEA-608/708 standards.
- **Output**: `pycaption/specs/scc/scc_specs_summary.md` (300+ control codes, 42 rules)
- **Usage**: `/analyze-scc-docs`

### analyze-vtt-docs
Generates comprehensive WebVTT specification from W3C sources.
- **Output**: `pycaption/specs/vtt/vtt_specs_summary.md` (76 rules, 8 tags, 6 settings, 7 entities)
- **Usage**: `/analyze-vtt-docs`

### check-scc-compliance
Exhaustive SCC compliance checker - identifies ALL specification violations.
- **Checks**: 42 rules, 704 control codes, validation gaps
- **Output**: `pycaption/compliance_checks/scc/compliance_report_EXHAUSTIVE_YYYY-MM-DD.md`
- **Usage**: `/check-scc-compliance`

### check-vtt-compliance
Exhaustive WebVTT compliance checker - identifies ALL specification violations.
- **Checks**: 76 rules, tag/setting/entity coverage, validation gaps
- **Output**: `pycaption/compliance_checks/vtt/compliance_report_EXHAUSTIVE_YYYY-MM-DD.md`
- **Usage**: `/check-vtt-compliance`

### suggest-scc-fixes
Generates detailed code fix for the #1 critical SCC issue.
- **Includes**: Exact Python code, tests, spec references
- **Output**: `pycaption/compliance_checks/scc/suggested_scc_fixes.md`
- **Usage**: `/suggest-scc-fixes` (run iteratively for multiple issues)

### suggest-vtt-fixes
Generates detailed code fix for the #1 critical WebVTT issue.
- **Includes**: Exact Python code, tests, W3C spec references
- **Output**: `pycaption/compliance_checks/vtt/suggested_vtt_fixes.md`
- **Usage**: `/suggest-vtt-fixes` (run iteratively for multiple issues)

### check-last-pr
Analyzes latest PR for compliance issues, regressions, and code quality.
- **Auto-detects**: SCC/VTT/DFXP changes
- **Checks**: New violations, removed validations, code quality
- **Output**: Format-specific folder or `pycaption/compliance_checks/pr_*.md`
- **Usage**: `/check-last-pr`

## Quick Start

1. **Generate specs** (one-time):
   ```
   /analyze-scc-docs
   /analyze-vtt-docs
   ```

2. **Check compliance**:
   ```
   /check-scc-compliance
   /check-vtt-compliance
   ```

3. **Fix issues** (iterative):
   ```
   /suggest-scc-fixes  → apply fix → test
   /suggest-vtt-fixes  → apply fix → test
   ```

4. **Review PR**:
   ```
   /check-last-pr
   ```

## Rule Format

- **RULE-XXX-###**: Specification rules (e.g., `RULE-FMT-001`, `RULE-TIME-005`)
- **IMPL-XXX-###**: Implementation requirements (generic, no code references)
- **CTRL-###**: Control codes (SCC only, e.g., `CTRL-008`)

Categories: FMT (format), TIME/TMC (timing), CUE (structure), SET (settings), TAG (markup), ENT (entities), REG (regions), LAY (layout), CHAR (characters)

## Notes

- **Fix skills** focus on ONE issue at a time for efficiency (~20K vs 90K tokens)
- **Specs** are source of truth: `pycaption/specs/{scc,vtt}/*_specs_summary.md`
- **Reports** saved to: `pycaption/compliance_checks/{scc,vtt}/`
- Re-run `analyze-*-docs` when standards change

---

**Last Updated**: 2026-04-21 | See individual SKILL.md files for implementation details
