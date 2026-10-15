# CampusFlow

CampusFlow is a Python helpdesk ticket tracker with an interactive command-line interface (CLI) and a local browser dashboard. It supports validated ticket creation, automatic priority calculation, assignment, status changes, an unresolved-ticket priority queue, workload reports by status and priority, and JSON persistence.

## Current development status (15 October 2026)

- **Issue #47 — reliability and follow-up notes:** merged through [PR #51](https://github.com/Onoja217/campusflow-next217/pull/51). The shared note API supports validated notes on open/in-progress tickets, sequential note IDs, JSON persistence, and retaining notes through resolve/reopen. Legacy ticket records without a `notes` field remain supported.
- **Verification:** GitHub Actions run [#139](https://github.com/Onoja217/campusflow-next217/actions/runs/38589183338) passed **100 tests** on integrated `main` commit [`7d42c129ad9710592651d85e6bcae024df4639d7`](https://github.com/Onoja217/campusflow-next217/commit/7d42c129ad9710592651d85e6bcae024df4639d7). The latest local run reported by the project owner passed 114 tests using `python3 -m unittest discover -s tests -v`.
- **Issue #48 — search, filters, reports, and CLI note integration:** in progress in [draft PR #50](https://github.com/Onoja217/campusflow-next217/pull/50), owned by Engineer B (Oabah1). The draft covers case-insensitive title search, AND-combined category/status/priority filters, expanded report counts, and safe resolution percentages. Follow-up-note CLI actions are implemented as menu option 11 (add) and menu option 12 (view), using Issue #47's shared API and covered by CLI tests. These draft changes are **not yet part of `main`**.
- **Next integration gate:** review the completed CLI note integration, obtain peer review, and confirm all required CI checks pass before merging PR #50.

## Features

- **Create tickets:** validate the title, category, urgency, and positive affected-user count.
- **Calculate priority:** assign `critical`, `high`, `medium`, or `low` automatically.
- **Generate ticket IDs:** use sequential IDs such as `T001`, `T002`, and so on.
- **Find tickets:** list all tickets or view one ticket by ID.
- **Search and filter tickets:** search titles without case sensitivity and combine category, status, and priority filters.
- **Assign tickets:** record the person responsible for an unresolved ticket.
- **Manage status:** follow the `open → in_progress → resolved` workflow, with an explicit action to reopen resolved tickets.
- **Review the priority queue:** order unresolved tickets by priority; resolved tickets are excluded.
- **View workload reports:** show totals by status and priority, including categories with zero tickets.
- **Save work:** persist tickets in JSON so they remain available after restart.
- **Record follow-up notes:** use CLI menu options 11 and 12 to add and retrieve validated notes through the shared ticket API; notes persist in JSON and remain attached when a ticket is resolved and reopened.
- **Use either interface:** the CLI and browser dashboard share the same ticket rules and default JSON file.

## Requirements

- Python 3.10 or newer
- No third-party runtime dependencies

## Setup

Clone the repository and open a terminal in the repository root:

```bash
git clone https://github.com/Onoja217/campusflow-next217.git
cd campusflow-next217
```

Confirm that Python 3.10 or newer is available:

```bash
python3 --version
```

On Windows, use `python` instead of `python3` if that is the command configured on your system. CampusFlow uses only the Python standard library, so no package installation step is required.

## Run the CLI

From the repository root:

```bash
python3 -m campusflow.cli
```

| Option | Action |
| --- | --- |
| 1 | Create ticket |
| 2 | List all tickets |
| 3 | View ticket by ID |
| 4 | Assign ticket |
| 5 | Change ticket status |
| 6 | Reopen resolved ticket |
| 7 | Exit |
| 8 | Show unresolved priority queue |
| 9 | Show ticket report |
| 10 | Search tickets and combine filters |
| 11 | Add a follow-up note to an eligible ticket |
| 12 | View follow-up notes for a ticket |

## Run the browser dashboard

The dashboard uses Python's built-in HTTP server and does not require a separate frontend framework or JavaScript package dependencies.

1. From the repository root, run:

   ```bash
   python3 -m campusflow.web
   ```

2. Open [http://localhost:3000](http://localhost:3000) in your browser.
3. Keep the terminal open while using the dashboard. Stop the server with `Ctrl+C`.

The dashboard supports creating and searching tickets, filtering the list, assigning owners, changing status, reopening resolved tickets, and viewing the unresolved priority queue. If port 3000 is already in use, stop the other process before starting CampusFlow.

## Troubleshooting

- **The CLI does not start:** confirm Python 3.10 or newer with `python3 --version`, run the command from the repository root, and check that the package folder is named `campusflow`.
- **The browser page does not load:** start the server with `python3 -m campusflow.web`, keep that terminal running, and open `http://localhost:3000`. If port 3000 is already occupied, stop the other local process and retry.
- **Tickets seem to disappear after restarting or between the CLI and dashboard:** the default data file is anchored to the project root, so both interfaces use the same `data/tickets.json` regardless of the terminal's current directory. Check that this file exists and contains valid JSON; back it up before making manual changes.
- **A persistence error appears:** do not delete or overwrite the data file as a first response. Make a backup, inspect the error, and validate the JSON. A malformed file should be repaired deliberately rather than silently replaced.
- **The test suite cannot find tests:** run `python3 -m unittest discover -s tests -v` from the repository root and confirm the `tests/` directory is present.
- **A browser action fails:** inspect the browser's displayed error and the server terminal output. Retain the reproduction steps and input values (excluding sensitive data) when reporting the issue.

## Validation and priority rules

Supported categories are `Network`, `Hardware`, `Software`, and `Other`. Category matching is case-insensitive. Supported urgency values are `low`, `medium`, and `high`; urgency is normalized to lowercase. Titles cannot be blank, and affected-user counts must be positive whole numbers.

Priority rules are evaluated in this order:

1. High urgency **and** at least 10 affected users → `critical`
2. Otherwise, high urgency **or** at least 10 affected users → `high`
3. Otherwise, medium urgency **or** at least 3 affected users → `medium`
4. Otherwise → `low`

## Status-transition rules

- New tickets start with status `open`.
- An `open` ticket can move to `in_progress` only after it has an assignee.
- An `in_progress` ticket can move to `resolved`.
- A resolved ticket cannot be modified through normal assignment/status actions.
- Only a resolved ticket can be reopened; reopening sets its status to `open`.
- Unsupported transitions are rejected with a validation message.

## Data storage and safe reset

The default data file is `<project-root>/data/tickets.json`. Its path is anchored to the project root, so the CLI and browser dashboard share the same file even if launched from different working directories. The data directory and file are created when ticket data is first saved. Both interfaces use this same file.

- A missing data file is treated as an empty ticket collection.
- Valid records, including assignment and status, are loaded on startup.
- Malformed JSON or invalid records produce a persistence error rather than silently replacing the existing data.
- Saves use a temporary file and atomic replacement to reduce the risk of partial writes.
- Avoid running multiple CampusFlow writers against the same JSON file simultaneously.

**To reset local ticket data safely:** stop the CLI/dashboard first, make a backup of `data/tickets.json` if you may need the records, and then delete or move that file. The next run starts with an empty collection and creates the file again when a ticket is saved. Do not delete this file if it contains records you need to keep. Automated persistence tests should use temporary directories and must not reset the real data file.

Each ticket record contains `id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, and `assigned_to`. The optional `notes` array stores follow-up notes; older valid records without this field remain supported. Tickets without an assignee are shown as **Unassigned**.

## Run the full test suite

From the repository root:

```bash
python3 -m unittest discover -s tests -v
```

The tests use Python's standard-library `unittest` framework. They cover ticket validation and priority boundaries, status transitions, assignment, CLI behavior, priority ordering, search and combined filters, report calculations, follow-up-note validation and persistence, JSON recovery, and browser/API smoke tests. Run the full suite before submitting changes and check the GitHub Actions result for the specific pull request/commit before merging.

## Team and contributions

The table below reflects the current CampusFlow Next collaboration.

| Role | Fellow | GitHub | Contributions |
| --- | --- | --- | --- |
| Engineer A | Onoja Ojonugba | [@Onoja217](https://github.com/Onoja217) | Repository owner and core application work, including ticket creation and validation, assignment and status workflow, JSON persistence, the browser dashboard, and the shared follow-up-note API in [PR #51](https://github.com/Onoja217/campusflow-next217/pull/51). |
| Engineer B | Okoh Abah | [@Oabah1](https://github.com/Oabah1) | Search and combined filters, report analytics, CLI search menu integration, and related regression tests in [PR #50](https://github.com/Onoja217/campusflow-next217/pull/50). |

### Relevant pull requests

- [PR #51 — Follow-up-note API and persistence](https://github.com/Onoja217/campusflow-next217/pull/51): provides the shared API for validating, storing, and retrieving follow-up notes.
- [PR #50 — Search, filters, and report analytics](https://github.com/Onoja217/campusflow-next217/pull/50): contains Engineer B's search, reporting, and CLI integration work. The pull request remains under review; follow-up-note CLI actions are implemented through menu options 11 and 12 and covered by CLI tests.

## Known limitations and future improvements

- The browser dashboard is a local development interface bound to `127.0.0.1:3000`; it is not a production multi-user service.
- There is no authentication or role-based access control.
- JSON persistence is suitable for this small local project, but concurrent writers can conflict. Avoid simultaneous CLI/dashboard writes; consider a transactional database such as SQLite if the project grows.
- Automated browser/API integration coverage should be expanded, including malformed requests, unknown routes, persistence failures, and concurrent updates.
- The dashboard does not yet present the CLI's full workload report by status and priority.
- Future work could add database-backed storage, authentication, stronger API integration tests, and report views in the dashboard.

## Project structure

```text
campusflow/
  cli.py
  persistence.py
  priority_queue.py
  reports.py
  search.py
  tickets.py
  web.py
tests/
  test_cli.py
  test_cli_persistence_smoke.py
  test_follow_up_notes.py
  test_persistence.py
  test_priority_queue.py
  test_priority_queue_cli.py
  test_reports.py
  test_search.py
  test_ticket_assignment.py
  test_ticket_status.py
  test_ticket_views.py
  test_tickets.py
  test_web.py
```

GitHub Actions runs the automated test suite for supported pull-request and push events. Verify the status of the exact commit under review before merging.
