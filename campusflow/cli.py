"""Interactive CLI entry point for CampusFlow ticket creation and views."""
from __future__ import annotations

from os import PathLike
import sys

from .persistence import (
    DEFAULT_TICKETS_PATH,
    TicketPersistenceError,
    load_tickets,
    save_tickets,
)
from .priority_queue import prioritized_tickets
from .reports import build_ticket_report
from .search import search_tickets
from .tickets import (
    Ticket,
    TicketValidationError,
    assign_ticket,
    change_ticket_status,
    create_ticket,
    format_ticket_details,
    format_ticket_list,
    get_ticket_by_id,
    parse_affected_users_input,
    reopen_ticket,
)


def _save_or_rollback(
    tickets: list[Ticket],
    previous: list[Ticket],
    path: str | PathLike[str],
) -> bool:
    """Persist a mutation or restore the in-memory collection on failure."""
    try:
        save_tickets(tickets, path)
    except TicketPersistenceError as error:
        tickets[:] = previous
        print(f"Persistence error: {error}")
        return False
    return True


def prompt_for_ticket(
    tickets: list[Ticket],
    tickets_path: str | PathLike[str] = DEFAULT_TICKETS_PATH,
) -> Ticket | None:
    """Prompt for a ticket and report success only after it has been saved."""
    previous = list(tickets)

    try:
        title = input("Ticket title: ")
        category = input("Category (Network/Hardware/Software/Other): ")
        urgency = input("Urgency (low/medium/high): ")
        affected_users = parse_affected_users_input(
            input("Affected users (positive whole number): ")
        )
        ticket = create_ticket(
            tickets,
            title=title,
            category=category,
            urgency=urgency,
            affected_users=affected_users,
        )
    except TicketValidationError as error:
        print(f"Error: {error}")
        return None

    if not _save_or_rollback(tickets, previous, tickets_path):
        return None

    print(
        f"Created {ticket.id}: {ticket.title} "
        f"(priority: {ticket.priority}, status: {ticket.status})"
    )
    return ticket


def show_tickets(tickets: list[Ticket]) -> None:
    """Print the concise view of all tickets."""
    print(format_ticket_list(tickets))


def show_priority_queue(tickets: list[Ticket]) -> None:
    """Print unresolved tickets in recommended handling order."""
    queue = prioritized_tickets(tickets)
    if not queue:
        print("No unresolved tickets.")
        return
    print(format_ticket_list(queue))


def show_ticket_report(tickets: list[Ticket]) -> None:
    """Print workload totals by category, status, priority, and resolution."""
    report = build_ticket_report(tickets)
    print(f"Total tickets: {report['total']}")
    print(f"Resolution percentage: {report['resolution_percentage']:.1f}%")

    print("\nBy category:")
    for category, count in report["by_category"].items():
        print(f"  {category}: {count}")

    print("\nBy status:")
    for status, count in report["by_status"].items():
        print(f"  {status}: {count}")

    print("\nBy priority:")
    for priority, count in report["by_priority"].items():
        print(f"  {priority}: {count}")


def show_ticket_search(tickets: list[Ticket]) -> None:
    """Prompt for optional search terms and filters, then print matches."""
    try:
        title = input("Title contains (leave blank for any): ")
        category = input(
            "Category (Network/Hardware/Software/Other, blank for any): "
        )
        status = input(
            "Status (open/in_progress/resolved, blank for any): "
        )
        priority = input(
            "Priority (low/medium/high/critical, blank for any): "
        )
        matches = search_tickets(
            tickets,
            title=title,
            category=category,
            status=status,
            priority=priority,
        )
    except TicketValidationError as error:
        print(f"Error: {error}")
        return

    if not matches:
        print("No matching tickets found.")
        return

    print(format_ticket_list(matches))


def show_ticket_by_id(tickets: list[Ticket], ticket_id: str) -> None:
    """Print ticket details or a friendly not-found message."""
    if not tickets:
        print("No tickets found.")
        return

    ticket = get_ticket_by_id(tickets, ticket_id)
    if ticket is None:
        requested = ticket_id.strip() if isinstance(ticket_id, str) else ""
        if requested:
            print(f"No ticket found with ID {requested}.")
        else:
            print("Please enter a ticket ID.")
        return

    print(format_ticket_details(ticket))


def _pause_if_interactive() -> None:
    """Pause after a result only when running in an interactive terminal."""
    if sys.stdin.isatty():
        input("Press Enter to return to the menu...")


def main(tickets_path: str | PathLike[str] = DEFAULT_TICKETS_PATH) -> None:
    """Load persisted tickets and run the interactive menu."""
    try:
        tickets = load_tickets(tickets_path)
    except TicketPersistenceError as error:
        print(f"Persistence error: {error}")
        print("CampusFlow stopped to protect the existing ticket data.")
        return

    print("CampusFlow ticket tracker")

    try:
        while True:
            print(
                "\n1. Create ticket\n"
                "2. List all tickets\n"
                "3. View ticket by ID\n"
                "4. Assign ticket\n"
                "5. Change ticket status\n"
                "6. Reopen resolved ticket\n"
                "7. Exit\n"
                "8. Show unresolved priority queue\n"
                "9. Show ticket report\n"
                "10. Search and filter tickets"
            )

            choice = input("Choose an option: ").strip()

            if choice == "1":
                prompt_for_ticket(tickets, tickets_path)

            elif choice == "2":
                show_tickets(tickets)
                _pause_if_interactive()

            elif choice == "3":
                show_ticket_by_id(tickets, input("Ticket ID: "))

            elif choice == "4":
                previous = list(tickets)
                try:
                    ticket_id = input("Ticket ID to assign: ")
                    assignee = input("Assignee name: ")
                    ticket = assign_ticket(tickets, ticket_id, assignee)
                    if _save_or_rollback(tickets, previous, tickets_path):
                        print(f"Assigned {ticket.id} to {ticket.assigned_to}.")
                except TicketValidationError as error:
                    print(f"Error: {error}")

            elif choice == "5":
                previous = list(tickets)
                try:
                    ticket_id = input("Ticket ID: ")
                    new_status = input("New status (in_progress/resolved): ")
                    ticket = change_ticket_status(tickets, ticket_id, new_status)
                    if _save_or_rollback(tickets, previous, tickets_path):
                        print(f"{ticket.id} status changed to {ticket.status}.")
                except TicketValidationError as error:
                    print(f"Error: {error}")

            elif choice == "6":
                previous = list(tickets)
                try:
                    ticket_id = input("Ticket ID to reopen: ")
                    ticket = reopen_ticket(tickets, ticket_id)
                    if _save_or_rollback(tickets, previous, tickets_path):
                        print(f"{ticket.id} reopened and set to open.")
                except TicketValidationError as error:
                    print(f"Error: {error}")

            elif choice == "7":
                print("CampusFlow closed.")
                return

            elif choice == "8":
                show_priority_queue(tickets)
                _pause_if_interactive()

            elif choice == "9":
                show_ticket_report(tickets)
                _pause_if_interactive()

            elif choice == "10":
                show_ticket_search(tickets)
                _pause_if_interactive()

            else:
                print(
                    "Invalid option. Choose 1, 2, 3, 4, 5, 6, 7, 8, 9, or 10."
                )

    except (EOFError, KeyboardInterrupt):
        print("\nCampusFlow closed.")


if __name__ == "__main__":
    main()
