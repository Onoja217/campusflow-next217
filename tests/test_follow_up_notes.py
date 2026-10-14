"""Regression tests for ticket follow-up notes and safe persistence."""
import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from campusflow.persistence import TicketPersistenceError, load_tickets, save_tickets
from campusflow.tickets import (
    FollowUpNote,
    TicketValidationError,
    add_follow_up_note,
    change_ticket_status,
    create_ticket,
    get_follow_up_notes,
    next_follow_up_note_id,
    reopen_ticket,
)


class FollowUpNoteTests(unittest.TestCase):
    def setUp(self):
        self.tickets = []
        self.ticket = create_ticket(
            self.tickets, title="Wi-Fi unavailable", category="Network",
            urgency="medium", affected_users=3,
        )

    def test_add_note_trims_content_and_allocates_sequential_ids(self):
        first = add_follow_up_note(self.tickets, self.ticket.id, "  Called the ISP. ")
        second = add_follow_up_note(self.tickets, self.ticket.id, "Router rebooted.")
        self.assertEqual((first.id, first.content), ("N001", "Called the ISP."))
        self.assertEqual(second.id, "N002")

    def test_blank_note_is_rejected_without_mutation_or_consuming_id(self):
        before = list(self.tickets)
        with self.assertRaises(TicketValidationError):
            add_follow_up_note(self.tickets, self.ticket.id, "   ")
        self.assertEqual(self.tickets, before)
        self.assertEqual(next_follow_up_note_id(self.tickets), "N001")

    def test_missing_ticket_rejects_note_without_mutation(self):
        before = list(self.tickets)
        with self.assertRaises(TicketValidationError):
            add_follow_up_note(self.tickets, "T999", "Follow up")
        self.assertEqual(self.tickets, before)
        self.assertEqual(next_follow_up_note_id(self.tickets), "N001")

    def test_resolved_ticket_rejects_notes_without_mutation(self):
        self.tickets[0] = replace(self.ticket, status="in_progress", assigned_to="Jireh")
        change_ticket_status(self.tickets, self.ticket.id, "resolved")
        before = list(self.tickets)
        with self.assertRaisesRegex(TicketValidationError, "open or in-progress"):
            add_follow_up_note(self.tickets, self.ticket.id, "Too late")
        self.assertEqual(self.tickets, before)
        self.assertEqual(next_follow_up_note_id(self.tickets), "N001")

    def test_notes_survive_resolve_and_reopen(self):
        note = add_follow_up_note(self.tickets, self.ticket.id, "Initial investigation")
        self.tickets[0] = replace(self.tickets[0], assigned_to="Jireh")
        change_ticket_status(self.tickets, self.ticket.id, "in_progress")
        change_ticket_status(self.tickets, self.ticket.id, "resolved")
        reopen_ticket(self.tickets, self.ticket.id)
        self.assertEqual(get_follow_up_notes(self.tickets, self.ticket.id), (note,))
        next_note = add_follow_up_note(self.tickets, self.ticket.id, "Retest after reopening")
        self.assertEqual(next_note.id, "N002")

    def test_notes_persist_and_note_ids_continue_after_reload(self):
        add_follow_up_note(self.tickets, self.ticket.id, "First note")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            save_tickets(self.tickets, path)
            restored = load_tickets(path)
            self.assertEqual(get_follow_up_notes(restored, self.ticket.id)[0].id, "N001")
            second = add_follow_up_note(restored, self.ticket.id, "Second note")
            self.assertEqual(second.id, "N002")
            save_tickets(restored, path)
            reloaded = load_tickets(path)
            self.assertEqual([n.id for n in get_follow_up_notes(reloaded, self.ticket.id)], ["N001", "N002"])

    def test_legacy_ticket_document_without_notes_remains_compatible(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            record = self.ticket.to_dict()
            record.pop("notes", None)
            path.write_text(json.dumps([record]), encoding="utf-8")
            loaded = load_tickets(path)
            self.assertEqual(get_follow_up_notes(loaded, self.ticket.id), ())

    def test_invalid_note_record_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            record = self.ticket.to_dict()
            record["notes"] = [{"id": "not-an-id", "content": "Broken"}]
            path.write_text(json.dumps([record]), encoding="utf-8")
            with self.assertRaises(TicketPersistenceError):
                load_tickets(path)

    def test_duplicate_note_ids_across_tickets_are_rejected(self):
        second = create_ticket(
            self.tickets, title="Printer down", category="Hardware",
            urgency="low", affected_users=1,
        )
        first_record = replace(self.tickets[0], notes=(
            FollowUpNote("N001", "Note one"),
        )).to_dict()
        second_record = replace(second, notes=(
            FollowUpNote("N001", "Duplicate"),
        )).to_dict()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text(json.dumps([first_record, second_record]), encoding="utf-8")
            with self.assertRaisesRegex(TicketPersistenceError, "duplicate note ID"):
                load_tickets(path)

    def test_failed_load_does_not_replace_callers_current_collection(self):
        before = list(self.tickets)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            path.write_text("{bad json", encoding="utf-8")
            with self.assertRaises(TicketPersistenceError):
                self.tickets[:] = load_tickets(path)
        self.assertEqual(self.tickets, before)

    def test_rejected_note_does_not_change_other_tickets(self):
        second = create_ticket(
            self.tickets, title="Printer down", category="Hardware",
            urgency="low", affected_users=1,
        )
        before = list(self.tickets)
        with self.assertRaises(TicketValidationError):
            add_follow_up_note(self.tickets, second.id, None)
        self.assertEqual(self.tickets, before)



    def test_get_notes_rejects_non_collection_values(self):
        for malformed in ("", {}, None):
            with self.subTest(malformed=malformed):
                tickets = [dict(self.ticket.to_dict(), notes=malformed)]
                with self.assertRaises(TicketValidationError):
                    get_follow_up_notes(tickets, self.ticket.id)

    def test_add_note_rejects_malformed_existing_notes_without_mutation_or_id(self):
        malformed_cases = (
            {"notes": [{"id": "N001", "content": ""}]},
            {"notes": [{"id": "bad-id", "content": "Existing"}]},
            {"notes": ["not-a-note"]},
            {"notes": ""},
        )
        for extra in malformed_cases:
            with self.subTest(extra=extra):
                ticket_record = self.ticket.to_dict()
                ticket_record.update(extra)
                tickets = [ticket_record]
                before = [dict(ticket_record)]
                next_id_before = next_follow_up_note_id(tickets)
                with self.assertRaises(TicketValidationError):
                    add_follow_up_note(tickets, self.ticket.id, "New note")
                self.assertEqual(tickets, before)
                self.assertEqual(next_follow_up_note_id(tickets), next_id_before)

if __name__ == "__main__":
    unittest.main()
