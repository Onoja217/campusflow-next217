"""Regression tests for browser ticket creation and dashboard workflows."""
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from campusflow.web import CampusFlowHandler, PAGE


class BrowserTicketCreationTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        tickets_path = Path(self.temp_dir.name) / "tickets.json"

        class TestHandler(CampusFlowHandler):
            pass

        TestHandler.tickets_path = tickets_path
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.temp_dir.cleanup()

    def request_json(self, path, payload=None, method=None):
        data = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url}{path}",
            data=data,
            headers={"Content-Type": "application/json"},
            method=method or ("POST" if data is not None else "GET"),
        )
        try:
            with urlopen(request) as response:
                body = response.read().decode("utf-8")
                return response.status, json.loads(body) if body else None
        except HTTPError as error:
            body = error.read().decode("utf-8")
            return error.code, json.loads(body) if body else None

    def post_ticket(self, category):
        payload = {
            "title": f"{category} test ticket",
            "category": category,
            "urgency": "medium",
            "affected_users": 1,
        }
        return self.request_json("/api/tickets", payload)

    def test_dashboard_page_loads_with_ticket_controls(self):
        with urlopen(self.base_url + "/") as response:
            page = response.read().decode("utf-8")
            self.assertEqual(response.status, 200)
            self.assertIn("text/html", response.headers["Content-Type"])
        self.assertIn("<title>CampusFlow · Helpdesk</title>", page)
        self.assertIn('id="create-form"', page)
        self.assertIn('id="ticket-rows"', page)
        self.assertIn('id="queue-list"', page)

    def test_hardware_ticket_is_created_and_persisted(self):
        status, result = self.post_ticket("Hardware")
        self.assertEqual(status, 201)
        self.assertEqual(result["ticket"]["category"], "Hardware")
        self.assertEqual(result["ticket"]["title"], "Hardware test ticket")
        self.assertEqual(len(result["tickets"]), 1)

    def test_software_ticket_is_created_and_persisted(self):
        status, result = self.post_ticket("Software")
        self.assertEqual(status, 201)
        self.assertEqual(result["ticket"]["category"], "Software")
        self.assertEqual(result["ticket"]["title"], "Software test ticket")
        self.assertEqual(len(result["tickets"]), 1)

    def test_concurrent_creates_receive_distinct_ticket_ids(self):
        from concurrent.futures import ThreadPoolExecutor

        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(self.post_ticket, ["Hardware", "Software"]))

        self.assertEqual([status for status, _ in results], [201, 201])
        ids = [result["ticket"]["id"] for _, result in results]
        self.assertEqual(set(ids), {"T001", "T002"})
        with urlopen(f"{self.base_url}/api/tickets") as response:
            stored = json.loads(response.read().decode("utf-8"))["tickets"]
        self.assertEqual(len(stored), 2)
        self.assertEqual({ticket["id"] for ticket in stored}, {"T001", "T002"})

    def test_blank_title_is_rejected_without_saving_a_ticket(self):
        status, result = self.request_json(
            "/api/tickets",
            {
                "title": "   ",
                "category": "Network",
                "urgency": "low",
                "affected_users": 1,
            },
        )
        self.assertEqual(status, 400)
        self.assertIn("Title cannot be blank", result["error"])
        list_status, stored = self.request_json("/api/tickets")
        self.assertEqual(list_status, 200)
        self.assertEqual(stored["tickets"], [])

    def test_assign_status_resolve_and_reopen_workflow(self):
        status, created = self.post_ticket("Network")
        self.assertEqual(status, 201)
        ticket_id = created["ticket"]["id"]

        status, rejected = self.request_json(
            f"/api/tickets/{ticket_id}/status", {"status": "in_progress"}
        )
        self.assertEqual(status, 400)
        self.assertIn("unassigned ticket", rejected["error"].lower())

        status, assigned = self.request_json(
            f"/api/tickets/{ticket_id}/assign", {"assignee": "Helpdesk Team"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(assigned["ticket"]["assigned_to"], "Helpdesk Team")

        status, started = self.request_json(
            f"/api/tickets/{ticket_id}/status", {"status": "in_progress"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(started["ticket"]["status"], "in_progress")

        status, resolved = self.request_json(
            f"/api/tickets/{ticket_id}/status", {"status": "resolved"}
        )
        self.assertEqual(status, 200)
        self.assertEqual(resolved["ticket"]["status"], "resolved")

        status, reopened = self.request_json(
            f"/api/tickets/{ticket_id}/reopen", {}
        )
        self.assertEqual(status, 200)
        self.assertEqual(reopened["ticket"]["status"], "open")
        self.assertEqual(reopened["ticket"]["assigned_to"], "Helpdesk Team")

        status, persisted = self.request_json("/api/tickets")
        self.assertEqual(status, 200)
        self.assertEqual(persisted["tickets"][0]["status"], "open")
        self.assertEqual(persisted["tickets"][0]["assigned_to"], "Helpdesk Team")

    def test_unknown_api_route_returns_not_found(self):
        status, result = self.request_json("/api/unknown")
        self.assertEqual(status, 404)
        self.assertEqual(result["error"], "Not found.")

    def test_all_tickets_table_has_explicit_category_column(self):
        self.assertIn("<th>Category</th>", PAGE)
        self.assertIn("placeholder=\"Search title, ID, category, or assignee…\"", PAGE)
        self.assertIn("</td><td>'+esc(t.category)+'</td><td>'+pill(t.priority)", PAGE)

    def test_queue_preview_explains_limit_and_shows_category(self):
        self.assertIn("top '+Math.min(5,queue.length)+' shown", PAGE)
        self.assertIn("esc(t.id)+' · '+esc(t.category)+' · '+esc(t.priority)", PAGE)

    def test_ticket_form_does_not_call_reset_method(self):
        # Avoid the browser's form-reset call entirely; clear fields explicitly
        # only after the API confirms the ticket was created successfully.
        self.assertNotIn(".reset()", PAGE)
        self.assertIn("document.querySelector('#ticket-title').value=''", PAGE)
        self.assertIn("notify('Created '+data.ticket.id", PAGE)

    def test_queue_preview_sorts_by_priority_then_numeric_ticket_id(self):
        self.assertIn("priorityOrder[a.priority]??9)-(priorityOrder[b.priority]??9)", PAGE)
        self.assertIn("Number(a.id.slice(1))-Number(b.id.slice(1))", PAGE)


if __name__ == "__main__":
    unittest.main()
