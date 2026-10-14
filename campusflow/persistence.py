"""JSON file persistence for CampusFlow tickets.

File I/O is isolated from ticket business rules. Saves use a same-directory
temporary file and atomic replacement so a failed write leaves the old file
untouched.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import re
import tempfile
from typing import Iterable

from .tickets import (
    CATEGORIES,
    PRIORITIES,
    TICKET_STATUSES,
    URGENCY_LEVELS,
    FollowUpNote,
    Ticket,
    TicketValidationError,
    calculate_priority,
)

# Anchor default storage to the project root, not the caller's working
# directory. This keeps the CLI and browser dashboard pointed at the same
# tickets.json file even when launched from different directories.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_TICKETS_PATH = PROJECT_ROOT / "data" / "tickets.json"
_REQUIRED_FIELDS = {
    "id",
    "title",
    "category",
    "urgency",
    "affected_users",
    "priority",
    "status",
    "assigned_to",
}
_NOTE_FIELDS = {"id", "content"}
_TICKET_ID = re.compile(r"^T[0-9]+$")


class TicketPersistenceError(RuntimeError):
    """Raised when ticket data cannot safely be loaded or saved."""


def _validate_record(value: object, index: int) -> Ticket:
    """Validate one decoded record without silently repairing stored data."""
    prefix = f"Ticket record {index}"
    if not isinstance(value, dict):
        raise TicketPersistenceError(f"{prefix} must be a JSON object.")

    keys = set(value)
    allowed_shapes = (_REQUIRED_FIELDS, _REQUIRED_FIELDS | {"notes"})
    if keys not in allowed_shapes:
        missing = sorted(_REQUIRED_FIELDS - keys)
        extra = sorted(keys - (_REQUIRED_FIELDS | {"notes"}))
        details = []
        if missing:
            details.append(f"missing fields: {', '.join(missing)}")
        if extra:
            details.append(f"unknown fields: {', '.join(extra)}")
        raise TicketPersistenceError(f"{prefix} has an invalid shape ({'; '.join(details)}).")

    if not isinstance(value["id"], str) or not _TICKET_ID.fullmatch(value["id"]):
        raise TicketPersistenceError(f"{prefix} has an invalid ticket ID.")
    if not isinstance(value["title"], str) or not value["title"].strip():
        raise TicketPersistenceError(f"{prefix} has an invalid title.")
    if value["category"] not in CATEGORIES or not isinstance(value["category"], str):
        raise TicketPersistenceError(f"{prefix} has an unsupported category.")
    if value["urgency"] not in URGENCY_LEVELS or not isinstance(value["urgency"], str):
        raise TicketPersistenceError(f"{prefix} has an unsupported urgency.")
    if type(value["affected_users"]) is not int or value["affected_users"] <= 0:
        raise TicketPersistenceError(f"{prefix} has an invalid affected_users value.")
    if value["priority"] not in PRIORITIES or not isinstance(value["priority"], str):
        raise TicketPersistenceError(f"{prefix} has an unsupported priority.")
    if value["status"] not in TICKET_STATUSES or not isinstance(value["status"], str):
        raise TicketPersistenceError(f"{prefix} has an unsupported status.")

    try:
        expected_priority = calculate_priority(value["urgency"], value["affected_users"])
    except TicketValidationError as error:
        raise TicketPersistenceError(f"{prefix} has invalid priority inputs.") from error
    if value["priority"] != expected_priority:
        raise TicketPersistenceError(
            f"{prefix} has inconsistent priority: expected {expected_priority!r} "
            f"for its urgency and affected_users."
        )

    assignee = value["assigned_to"]
    if assignee is not None and (
        not isinstance(assignee, str) or not assignee.strip()
    ):
        raise TicketPersistenceError(f"{prefix} has an invalid assigned_to value.")
    if value["status"] == "in_progress" and (
        not isinstance(assignee, str) or not assignee.strip()
    ):
        raise TicketPersistenceError(
            f"{prefix} cannot be in_progress without an assigned_to value."
        )

    raw_notes = value.get("notes", [])
    if not isinstance(raw_notes, (list, tuple)):
        raise TicketPersistenceError(f"{prefix} has invalid notes; expected an array.")
    notes: list[FollowUpNote] = []
    seen_note_ids: set[str] = set()
    for note_index, note in enumerate(raw_notes, start=1):
        note_prefix = f"{prefix}, note {note_index}"
        if not isinstance(note, dict) and not hasattr(note, "keys"):
            raise TicketPersistenceError(f"{note_prefix} must be a JSON object.")
        if set(note.keys()) != _NOTE_FIELDS:
            raise TicketPersistenceError(f"{note_prefix} has an invalid shape.")
        note_id = note.get("id")
        content = note.get("content")
        if not isinstance(note_id, str) or not re.fullmatch(r"^N[0-9]+$", note_id):
            raise TicketPersistenceError(f"{note_prefix} has an invalid note ID.")
        if note_id in seen_note_ids:
            raise TicketPersistenceError(f"{note_prefix} has a duplicate note ID {note_id!r}.")
        if not isinstance(content, str) or not content.strip():
            raise TicketPersistenceError(f"{note_prefix} has invalid content.")
        seen_note_ids.add(note_id)
        notes.append(FollowUpNote(note_id, content.strip()))

    return Ticket(
        id=value["id"], title=value["title"], category=value["category"],
        urgency=value["urgency"], affected_users=value["affected_users"],
        priority=value["priority"], status=value["status"],
        assigned_to=value["assigned_to"], notes=tuple(notes),
    )


def load_tickets(path: str | os.PathLike[str] = DEFAULT_TICKETS_PATH) -> list[Ticket]:
    """Load and validate tickets; a missing file is a new empty workspace."""
    source = Path(path)
    try:
        raw = source.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    except OSError as error:
        raise TicketPersistenceError(f"Cannot read ticket file '{source}': {error}") from error

    try:
        payload = json.loads(raw)
    except (json.JSONDecodeError, UnicodeDecodeError) as error:
        raise TicketPersistenceError(
            f"Ticket file '{source}' contains invalid JSON; it was not changed."
        ) from error

    if not isinstance(payload, list):
        raise TicketPersistenceError(
            f"Ticket file '{source}' must contain a JSON array of ticket records."
        )

    tickets: list[Ticket] = []
    seen_ids: set[str] = set()
    seen_note_ids: set[str] = set()
    for index, record in enumerate(payload, start=1):
        ticket = _validate_record(record, index)
        if ticket.id in seen_ids:
            raise TicketPersistenceError(
                f"Ticket file '{source}' contains duplicate ID {ticket.id!r}."
            )
        seen_ids.add(ticket.id)
        for note in ticket.notes:
            if note.id in seen_note_ids:
                raise TicketPersistenceError(
                    f"Ticket file '{source}' contains duplicate note ID {note.id!r}."
                )
            seen_note_ids.add(note.id)
        tickets.append(ticket)
    return tickets


def save_tickets(
    tickets: Iterable[Ticket],
    path: str | os.PathLike[str] = DEFAULT_TICKETS_PATH,
) -> None:
    """Atomically save validated ticket records as UTF-8 JSON."""
    destination = Path(path)
    records = []
    seen_ids: set[str] = set()
    seen_note_ids: set[str] = set()
    for index, ticket in enumerate(tickets, start=1):
        record = _validate_record(ticket.to_dict() if isinstance(ticket, Ticket) else ticket, index)
        if record.id in seen_ids:
            raise TicketPersistenceError(f"Cannot save duplicate ticket ID {record.id!r}.")
        seen_ids.add(record.id)
        for note in record.notes:
            if note.id in seen_note_ids:
                raise TicketPersistenceError(f"Cannot save duplicate note ID {note.id!r}.")
            seen_note_ids.add(note.id)
        records.append(record.to_dict())

    temporary_path: str | None = None
    try:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            newline="\n",
            dir=destination.parent,
            prefix=f".{destination.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary:
            temporary_path = temporary.name
            json.dump(records, temporary, ensure_ascii=False, indent=2)
            temporary.write("\n")
            temporary.flush()
            os.fsync(temporary.fileno())
        os.replace(temporary_path, destination)
        temporary_path = None
    except (OSError, TypeError, ValueError) as error:
        raise TicketPersistenceError(
            f"Cannot safely save tickets to '{destination}': {error}"
        ) from error
    finally:
        if temporary_path is not None:
            try:
                os.unlink(temporary_path)
            except FileNotFoundError:
                pass
            except OSError:
                pass
