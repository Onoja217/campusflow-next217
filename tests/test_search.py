"""Tests for case-insensitive ticket search and combined filters."""
import unittest

from campusflow.search import search_tickets
from campusflow.tickets import Ticket, TicketValidationError


def make_ticket(ticket_id, title, category, status, priority):
    return Ticket(
        id=ticket_id,
        title=title,
        category=category,
        urgency="low",
        affected_users=1,
        priority=priority,
        status=status,
        assigned_to=None,
    )


class TicketSearchTests(unittest.TestCase):
    def setUp(self):
        self.tickets = [
            make_ticket("T001", "Wi-Fi not working", "Network", "open", "high"),
            make_ticket("T002", "Office printer jam", "Hardware", "in_progress", "medium"),
            make_ticket("T003", "Wi-Fi slow in lab", "Network", "resolved", "low"),
            make_ticket("T004", "Email app crashing", "Software", "open", "critical"),
        ]

    def test_title_search_is_case_insensitive_substring_match(self):
        results = search_tickets(self.tickets, title="wIfI")
        self.assertEqual([ticket.id for ticket in results], ["T001", "T003"])

    def test_blank_title_and_no_filters_return_all_tickets(self):
        self.assertEqual(search_tickets(self.tickets), self.tickets)
        self.assertEqual(search_tickets(self.tickets, title="   "), self.tickets)

    def test_category_filter_is_case_insensitive(self):
        results = search_tickets(self.tickets, category="network")
        self.assertEqual([ticket.id for ticket in results], ["T001", "T003"])

    def test_status_filter_works_independently(self):
        results = search_tickets(self.tickets, status="IN_PROGRESS")
        self.assertEqual([ticket.id for ticket in results], ["T002"])

    def test_priority_filter_works_independently(self):
        results = search_tickets(self.tickets, priority="CRITICAL")
        self.assertEqual([ticket.id for ticket in results], ["T004"])

    def test_filters_are_combined_with_and(self):
        results = search_tickets(
            self.tickets,
            title="wifi",
            category="NETWORK",
            status="resolved",
            priority="LOW",
        )
        self.assertEqual([ticket.id for ticket in results], ["T003"])

    def test_filters_that_do_not_match_return_empty_list(self):
        self.assertEqual(
            search_tickets(self.tickets, category="Hardware", status="open"),
            [],
        )

    def test_invalid_filter_values_are_rejected(self):
        for kwargs in (
            {"category": "Printer"},
            {"status": "waiting"},
            {"priority": "urgent"},
            {"title": None},
        ):
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(TicketValidationError):
                    search_tickets(self.tickets, **kwargs)

    def test_search_does_not_mutate_original_collection(self):
        before = list(self.tickets)
        search_tickets(self.tickets, title="wifi", status="open")
        self.assertEqual(self.tickets, before)


if __name__ == "__main__":
    unittest.main()
