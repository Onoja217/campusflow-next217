"""Search and filter helpers for CampusFlow tickets."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import TypeAlias

from .tickets import (
    CATEGORIES,
    PRIORITIES,
    TICKET_STATUSES,
    Ticket,
    TicketValidationError,
    normalize_category,
)

TicketLike: TypeAlias = Ticket | Mapping[str, object]


def _value(ticket: TicketLike, field: str) -> object:
    """Read a field from either a Ticket or a mapping-shaped record."""
    if isinstance(ticket, Ticket):
        return getattr(ticket, field)
    return ticket.get(field)


def search_tickets(
    tickets: Iterable[TicketLike],
    *,
    title: object = "",
    category: object = None,
    status: object = None,
    priority: object = None,
) -> list[TicketLike]:
    """Search by title substring and combine optional filters with AND.

    Title matching is case-insensitive. A blank title query and omitted filters
    do not restrict results. The source collection is never changed.
    """
    if not isinstance(title, str):
        raise TicketValidationError("Title search must be text.")
    title_query = title.strip().casefold()

    clean_category = None
    if category is not None and str(category).strip():
        clean_category = normalize_category(category)

    clean_status = None
    if status is not None and str(status).strip():
        if not isinstance(status, str):
            raise TicketValidationError(
                f"Status must be one of: {', '.join(TICKET_STATUSES)}."
            )
        clean_status = status.strip().casefold()
        if clean_status not in TICKET_STATUSES:
            raise TicketValidationError(
                f"Unsupported status {status!r}. Choose one of: {', '.join(TICKET_STATUSES)}."
            )

    clean_priority = None
    if priority is not None and str(priority).strip():
        if not isinstance(priority, str):
            raise TicketValidationError(
                f"Priority must be one of: {', '.join(PRIORITIES)}."
            )
        clean_priority = priority.strip().casefold()
        if clean_priority not in PRIORITIES:
            raise TicketValidationError(
                f"Unsupported priority {priority!r}. Choose one of: {', '.join(PRIORITIES)}."
            )

    results = []
    for ticket in tickets:
        ticket_title = _value(ticket, "title")
        if title_query and (
            not isinstance(ticket_title, str)
            or title_query not in ticket_title.casefold()
        ):
            continue
        if clean_category is not None and _value(ticket, "category") != clean_category:
            continue
        if clean_status is not None and _value(ticket, "status") != clean_status:
            continue
        if clean_priority is not None and _value(ticket, "priority") != clean_priority:
            continue
        results.append(ticket)
    return results
