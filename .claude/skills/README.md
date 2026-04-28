# Caption Compliance Skills

Custom Claude Code skills for SCC, WebVTT, and DFXP/TTML compliance in pycaption per CEA-608/708, W3C WebVTT, and W3C TTML standards.

## Workflow

```
analyze-*-docs --> check-*-compliance --> suggest-*-fixes
                   run-all-compliance     check-last-pr (PR review)
```

## Skills

| Skill | What it does |
|-------|-------------|
| `/analyze-scc-docs` | Generate SCC spec summary from CEA-608/708 web sources (agent-driven, uses WebFetch/WebSearch) |
| `/analyze-vtt-docs` | Generate WebVTT spec summary from W3C web sources (agent-driven, uses WebFetch/WebSearch) |
| `/analyze-dfxp-docs` | Generate DFXP/TTML spec summary from W3C TTML web sources (agent-driven, uses WebFetch/WebSearch) |
| `/check-scc-compliance` | Deep validation + 44 rules + 621 control codes + frame rate analysis + test coverage |
| `/check-vtt-compliance` | Deep validation + 76 rules + tag/setting/entity coverage with read/write distinction |
| `/check-dfxp-compliance` | Deep validation + 115 rules + styling/timing/parameter coverage with read/write distinction |
| `/suggest-scc-fixes` | Analyzes latest SCC compliance report, generates code fix for the most critical issue |
| `/suggest-vtt-fixes` | Analyzes latest VTT compliance report, generates code fix for the most critical issue |
| `/suggest-dfxp-fixes` | Analyzes latest DFXP compliance report, generates code fix for the most critical issue |
| `/check-last-pr` | Comprehensive PR review: compliance, code review, regressions, test coverage |
| `/run-all-compliance` | Runs all 3 compliance checks (SCC, VTT, DFXP) in sequence, produces 3 dated reports |

## GitHub Actions

| Action | Trigger | Description |
|--------|---------|-------------|
| `scc_compliance_check.yml` | `workflow_dispatch` | Runs SCC compliance check, uploads report, optional Slack notification |
| `vtt_compliance_check.yml` | `workflow_dispatch` | Runs VTT compliance check, uploads report, optional Slack notification |
| `dfxp_compliance_check.yml` | `workflow_dispatch` | Runs DFXP compliance check, uploads report, optional Slack notification |
| `all_compliance_checks.yml` | `workflow_dispatch` | Runs all 3 compliance checks, uploads combined report, summary table in Slack |
| `pr_compliance_check.yml` | `workflow_dispatch` / `pull_request` | PR review: compliance, regressions, test coverage, comments on PR |
| `spec_refresh_reminder.yml` | `schedule` (bi-annual) / `workflow_dispatch` | Sends Slack reminder to re-run analyze-docs skills locally |

All compliance actions extract and run the same Python scripts from the skill `.md` files — local skills and GitHub Actions produce identical reports.

## Spec Regeneration

The analyze-docs skills need to be run locally (they require Claude AI with WebFetch/WebSearch). The underlying specs rarely change:

| Format | Standard | Frequency | Reason |
|--------|----------|-----------|--------|
| SCC | CEA-608/708 | 6 months | Mature, rarely updated |
| VTT | W3C WebVTT | 6 months | Living standard, but core spec is stable |
| DFXP | W3C TTML 1.0/2.0 | 6 months | Stable W3C Recommendation |

A bi-annual Slack reminder (`spec_refresh_reminder.yml`) fires on Jan 1 and Jul 1. After regenerating specs, run `/run-all-compliance` to update the compliance reports.

## Rule Format

- **RULE-XXX-###**: Spec rules
- **IMPL-XXX-###**: Implementation requirements
- **CTRL-###**: Control codes (SCC only)

## Notes

- Fix skills target ONE issue at a time for efficiency (~20K vs 90K tokens)
- Specs are the source of truth for compliance checks; compliance scripts read spec summaries, not raw standards
- Spec summaries: `ai_artifacts/specs/{scc,vtt,dfxp}/*_specs_summary.md`
- Master checklists: `ai_artifacts/specs/{scc,vtt,dfxp}/master_checklist.md`
- Slack notifications require `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` repository secrets
- `${{ github.token }}` is used automatically for GitHub API calls (no secret setup needed)

---
**Last Updated**: 2026-04-28
