"""API tests for the dashboard summary and the demo seed."""

from .base import ApiTestCase


class SummaryTests(ApiTestCase):
    """Headline numbers."""

    def test_summary_reflects_contributions(self) -> None:
        member_id = self.add_member()
        self.contribute(member_id, "1500")
        summary = self.client.get("/summary").json()
        self.assertEqual(summary["member_count"], 1)
        self.assertEqual(summary["pool_total"], "1500.00")
        self.assertEqual(summary["available_funds"], "1500.00")


class DemoSeedTests(ApiTestCase):
    """The seed endpoint fills an empty chama exactly once."""

    def test_seed_once(self) -> None:
        first = self.client.post("/demo/seed")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(first.json()["members"], 3)
        self.assertEqual(len(self.client.get("/loans").json()), 1)
        self.assertEqual(self.client.post("/demo/seed").status_code, 409)