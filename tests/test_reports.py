"""Tests for ticket reports, including empty and mixed workloads."""
from contextlib import redirect_stdout
from io import StringIO
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from campusflow.cli import main, show_ticket_report
from campusflow.reports import build_ticket_report
from campusflow.tickets import CATEGORIES, PRIORITIES, TICKET_STATUSES, Ticket


def make_ticket(ticket_id, priority, status, category="Network"):
    return Ticket(
        id=ticket_id,
        title=f"Ticket {ticket_id}",
        category=category,
        urgency="low",
        affected_users=1,
        priority=priority,
        status=status,
        assigned_to=None,
    )


class TicketReportTests(unittest.TestCase):
    def test_empty_data_returns_zero_for_every_group_and_zero_resolution(self):
        report = build_ticket_report([])

        self.assertEqual(report["total"], 0)
        self.assertEqual(report["by_category"], dict.fromkeys(CATEGORIES, 0))
        self.assertEqual(report["by_status"], dict.fromkeys(TICKET_STATUSES, 0))
        self.assertEqual(report["by_priority"], dict.fromkeys(PRIORITIES, 0))
        self.assertEqual(report["resolution_percentage"], 0.0)

    def test_mixed_tickets_have_correct_totals_and_breakdowns(self):
        tickets = [
            make_ticket("T001", "critical", "open", "Network"),
            make_ticket("T002", "high", "in_progress", "Hardware"),
            make_ticket("T003", "high", "open", "Network"),
            make_ticket("T004", "low", "resolved", "Software"),
            make_ticket("T005", "medium", "resolved", "Other"),
        ]

        report = build_ticket_report(tickets)

        self.assertEqual(report["total"], len(tickets))
        self.assertEqual(
            report["by_category"],
            {"Network": 2, "Hardware": 1, "Software": 1, "Other": 1},
        )
        self.assertEqual(
            report["by_status"],
            {"open": 2, "in_progress": 1, "resolved": 2},
        )
        self.assertEqual(
            report["by_priority"],
            {"low": 1, "medium": 1, "high": 2, "critical": 1},
        )
        self.assertEqual(report["resolution_percentage"], 40.0)

    def test_counts_include_zero_categories_in_mixed_data(self):
        report = build_ticket_report([make_ticket("T001", "low", "open")])

        self.assertEqual(report["by_category"]["Hardware"], 0)
        self.assertEqual(report["by_category"]["Software"], 0)
        self.assertEqual(report["by_category"]["Other"], 0)
        self.assertEqual(report["by_status"]["in_progress"], 0)
        self.assertEqual(report["by_status"]["resolved"], 0)
        self.assertEqual(report["by_priority"]["critical"], 0)
        self.assertEqual(report["by_priority"]["high"], 0)
        self.assertEqual(report["by_priority"]["medium"], 0)
        self.assertEqual(report["resolution_percentage"], 0.0)

    def test_cli_displays_zero_ticket_report_without_crashing(self):
        output = StringIO()
        with redirect_stdout(output):
            show_ticket_report([])

        rendered = output.getvalue()
        self.assertIn("Total tickets: 0", rendered)
        self.assertIn("Resolution percentage: 0.0%", rendered)
        for category in CATEGORIES:
            self.assertIn(f"{category}: 0", rendered)
        for status in TICKET_STATUSES:
            self.assertIn(f"{status}: 0", rendered)
        for priority in PRIORITIES:
            self.assertIn(f"{priority}: 0", rendered)

    def test_menu_can_display_report_for_empty_store(self):
        output = StringIO()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "tickets.json"
            with patch("campusflow.cli.sys.stdin") as stdin:
                stdin.isatty.return_value = False
                with patch("builtins.input", side_effect=["9", "7"]):
                    with redirect_stdout(output):
                        main(path)

        rendered = output.getvalue()
        self.assertIn("9. Show ticket report", rendered)
        self.assertIn("Total tickets: 0", rendered)
        self.assertIn("CampusFlow closed.", rendered)


if __name__ == "__main__":
    unittest.main()
