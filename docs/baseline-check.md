# CampusFlow baseline audit — Issue #47

**Audit date:** 2026-10-14  
**Repository:** [Onoja217/campusflow-next217](https://github.com/Onoja217/campusflow-next217)  
**Baseline branch:** `main`  
**Baseline commit:** [`755a7c07e41b8f756d0855b935a2ca92bc797005`](https://github.com/Onoja217/campusflow-next217/commit/755a7c07e41b8f756d0855b935a2ca92bc797005)  
**Scope:** Observe current behavior before implementing [Issue #47](https://github.com/Onoja217/campusflow-next217/issues/47). No application code was changed as part of this audit.

## Test execution evidence

The repository's GitHub Actions workflow `.github/workflows/tests.yml` checks out the repository, configures Python 3.12, and runs:

```bash
python -m unittest discover -s tests -v
```

The baseline audit recorded a successful GitHub Actions run for the baseline commit:

- Workflow run: [Python tests #106](https://github.com/Onoja217/campusflow-next217/actions/runs/38140531687)
- Job: `unittest` — reported as completed successfully in the audit evidence.
- Test command result: **86 tests ran in 5.733 seconds**.
- The recorded log listed 86 test cases ending in `ok`; no test failures were reported.
- Runtime recorded in the audit: GitHub-hosted Ubuntu 24.04, Python 3.12.15.

A separate local clone/test attempt in the assistant execution environment could not resolve `github.com`. Therefore, this report distinguishes the recorded remote CI result from local execution; it does **not** claim that the tests were rerun locally on 2026-10-14. The run details above are the evidence captured during the audit, not a new rerun performed by this documentation update.

## Existing safeguards observed

### Ticket lifecycle and assignment

The existing `tests/test_ticket_status.py` covers the standard lifecycle, including:

- An assigned ticket can move through `open → in_progress → resolved`.
- An unassigned ticket cannot enter `in_progress`.
- An open ticket cannot be resolved directly.
- A resolved ticket rejects normal status changes.
- Reopening is explicit and only applies to resolved tickets.
- Unsupported statuses and missing ticket IDs are rejected.
- Status updates are reflected in the mutable ticket record.

The existing `tests/test_ticket_assignment.py` covers assignment validation, rejection of blank/unknown IDs and blank assignees, avoiding mutation on failed assignments, and rejection of assignment changes for resolved tickets.

### JSON persistence

The existing `tests/test_persistence.py` covers:

- Project-root-anchored default storage path.
- Missing files loading as an empty collection.
- Unicode and all-field save/load round trips.
- Empty collection serialization as a JSON array.
- Rejection of malformed JSON, non-array documents, invalid record shapes/types/statuses, and duplicate ticket IDs.
- Rejection of invalid records on save.
- Continuing ticket ID generation from the highest ID after reload.
- Preserving the previous file when atomic replacement fails.
- Treating unreadable files as errors rather than as missing files.

The CLI persistence smoke tests also cover persistence across separate CLI runs and retaining assignee/status fields.

## Issue #47 gaps to address

These are target behaviors for implementation, not claims that the current code already supports them:

1. **Structured follow-up notes:** The current ticket schema and listed persistence tests do not show a notes field or note lifecycle. Agree on a stable note record and API before implementation. Notes should have sequential IDs, be added only to open or in-progress tickets, and remain attached when a ticket is resolved and reopened.
2. **Rejected operations must be side-effect-free:** Add focused tests proving rejected note additions do not change ticket state or consume a note ID. For example, if the first successful note receives `N001`, a rejected attempt must not use an ID; the next successful note should receive `N002`. Apply the same no-mutation expectation to rejected status and assignment operations.
3. **Atomic in-memory loading:** Existing tests establish several file-validation safeguards, but add a regression test that starts with a populated in-memory store, attempts to load a malformed or duplicate-ID document, and verifies that the original records remain unchanged after the load is rejected. Validate the complete incoming document before replacing the current in-memory collection.
4. **End-to-end ID continuity:** Extend coverage to note IDs across save/reload and a fresh process, where appropriate for the agreed note API. Confirm the next successful note gets the next ID rather than reusing an existing one.
5. **Cross-feature contract with Issue #48:** Before CLI work is implemented, agree with the Issue #48 engineer on the note data shape, the functions for adding and retrieving notes, how IDs are generated, and the error/return conventions. The CLI should call the shared API rather than duplicate validation. Record the final agreement in the relevant project documentation.

### Suggested contract to agree on

This is a proposal for the two engineers to confirm, not a claim that the API already exists:

- A note contains a stable note ID, note text, and a creation timestamp if the project already uses timestamps consistently.
- The ticket stores its notes in creation order, and notes are saved and loaded as part of the ticket's JSON representation.
- One shared service function validates and adds a note; a separate read function returns a ticket's notes without changing them.
- A note can be added only while the ticket status is `open` or `in_progress`. Resolving or reopening a ticket must not delete its existing notes.
- A rejected operation returns the project's agreed error result or raises its agreed exception, leaves ticket data unchanged, and does not advance the note-ID counter.
- Loading validates the full document before replacing the active in-memory records. A failed load leaves the old records and ID counters intact.

## Baseline acceptance — historical record

At the original baseline commit, the existing suite was recorded as green: 86 tests passed in the GitHub Actions run documented above. That was baseline evidence, not a local test run during this audit.

## Issue #47 implementation and post-merge verification

Issue #47 was merged through [PR #51](https://github.com/Onoja217/campusflow-next217/pull/51) on 2026-10-14.

- **Integrated main commit:** [36dac2c891d7b620bc408d5403f421f3fe55f4ba](https://github.com/Onoja217/campusflow-next217/commit/36dac2c891d7b620bc408d5403f421f3fe55f4ba)
- **Implementation commit tested by PR CI:** [7abd6f87bafff59568efb5ff9929ee0aeea34577](https://github.com/Onoja217/campusflow-next217/commit/7abd6f87bafff59568efb5ff9929ee0aeea34577)
- **Test command:** `python -m unittest discover -s tests -v` (the workflow uses this command; Issue #47's requested local command is `python3 -m unittest discover -s tests -v`).
- **CI evidence:** [Python tests run #130](https://github.com/Onoja217/campusflow-next217/actions/runs/38583580118) completed successfully. The job log reports **99 tests ran in 5.729 seconds**.
- **Local execution:** Not performed in the connected audit environment; GitHub CI evidence is not represented as a local run.

### Scope implemented

- Immutable `FollowUpNote(id, content)` records and shared add/read functions.
- Sequential note IDs, validated note content, and note creation only for open/in-progress tickets.
- Notes retained when tickets are resolved and reopened.
- JSON note persistence with legacy records that omit `notes` remaining valid.
- Validation of ticket/note records and duplicate ticket/note IDs before a loaded collection is returned.
- Regression tests for note lifecycle, rejection without mutation, malformed notes, persistence, and ID continuity.

### Remaining verification gate

- [x] Issue #47 changes merged into `main`.
- [x] The PR's required CI run passed with 99 tests.
- [ ] Confirm a successful full-suite run on the **integrated merge commit** `36dac2c891d7b620bc408d5403f421f3fe55f4ba`; the available run cited above is tied to the PR head, not the merge commit.
- [ ] Verify any post-merge CI run and record its exact URL and test count here.

**Current decision:** The PR-head CI is green, but Issue #47 should not be described as having completed its post-merge verification gate until the integrated `main` run is confirmed.
