# CampusFlow

CampusFlow is a Python helpdesk ticket tracker with an interactive command-line interface (CLI) and a local browser dashboard. It supports validated ticket creation, automatic priority calculation, assignment, status changes, search and combined filters, workload reports, an unresolved-ticket priority queue, follow-up notes, and JSON persistence.

## Current development and audit status (15 October 2026)

- **Issue #47 — follow-up notes and persistence safeguards:** merged through [PR #51](https://github.com/Onoja217/campusflow-next217/pull/51).
- **Issue #48 — search, filters, reports, and CLI note integration:** implemented on [PR #50](https://github.com/Onoja217/campusflow-next217/pull/50). Its latest recorded PR-head CI run [#154](https://github.com/Onoja217/campusflow-next217/actions/runs/38744979052) passed **117 tests** on commit [`267a143a9787a7892d5c156c7f868fe35b8802a3`](https://github.com/Onoja217/campusflow-next217/commit/267a143a9787a7892d5c156c7f868fe35b8802a3). The PR description records a local run of 117 passing tests and a clean `git diff --check`; these are branch-specific results, not evidence that this work has merged to `main`.
- **Review/merge status:** treat PR #50 as in progress until its current GitHub state confirms approval and merge. Do not describe Issue #48 as merged based only on green CI.
- **Audit evidence:** see [`docs/baseline-check.md`](docs/baseline-check.md) for historical baseline and CI records, and [`docs/audit-evidence.md`](docs/audit-evidence.md) for the evidence boundaries and remaining audit actions.
- **Manual demonstration:** the project owner has reported interactive CLI checks using sample tickets T001–T005, assignment, invalid-input handling, and the menu-output pause behavior. The evidence should be considered owner-reported unless accompanied by a dated transcript, screenshot, or reviewer observation in the repository.

## Features

- Create tickets with validation for title, category, urgency, and positive affected-user count.
- Calculate priority using the rules below and generate sequential IDs such as `T001`.
- List tickets and look up a ticket by ID.
- Assign tickets and enforce the `open → in_progress → resolved` workflow, with explicit reopening.
- Show an unresolved priority queue; resolved tickets are excluded.
- Search titles case-insensitively and combine category, status, and priority filters.
- Report totals and grouped counts by category, status, and priority, including safe resolution percentages.
- Add and view follow-up notes through the shared note API and CLI menu options 11 and 12; notes persist and remain attached through resolve/reopen.
- Persist tickets to JSON and share the same project-root data file between the CLI and browser dashboard.

## Requirements and setup

- Python 3.10 or newer
- No third-party runtime dependencies

```bash
git clone https://github.com/Onoja217/campusflow-next217.git
cd campusflow-next217
python3 --version
python3 -m unittest discover -s tests -v
```

On Windows, use `python` in place of `python3` if that is the configured command.

## Run the CLI

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
| 11 | Add a follow-up note |
| 12 | View follow-up notes |

## Run the browser dashboard

```bash
python3 -m campusflow.web
```

Open [http://localhost:3000](http://localhost:3000) and keep the terminal running. Stop the server with `Ctrl+C`. The dashboard is a local development interface, not a production multi-user service.

## Validation and priority rules

Categories are `Network`, `Hardware`, `Software`, and `Other`. Urgency values are `low`, `medium`, and `high`. Titles must not be blank and affected-user counts must be positive whole numbers.

1. High urgency **and** at least 10 affected users → `critical`
2. Otherwise, high urgency **or** at least 10 affected users → `high`
3. Otherwise, medium urgency **or** at least 3 affected users → `medium`
4. Otherwise → `low`

## Status and follow-up-note rules

- New tickets start as `open`.
- An `open` ticket needs an assignee before it can move to `in_progress`.
- An `in_progress` ticket can move to `resolved`; only resolved tickets can be reopened.
- New notes are accepted only for open or in-progress tickets. Existing notes remain attached after resolving and reopening.
- Rejected operations should not mutate ticket data or consume a note ID.

## Data storage and safety

The default data file is `<project-root>/data/tickets.json`. Missing data files load as an empty collection; malformed JSON and invalid records should produce an error rather than silently overwrite data. Saves use a temporary file and atomic replacement. Avoid simultaneous CLI/dashboard writers against the same JSON file.

A ticket record contains `id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, and `assigned_to`; the optional `notes` array supports legacy records without notes. Back up local data before manual repair or reset.

## Team

| Role | Fellow | Contributions |
| --- | --- | --- |
| Engineer A | Onoja Ojonugba ([`@Onoja217`](https://github.com/Onoja217)) | Repository owner; ticket validation and lifecycle, persistence, browser dashboard, shared follow-up-note API, and audit documentation. |
| Engineer B | Okoh Abah ([`@Oabah1`](https://github.com/Oabah1)) | Search, combined filters, report analytics, CLI integration, and related regression tests on PR #50. |

## Known limitations

- The browser dashboard is intended for local development and has no authentication or role-based access control.
- JSON storage is suitable for a small local project; simultaneous writers can conflict.
- Automated tests are strong evidence for tested behavior, but do not replace a recorded practical demonstration, genuine learning reflections, or independent reviewer/mentor feedback.
