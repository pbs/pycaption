# Caption Compliance Skills

Custom Claude Code skills for SCC, WebVTT, DFXP/TTML, and SAMI compliance in pycaption per CEA-608/708, W3C WebVTT, W3C TTML, and Microsoft SAMI standards.

## Workflow

```
analyze-*-docs --> check-*-compliance --> suggest-*-fixes
                   run-all-compliance     check-last-pr (PR review)
```

## Skills

| Skill | What it does |
|-------|-------------|
| `/analyze-scc-docs` | Generate SCC spec summary from CEA-608/708 sources. Uses local `standards_summary.md` if available, otherwise falls back to web sources (agent-driven, uses WebFetch/WebSearch) |
| `/analyze-vtt-docs` | Generate WebVTT spec summary from W3C web sources (agent-driven, uses WebFetch/WebSearch) |
| `/analyze-dfxp-docs` | Generate DFXP/TTML spec summary from W3C TTML web sources (agent-driven, uses WebFetch/WebSearch) |
| `/analyze-sami-docs` | Generate SAMI spec summary from Microsoft SAMI documentation and web sources (agent-driven, uses WebFetch/WebSearch) |
| `/check-scc-compliance` | Sanity check + 12 deep validations (cross-mode EDM, zero-value truthiness, silent error suppression, read-only styling, position fallback, etc.) + 44 rules + 704 control codes + frame rate analysis + test coverage |
| `/check-vtt-compliance` | Sanity check + deep validation + 76 rules + tag/setting/entity coverage with read/write distinction |
| `/check-dfxp-compliance` | Sanity check + deep validation + 115 rules + styling/timing/parameter coverage with read/write distinction |
| `/check-sami-compliance` | Sanity check + deep validation + 75 rules + styling/element/timing/language/encoding coverage with read/write distinction |
| `/suggest-scc-fixes` | Analyzes latest SCC compliance report, generates code fix for the most critical issue |
| `/suggest-vtt-fixes` | Analyzes latest VTT compliance report, generates code fix for the most critical issue |
| `/suggest-dfxp-fixes` | Analyzes latest DFXP compliance report, generates code fix for the most critical issue |
| `/check-last-pr` | Comprehensive PR review: compliance, code review, regressions, test coverage |
| `/run-all-compliance` | Runs all 4 compliance checks (SCC, VTT, DFXP, SAMI) in sequence, produces 4 dated reports |
| `/generate-standards-summary` | Reads proprietary PDF standards (CEA-608, CEA-708, SMPTE ST 2052-1, RP 2052-10) and generates local-only `standards_summary.md` files for analyze skills |

## GitHub Actions

| Action | Trigger | Description |
|--------|---------|-------------|
| `scc_compliance_check.yml` | `workflow_dispatch` | Runs SCC compliance check, uploads report, optional Slack notification |
| `vtt_compliance_check.yml` | `workflow_dispatch` | Runs VTT compliance check, uploads report, optional Slack notification |
| `dfxp_compliance_check.yml` | `workflow_dispatch` | Runs DFXP compliance check, uploads report, optional Slack notification |
| `all_compliance_checks.yml` | `workflow_dispatch` | Runs all 4 compliance checks, uploads combined report, summary table in Slack |
| `pr_compliance_check.yml` | `workflow_dispatch` / `pull_request` | PR review: compliance, regressions, test coverage, comments on PR |
| `spec_refresh_reminder.yml` | `schedule` (bi-annual) / `workflow_dispatch` | Sends Slack reminder to re-run analyze-docs skills locally |

All compliance actions extract and run the same Python scripts from the skill `.md` files — local skills and GitHub Actions produce identical reports. Workflows extract metrics directly from the generated report markdown (not from a separate summary file).

## Security

- Third-party GitHub Actions (`archive/github-actions-slack`) are pinned to commit SHA (not mutable tags) to prevent supply-chain attacks
- Workflow `run:` blocks use shell variable expansion (`$VAR`) instead of expression interpolation (`${{ env.VAR }}`) for defense-in-depth against injection
- PR compliance workflow uses allowlist-only extraction when reading script output into `$GITHUB_ENV`
- Slack availability checks verify both `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` before attempting to send
- Workflows use minimal permissions (`contents: read`; only `pr_compliance_check` adds `pull-requests: write`)
- Slack success notifications require `SCRIPT_CRASHED != 'true'` to prevent misleading messages from partial runs
- PR comment step uses `continue-on-error: true` to avoid failing the job on fork PRs where `GITHUB_TOKEN` is read-only

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

## Local Standards Files

Any format's compliance workflow can optionally use a local copy of its proprietary standard for more comprehensive analysis. These files are **not committed to the repo** (gitignored via `ai_artifacts/specs/*/standards_summary.md`) because they may contain proprietary content.

| File | Purpose | In repo? |
|------|---------|----------|
| `ai_artifacts/specs/*/standards_summary.md` | Proprietary standard reference (any format) | **No** — gitignored, local only |
| `ai_artifacts/specs/scc/scc_specs_summary.md` | Derived rule framework (44 rules) | Yes |
| `ai_artifacts/specs/scc/scc_web_summary.md` | Summarized from public web sources | Yes |

**How it works:** When `/analyze-scc-docs` runs, it checks if `standards_summary.md` exists locally. If found, it uses it as the primary reference alongside web sources. If not found, it relies entirely on web sources. The compliance checks (`/check-scc-compliance`, CI workflows) only need `scc_specs_summary.md` — they work without the proprietary file.

Contributors with licensed copies of the relevant standards can run `/generate-standards-summary` to produce these files from PDFs (CEA-608, CEA-708, SMPTE ST 2052-1, SMPTE RP 2052-10). The skill reads the PDFs and outputs sanitized prose summaries without reproducing proprietary content.

## Gotchas

[`gotchas.md`](gotchas.md) lists past mistakes (copyright, workflow bugs, false-positive reviews, security patterns) that skills must avoid. Skills reference it in pre-flight checks and append new gotchas post-run when they discover repeatable patterns. Currently 13 gotchas covering: proprietary content, source attribution, W3C licensing, expression injection, `set -e` bugs, Slack guards, IMPL regex, false-positive reviews, gitignore coverage, SHA pinning, crash guards, fork PR failures, and module-to-package refactors.

## Notes

- Fix skills target ONE issue at a time for efficiency (~20K vs 90K tokens)
- Specs are the source of truth for compliance checks; compliance scripts read spec summaries, not raw standards
- Spec summaries: `ai_artifacts/specs/{scc,vtt,dfxp}/*_specs_summary.md`
- Master checklists: `ai_artifacts/specs/{scc,vtt,dfxp}/master_checklist.md`
- CI workflows upload compliance reports as GitHub Actions artifacts (90-day retention); local runs write to `ai_artifacts/compliance_checks/`
- Slack notifications require `SLACK_BOT_TOKEN` and `SLACK_CHANNEL_ID` repository secrets
- `${{ github.token }}` is used automatically for GitHub API calls (no secret setup needed)

---
**Last Updated**: 2026-07-30
