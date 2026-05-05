Structured feature/bug implementation workflow. Usage example: /ship-it "fix EDM being ignored in paint-on mode"

Ultrathink!

The user wants to work on: $ARGUMENTS

Follow the stages below in order. At each checkpoint, STOP and wait for user input before proceeding to the next stage.

---

## Stage 1: Understand

1. **Pre-flight check**: Run `git status` to verify the working tree is clean. If there are modified or staged files, STOP and ask the user whether to stash them, commit them first, or proceed anyway (with a warning that revert will be harder). Untracked files are fine — ignore them unless they conflict with the task.
2. **Base branch check**: Verify you are on `main` or a branch that is up to date with `main`. If not, ask the user whether to rebase/merge from `main` first, or proceed on the current base (with a warning that the implementation may conflict with recent changes).
3. Read `ai_artifacts/project_understanding.md` to understand the pycaption project context.
4. Check `ai_artifacts/compliance_checks/` for any existing compliance reports related to the task.
5. Explore the codebase areas relevant to what the user described above. Look at existing patterns, files that will need changes, and related test files.
6. Ask the user: **What type of change is this?**
   - **Bug fix** → patch version bump (X.Y.Z → X.Y.Z+1)
   - **New feature** → minor version bump (X.Y.Z → X.Y+1.0)
   - **Refactor / CI / chore** → no version bump unless it changes public behavior

**CHECKPOINT**: Wait for the user to confirm the change type before proceeding.

---

## Stage 2: Design

Based on your understanding, create **1 to 2 implementation variants**.

For each variant, present:
- **Approach**: Brief description of how it works
- **Files to modify/create**: List each file with a one-line explanation of the change
- **Spec reference**: Which spec rules this addresses (if applicable, cite rule IDs from compliance reports)
- **Trade-offs**: Pros and cons of this approach

**CHECKPOINT**: Present the variants and wait for the user to choose one.

---

## Stage 3: Implement

Implement the chosen variant.

- Create a feature branch from the current branch if you are on `main`. If already on a feature branch (e.g., `OCTO-*`, `fix/*`, `feat/*`), stay on it. Use `fix/<short-description>` for bug fixes, `feat/<short-description>` for features.
- Follow existing project patterns and conventions
- Keep changes minimal and focused
- Ensure compliance with the relevant caption format specification (CEA-608 for SCC, TTML for DFXP, W3C for WebVTT)
- If the change touches shared code (`base.py`, `geometry.py`, `exceptions.py`), note which formats may be affected and plan to run cross-format tests in Stage 4
- After implementing, present a summary of all files changed and what was done in each

**CHECKPOINT**: Wait for user to review and confirm before proceeding to tests.

---

## Stage 4: Test

Write tests for the implementation.

- Tests go in `tests/` directory, matching existing test file for the format (e.g., `test_scc.py`)
- Define new fixtures in `tests/fixtures/<format>.py` (e.g., `fixtures/scc.py`) as session-scoped pytest fixtures
- Add the import for any new fixtures to `tests/conftest.py` (this is the registration step — conftest re-exports, it doesn't define)
- Use inline SCC/DFXP/WebVTT/SRT content strings as fixture data (follow existing pattern)
- Follow existing test class structure (e.g., `TestSCCReader`, `TestTimingCorrectingCaptionList`)
- Run the full test suite: `python -m pytest tests/ -q`
- Present test results
- If tests fail, diagnose the failure and fix the implementation. Re-run the suite. Fixes here should be limited to test plumbing or minor corrections — if the fix requires changing the core approach, STOP and loop back to Stage 2.
- If after 3 attempts tests still fail, STOP and present the failures to the user with options:
  - (a) continue debugging together
  - (b) revert all changes from Stage 3 onward and return to Stage 2 to pick a different variant

**CHECKPOINT**: Wait for user to review tests and results before proceeding to review.

---

## Stage 5: Review

Re-read all files you modified or created from disk (not from conversation memory). Review the implementation against these principles:

### Python (Zen of Python)
1. Don't repeat yourself
2. Explicit is better than implicit
3. Simple is better than complex
4. Complex is better than complicated
5. Flat is better than nested
6. Sparse is better than dense
7. Readability counts
8. Special cases aren't special enough to break the rules
9. Practicality beats purity
10. In the face of ambiguity, don't guess
11. There should be one -- and preferably only one -- obvious way to do it
12. If the implementation is hard to explain, it's a bad idea
13. If the implementation is easy to explain, it may be a good idea

### Caption-Specific
14. Timing values must be in microseconds (project convention)
15. Buffer/state resets must be complete (buffer + position tracker + time)
16. Control code handling must respect mode (pop-on vs paint-on vs roll-up)
17. Implicit timing correction (TimingCorrectingCaptionList) must not be disrupted
18. Changes must not break cross-format conversion (SCC->DFXP, SCC->WebVTT, etc.)

### Practical
19. Code should be as isolated and self-contained as possible
20. A change should be easy to delete and create again under a different flavor
21. Edge cases (empty buffers, mode switches, doubled commands) must be handled

### Security
22. Code validates all inputs and fails securely
23. No injection vulnerabilities in format parsing
24. Malformed input must not cause crashes or infinite loops

For each issue found, present a **numbered proposal**:

**Proposal N: <title>**
- **Principle**: Which principle this addresses
- **File**: Path to the file
- **Current**: The current code
- **Proposed**: The rewritten code
- **Why**: Brief explanation

If the implementation already follows all principles, say so explicitly and skip to Stage 6.

**CHECKPOINT**: Ask the user which proposals to accept. They can respond with:
- "accept all" or "reject all"
- "accept 1, 3" or "reject 2"
- "accept 1 but change X to Y"

---

## Stage 6: Finalize

1. Apply all accepted proposals from Stage 5.
2. Update test cases to reflect any changes made during review.
3. Bump the version in `setup.py` (the `version=` parameter) — but first check if the version was already bumped in this branch (`git diff main -- setup.py`). If already bumped, skip this step.
   - **Bug fix**: increment the patch number (e.g., X.Y.Z -> X.Y.Z+1)
   - **New feature**: increment the minor number and reset patch (e.g., X.Y.Z -> X.Y+1.0)
   - **Refactor / CI / chore**: skip version bump
4. Re-run the full test suite: `python -m pytest tests/ -q`
5. If tests fail after applying review proposals, diagnose and fix. If the fix is non-trivial, STOP and present the issue to the user with options:
   - (a) revert the failing proposals and re-commit without them
   - (b) debug together
6. If a compliance check skill exists for the format (`/check-scc-compliance`, `/check-dfxp-compliance`, or `/check-vtt-compliance`), re-run it to regenerate the report. If the task involves a format without a compliance skill (SRT, SAMI, MicroDVD), skip this step. If the compliance report shows new regressions not present before this change, STOP and present them to the user before committing.
7. Check if `main` has advanced: `git fetch origin main && git log HEAD..origin/main --oneline`. If new commits exist on `main`, ask the user whether to rebase/merge before committing or proceed as-is.
8. Stage only the files modified or created during this workflow — do not use `git add -A` or `git add .` (untracked files from other work must not be included).
9. Commit with a descriptive message summarizing the fix/feature.
10. Present a final summary of ALL changes made throughout the entire workflow (Stages 3 through 6).
