# CampusFlow baseline audit — Issue #47

**Audit date:** 2026-10-14  
**Repository:** [Onoja217/campusflow-next217](https://github.com/Onoja217/campusflow-next217)  
**Baseline branch:** `main`  
**Baseline commit:** [`755a7c07e41b8f756d0855b935a2ca92bc797005`](https://github.com/Onoja217/campusflow-next217/commit/755a7c07e41b8f756d0855b935a2ca92bc797005)  
**Scope:** Observe current behavior before implementing [Issue #47](https://github.com/Onoja217/campusflow-next217/issues/47).

## Test execution evidence

The baseline audit recorded a successful GitHub Actions run for the baseline commit:

- Workflow run: [Python tests #106](https://github.com/Onoja217/campusflow-next217/actions/runs/38140531687)
- Command recorded by the workflow: `python -m unittest discover -s tests -v`
- Result recorded in the audit: **86 tests passed in 5.733 seconds**.
- Runtime recorded: GitHub-hosted Ubuntu 24.04, Python 3.12.15.

A separate local clone/test attempt could not resolve `github.com`. Therefore, this file distinguishes the previously recorded remote CI result from local execution; it does not claim the baseline tests were rerun locally in this session. The implementation branch must be validated by its own CI run.

## Existing safeguards observed

- Ticket creation validates title, category, urgency, and positive integer affected-user counts before appending.
- Priority is calculated centrally from urgency and affected-user count.
- An unassigned ticket cannot move to `in_progress`; a resolved ticket cannot be reassigned through normal assignment actions.
- JSON loading validates ticket records and duplicate ticket IDs before returning a replacement collection.
- JSON saves use a temporary file and atomic replacement.
- Existing tests cover lifecycle transitions, priority rules, CLI behavior, queue ordering, reports, persistence, and dashboard smoke paths.

## Issue #47 gaps targeted

1. Add structured follow-up notes with sequential IDs and validated content.
2. Reject notes on resolved tickets without mutating ticket state or consuming an ID.
3. Preserve notes through resolve/reopen and save/reload.
4. Reject malformed note records and duplicate note IDs as well as invalid/duplicate ticket IDs.
5. Preserve legacy valid ticket JSON that omits the new `notes` field.
6. Add focused tests for note lifecycle, non-mutation, malformed persistence data, and ID continuity.

## Cross-engineer API proposal

The proposed shared data-layer API is:

- `FollowUpNote(id, content)`, where IDs use `N001`, `N002`, etc. and are allocated globally across the collection.
- `add_follow_up_note(tickets, ticket_id, content)` validates and appends a note, returning the created note or raising `TicketValidationError`.
- `get_follow_up_notes(tickets, ticket_id)` returns notes in creation order without mutating state.
- Notes are stored in each ticket's `notes` array in JSON. Existing ticket records without that field load with an empty note collection.
- Notes may be added only while a ticket is `open` or `in_progress`; existing notes remain attached when the ticket is resolved or reopened.
- Rejected operations must leave ticket data and the next generated note ID unchanged.

Engineer B should confirm this contract before implementing the Issue #48 CLI note menu. The API intentionally keeps validation in the data layer rather than duplicating it in the CLI.

## Execution status

- [x] Inspect latest `main` and relevant ticket, persistence, and test modules.
- [x] Record baseline commit and previously recorded remote CI result.
- [x] Create focused branch from the inspected `main` commit.
- [ ] Run new and existing tests in CI; do not claim a pass until the run completes.
- [ ] Obtain Engineer B's specific review of the schema, API, diff, and tests.
- [ ] Address feedback and rerun the full suite on the integrated `main` after merge.

**Baseline decision:** Proceed additively from the recorded green baseline. Do not rewrite the application, reset project data, or merge without successful CI and substantive peer review.
