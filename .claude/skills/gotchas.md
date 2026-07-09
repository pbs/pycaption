# Gotchas - Mistakes Not to Repeat

Lessons from PR #369 review. Every skill that generates specs, writes workflows, or reviews PRs **MUST** check this file and avoid these mistakes.

---

## 1. Proprietary standard content in spec files

**What happened:** `scc_specs_summary.md` contained CEA-608 data tables (hex code lookup tables, character mapping tables, control code enumerations) copied from the proprietary standard. Reviewer flagged it as a copyright risk.

**Rule:** Never reproduce proprietary data tables in spec files. Instead:
- Describe codes in prose (e.g., "19 miscellaneous control codes: RCL (9420), BS (9421), ...")
- Reference `pycaption/scc/constants.py` for complete mappings
- Hex codes can appear inline in descriptions, but not as structured lookup tables derived from the standard

**Applies to:** `analyze-scc-docs`, `analyze-vtt-docs`, `analyze-dfxp-docs`, `suggest-*-fixes`

---

## 2. Source attribution pointing to proprietary standards

**What happened:** Source lines said "Sources: CEA-608 Section 4.2.1" or "Sources: CEA-608-E S-2019" — implying the spec was derived from proprietary material.

**Rule:** Use generic source citations:
- OK: "Sources: Public SCC documentation", "Sources: SCC format specification"
- OK: "CEA-608" as a technical format name (e.g., "CEA-608 bytes", "CEA-608 Line 21 data")
- NOT OK: "Sources: CEA-608", "Sources: CEA-608 Section X.Y", "Sources: CEA-608 standard"

**Applies to:** `analyze-scc-docs`, `suggest-scc-fixes`

---

## 3. W3C content needs license attribution

**What happened:** DFXP and VTT specs summarized W3C standards without attribution. W3C Document License requires it.

**Rule:** Any spec file summarizing W3C content must include in the header:
- `**License**: Requirements summarized from [spec name], Copyright (c) W3C. Published under the [license name] ([url]).`

**Applies to:** `analyze-vtt-docs`, `analyze-dfxp-docs`

---

## 4. `${{ env.VAR }}` in workflow `run:` blocks

**What happened:** Workflows used `${{ env.VAR }}` in shell `run:` blocks. While safe when values are workflow-controlled, this is an expression injection vector if values ever become user-controllable.

**Rule:** Always use `$VAR` (shell expansion) instead of `${{ env.VAR }}` in `run:` blocks. Reserve `${{ }}` for `if:` conditions, `with:` parameters, and `env:` mappings where shell expansion is not available.

This is especially dangerous for **attacker-controlled GitHub context values** like `github.head_ref`, `github.event.pull_request.title`, `github.event.pull_request.body`, and `github.event.comment.body`. These are fully user-controlled and MUST never appear in `run:` blocks. Pass them through an `env:` mapping instead:
```yaml
env:
  HEAD_REF: ${{ github.head_ref || github.ref }}
run: |
  BRANCH="$HEAD_REF"
```

**Applies to:** All workflow files, `check-last-pr`

---

## 5. `set -e` kills exit code capture in multi-command scripts

**What happened:** `all_compliance_checks.yml` ran `python3 script.py; EXIT=$?` — but GitHub Actions uses `bash -e` by default, so a non-zero exit terminates bash before `EXIT=$?` executes. Subsequent checks never ran and the job passed green with no data.

**Rule:** To capture exit codes under `set -e`, use:
```bash
command && EXIT=0 || EXIT=$?
```
Never use `command; EXIT=$?` in GitHub Actions `run:` blocks.

**Applies to:** All workflow files, `check-last-pr`

---

## 6. Slack notification guard must check both secrets

**What happened:** Slack availability check only tested `SLACK_BOT_TOKEN` but not `SLACK_CHANNEL_ID`. If one was missing, the notification step would fail.

**Rule:** Always check both secrets:
```yaml
if [ -n "$SLACK_TOKEN" ] && [ -n "$SLACK_CHANNEL" ]; then
```
With both passed via `env:` block.

**Applies to:** All workflow files

---

## 7. IMPL rule regex must handle both formats

