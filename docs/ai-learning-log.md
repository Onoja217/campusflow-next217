# CampusFlow Next — AI-assisted learning and verification log

**Repository:** [Onoja217/campusflow-next217](https://github.com/Onoja217/campusflow-next217)  
**Purpose:** Record genuine AI-assisted learning separately from code-review, implementation, and test evidence.

> **Evidence-integrity rule:** Git history, PR comments, and passing tests prove engineering activity or test outcomes; they do not prove which AI prompt a person used, what that person learned, or whether a suggestion came from AI. Do not invent prompts, first-person reflections, or acceptance/rejection decisions. Each engineer must complete the AI-specific fields from their own actual interaction history.

## Engineer A — Onoja Monday Ojonugba

### Evidence example A1 — Follow-up-note validation and persistence

- **Verified engineering task:** Implemented the follow-up-note contract and validation/persistence changes in PR #51.
- **AI prompt actually used:** **Not recorded in the repository evidence available for this audit.** Onoja must add the exact prompt or honestly state that the prompt is unavailable.
- **Initial understanding:** **Onoja to describe in their own words.**
- **Independent check / experiment:** The merged implementation has automated tests for note validation, legacy records, persistence, and invalid operations. A specific test reference is `tests/test_follow_up_notes.py`; the repository's test suite can be run with `python3 -m unittest discover -s tests -v`.
- **Observed result:** PR #51 was merged. The available test output in the audit context includes `test_resolved_ticket_rejects_notes_without_mutation` passing. Do not treat that single test as proof of every persistence case.
- **Relevant review feedback:** [PR #51](https://github.com/Onoja217/campusflow-next217/pull/51) includes feedback about rejecting malformed note collections and validating existing note entries before mutation.
- **Code/test references:** [`campusflow/tickets.py`](https://github.com/Onoja217/campusflow-next217/blob/main/campusflow/tickets.py), [`campusflow/persistence.py`](https://github.com/Onoja217/campusflow-next217/blob/main/campusflow/persistence.py), [`tests/test_follow_up_notes.py`](https://github.com/Onoja217/campusflow-next217/blob/main/tests/test_follow_up_notes.py), [PR #51](https://github.com/Onoja217/campusflow-next217/pull/51).
- **AI suggestion accepted / improved / rejected:** **Onoja to record only after checking their actual AI conversation.**
- **Learning reflection:** **Onoja to write in their own words:** what assumption changed, what they still need to understand, and how they verified the behaviour.

### Evidence example A2 — Peer review of search and filter behaviour

- **Verified engineering task:** Reviewed PR #50 and identified that the interactive CLI search branch did not pause after displaying results; requested a pause and a regression test. The review also asked for clarity on how follow-up-note functionality relates to Issue #47.
- **AI prompt actually used:** **Not recorded; do not substitute the review comment for an AI prompt.**
- **Independent check / experiment:** The review concern is tied to the CLI implementation and regression coverage. Relevant references are [PR #50](https://github.com/Onoja217/campusflow-next217/pull/50) and [`tests/test_cli.py`](https://github.com/Onoja217/campusflow-next217/blob/main/tests/test_cli.py).
- **Observed response/change:** Oabah1 replied that the search output pause and regression test were added and that the shared follow-up-note API was integrated into CLI options 11 and 12.
- **AI suggestion accepted / improved / rejected:** **Onoja to fill from a real AI interaction, if AI was used.**
- **Learning reflection:** **Onoja to complete personally.**

### Critical-thinking entry — required if AI was used

- **Actual AI suggestion:** **Not captured in repository evidence; add exact wording or mark unavailable.**
- **What was incomplete or incorrect:** **Onoja to explain from the real interaction.**
- **What was changed or rejected:** **Onoja to explain, linking the relevant diff/test.**
- **Verification:** Use a real test output, code reference, or review link; do not infer that a code review was an AI suggestion.

## Engineer B — Oabah1 (GitHub account)

> The repository identifies the PR #50 author as GitHub user **Oabah1**. The repository evidence reviewed here does not establish that person's full legal/display name; use their preferred name only after they confirm it.

### Evidence example B1 — Search, combined filters, and reports

- **Verified engineering task:** Authored PR #50, adding ticket search, category/status/priority filters, report analytics, and CLI integration.
- **AI prompt actually used:** **Not recorded in the repository evidence available for this audit.** Oabah1 must add the actual prompt from their own AI history or state that it is unavailable.
- **Initial understanding:** **Oabah1 to describe in their own words.**
- **Independent check / experiment:** PR #50 describes combined criteria using AND logic and report handling for an empty ticket collection (resolution percentage `0.0%`). Relevant tests include [`tests/test_search.py`](https://github.com/Onoja217/campusflow-next217/blob/main/tests/test_search.py), [`tests/test_reports.py`](https://github.com/Onoja217/campusflow-next217/blob/main/tests/test_reports.py), and [`tests/test_cli.py`](https://github.com/Onoja217/campusflow-next217/blob/main/tests/test_cli.py).
- **Observed result:** PR #50's verification record reports 117 tests passing locally and GitHub Actions run #154 passing on commit [`267a143a9787a7892d5c156c7f868fe35b8802a3`](https://github.com/Onoja217/campusflow-next217/commit/267a143a9787a7892d5c156c7f868fe35b8802a3). The current audit also observed a local run of 117 tests passing; cite the actual terminal output if attaching it as evidence.
- **Relevant review feedback and code change:** [PR #50](https://github.com/Onoja217/campusflow-next217/pull/50) records feedback that interactive search results needed a pause and regression test. The author replied that the pause/test were added, with additional filter tests and failed-save rollback coverage.
- **AI suggestion accepted / improved / rejected:** **Oabah1 to record only after checking their actual AI conversation.**
- **Learning reflection:** **Oabah1 to write in their own words.**

### Critical-thinking entry — required if AI was used

- **Actual AI suggestion:** **Not captured in repository evidence; add exact wording or mark unavailable.**
- **What was incomplete or incorrect:** **Oabah1 to explain from the real interaction.**
- **What was changed or rejected:** **Oabah1 to explain, linking the relevant diff/test.**
- **Verification:** Link a real test result or code review. Do not claim that review feedback originated from AI.

## Completion status

- [x] Corrected the project/repository references to CampusFlow Next.
- [x] Replaced the stale Fellow 2 label with the PR #50 author account Oabah1, without guessing a personal name.
- [x] Added concrete, traceable implementation/review/test examples for both engineers.
- [x] Distinguished peer-review feedback from AI prompts.
- [ ] Engineer A records at least three genuine AI interactions, if required by the assignment rubric, from their own conversation history.
- [ ] Engineer B records at least three genuine AI interactions, if required by the assignment rubric, from their own conversation history.
- [ ] Each engineer records at least one real AI suggestion they corrected, improved, or rejected, with the actual prompt and verification.
- [ ] Both engineers add personal reflections in their own words and confirm the log is accurate.

**Audit conclusion:** The repository supports the engineering and review examples linked above, but does not itself establish each engineer's actual AI prompts or personal learning. Keep the learning-evidence requirement marked **in progress** until each engineer supplies those genuine details.