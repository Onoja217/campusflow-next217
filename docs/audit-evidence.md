# CampusFlow audit evidence register

**Updated:** 15 October 2026  
**Repository:** [Onoja217/campusflow-next217](https://github.com/Onoja217/campusflow-next217)

This register separates automated verification, practical demonstration, learning evidence, and independent review. A passing test suite is important, but it does not prove that every audit requirement is complete.

## 1. Automated verification

| Item | Evidence | What it establishes | Boundary |
| --- | --- | --- | --- |
| Issue #47 merged implementation | [PR #51](https://github.com/Onoja217/campusflow-next217/pull/51) | Follow-up-note API, validation, persistence, and regression tests were merged. | Does not establish the status of Issue #48. |
| Issue #47 integrated-main CI | [Actions run #139](https://github.com/Onoja217/campusflow-next217/actions/runs/38589183338) | 100 tests passed on main commit [`7d42c129ad9710592651d85e6bcae024df4639d7`](https://github.com/Onoja217/campusflow-next217/commit/7d42c129ad9710592651d85e6bcae024df4639d7). | Remote GitHub Actions evidence, not a local run. |
| Issue #48 feature branch | [PR #50](https://github.com/Onoja217/campusflow-next217/pull/50) | The PR description records 117 local tests passing, `git diff --check` passing, and latest-head CI run [#154](https://github.com/Onoja217/campusflow-next217/actions/runs/38744979052) passing on commit [`267a143a9787a7892d5c156c7f868fe35b8802a3`](https://github.com/Onoja217/campusflow-next217/commit/267a143a9787a7892d5c156c7f868fe35b8802a3). | These are PR-head results. Verify the live PR state and final merged commit before calling Issue #48 complete. |
| Historical Issue #47 baseline | [Baseline audit](baseline-check.md) | Records the earlier 86-test baseline and later implementation verification separately. | Historical test counts must not be presented as the current test count. |

## 2. Practical demonstration

The project owner has reported an interactive CLI demonstration using sample ticket IDs T001–T005. Reported checks included assigning T002 to Onoja, checking malformed/invalid input, and observing the pause behavior for menu output so list, queue, and report results remain visible.

This is recorded as **owner-reported demonstration evidence**, not an independently witnessed audit. No transcript, screenshot, recording, or reviewer sign-off is attached to this register.

### Evidence to attach for a reproducible audit

- [ ] Record the date, operating system, Python version, branch, and commit SHA used for the demonstration.
- [ ] Capture the CLI startup and menu, without exposing personal or sensitive data.
- [ ] Demonstrate a valid ticket and its calculated priority.
- [ ] Demonstrate an invalid input being rejected without creating or corrupting a ticket.
- [ ] Demonstrate assignment and the permitted status lifecycle.
- [ ] Demonstrate the unresolved queue and report staying visible until Enter is pressed.
- [ ] If auditing Issue #48, demonstrate title search, each individual filter, combined AND filters, report totals, adding/viewing a note, and note persistence after restart.
- [ ] Have a peer or mentor observe the demonstration and record their name, date, feedback, and any follow-up action.

Do not mark these boxes complete unless the evidence is actually captured. The checklist is a plan for collecting evidence, not a claim that all steps have been independently verified.

## 3. Learning and review evidence

Automated tests and authored code do not by themselves establish authentic learning reflections, critical evaluation of AI assistance, or partner/mentor review. These records must be written by the people who performed the work; this document does not invent prompts, personal reflections, feedback, or review outcomes.

- [ ] Each fellow records their own actual AI-assisted interactions, including the task, the suggestion received, what they checked, and what they accepted, changed, or rejected.
- [ ] Each fellow records a concrete correction or improvement they made after checking a suggestion, with a link to the relevant commit/PR or test where possible.
- [ ] Each fellow writes a short personal reflection in their own words: what they learned, what they still do not understand, and how they verified the result.
- [ ] Record genuine peer/mentor feedback with a link to the review/comment and the change made in response. Do not substitute CI status for a human review.
- [ ] Confirm any assignment-specific minimum interaction count against the official rubric and link each real interaction. Do not fill missing entries with reconstructed or hypothetical conversations.

If a learning log exists in another branch or submission folder, link the actual file here after confirming its location and contents.

## 4. Documentation accuracy checks

- [x] README clone instructions point to `Onoja217/campusflow-next217`.
- [x] README describes the CLI options through 12, including follow-up notes.
- [x] README distinguishes Issue #47 (merged) from Issue #48 (PR #50; status must be checked before declaring merged).
- [x] CI evidence is linked to a specific workflow run and commit rather than stated as an undated generic pass.
- [x] README explicitly distinguishes owner-reported practical checks from independently captured evidence.
- [ ] After the PR #50 status is confirmed, update README and this register with the actual final state and final commit SHA.
- [ ] Add dated practical-demo artifacts and genuine learning/review records when available.

## Audit conclusion

The repository has substantial automated verification evidence. The documentation now records the evidence sources and avoids claiming that tests prove a practical demonstration or learning/review requirements are complete. The overall audit should remain **in progress** until the current Issue #48 merge/review state is confirmed and the practical-demo, learning, and independent-review evidence is attached or explicitly marked not applicable by the official rubric.