**What happened:** SCC skill used `IMPL-[A-Z]+-\d{3}` (requires category prefix), DFXP used `IMPL-\d{3}` (no prefix). Neither matched the other format's IDs.

**Rule:** Always use the unified regex: `IMPL-(?:[A-Z]+-)?\d{3}` — matches both `IMPL-FMT-001` and `IMPL-001`.

**Applies to:** `check-scc-compliance`, `check-vtt-compliance`, `check-dfxp-compliance`

---

## 8. PR review must verify claims before reporting

**What happened:** Initial PR review reported 13 issues. On verification, many were false positives (e.g., "missing mkdir" when Python scripts use `os.makedirs`, "heredoc indentation" when YAML `|` handles it). This eroded trust.

**Rule:** Before reporting an issue, verify it is real:
- Read the actual code, not just the diff
- Check if the concern is already handled elsewhere
- Test the claim (run the script, check the YAML spec)

**Applies to:** `check-last-pr`

---

## 9. `.gitignore` pattern should cover all formats

**What happened:** `.gitignore` only blocked `ai_artifacts/specs/scc/standards_summary.md`. If someone added a proprietary DFXP or VTT standard, it wouldn't be gitignored.

**Rule:** Use glob pattern `ai_artifacts/specs/*/standards_summary.md` to cover all formats.

**Applies to:** `.gitignore`, `analyze-*-docs`

---

## 10. Third-party actions must be SHA-pinned and workflows need explicit `permissions:`

**What happened:** `unit_tests.yml` used `slackapi/slack-github-action@v3.0.2` (mutable tag) while compliance workflows correctly SHA-pinned their Slack action. Four workflows also lacked a `permissions:` block, getting default write-all permissions.

**Rule:**
- All third-party GitHub Actions (anything not under `actions/`) MUST be pinned to a full commit SHA, not a mutable tag. A compromised tag update can exfiltrate secrets.
- Every workflow MUST declare an explicit `permissions:` block with minimal scopes. Never rely on default write-all.

**Applies to:** All workflow files, `check-last-pr`

---

## 11. Don't send Slack success before confirming the script didn't crash

**What happened:** Compliance workflows used `continue-on-error: true` on the script step so metric extraction could proceed. But the Slack success notification fired based on `REPORT_EXISTS=true` without checking `SCRIPT_CRASHED`. A script that crashes after partially writing a report sends a misleading "success" with incomplete metrics.

**Rule:** Slack success notifications must also check that the script did not crash:
```yaml
if: env.REPORT_EXISTS == 'true' && env.SCRIPT_CRASHED != 'true'
```

**Applies to:** All compliance workflow files, `check-last-pr`

---

## 12. Fork PRs break `pull-requests: write` steps

**What happened:** `pr_compliance_check.yml` uses `actions/github-script` to comment on PRs. On fork PRs, `GITHUB_TOKEN` is read-only, so the `createComment` API call returns 403 and fails the entire job — even though the compliance analysis itself succeeded.

**Rule:** Any step that writes to a PR (comments, labels, status checks) must either:
- Use `continue-on-error: true` so the job doesn't fail on forks, or
- Add a fork check to the `if:` condition: `&& !github.event.pull_request.head.repo.fork`

**Applies to:** `pr_compliance_check`, `check-last-pr`, any new workflow that comments on PRs

---

## 13. Module-to-package refactors flagged as removed public API

**What happened:** PR #387 split `pycaption/webvtt.py` into `pycaption/webvtt/` package (reader.py, writer.py, constants.py, __init__.py with re-exports). The review tool compared the old single file against `reader.py` only and flagged `microseconds`, `WebVTTWriter`, and `write` as "REMOVED_PUBLIC_DEF/CLASS" — all critical. In reality they were moved to sibling files and re-exported from `__init__.py`.

**Rule:** When reviewing a diff that deletes a module and adds a same-named package directory:
- Check `__init__.py` re-exports before flagging anything as removed
- Verify import paths still work (`from pycaption import X` and `from pycaption.subpackage import Y`)
- Only flag as "removed" if the symbol is genuinely absent from all new files AND not re-exported

**Applies to:** `check-last-pr`

---

*Last updated: 2026-07-09*
