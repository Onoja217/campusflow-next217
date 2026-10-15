"""Workload reporting helpers for CampusFlow tickets."""
from __future__ import annotations

from collections.abc import Iterable

from .tickets import CATEGORIES, PRIORITIES, TICKET_STATUSES, Ticket


def build_ticket_report(tickets: Iterable[Ticket]) -> dict[str, object]:
    """Summarize ticket totals by category, status, and priority.

    Every supported category is included, even when its count is zero.
    Resolution percentage is resolved tickets divided by total tickets. Empty
    workloads report 0.0 percent. The supplied iterable is read once and is
    never modified.
    """
    category_counts = dict.fromkeys(CATEGORIES, 0)
    status_counts = dict.fromkeys(TICKET_STATUSES, 0)
    priority_counts = dict.fromkeys(PRIORITIES, 0)
    total = 0

    for ticket in tickets:
        total += 1
        category_counts[ticket.category] += 1
        status_counts[ticket.status] += 1
        priority_counts[ticket.priority] += 1

    resolved_percentage = (
        (status_counts["resolved"] / total) * 100 if total else 0.0
    )
    return {
        "total": total,
        "by_category": category_counts,
        "by_status": status_counts,
        "by_priority": priority_counts,
        "resolution_percentage": resolved_percentage,
    }
