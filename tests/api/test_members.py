"""Shared fixture for API tests (not a test module itself)."""

import unittest
from decimal import Decimal

from fastapi.testclient import TestClient

from api.main import create_app
from chama_manager import Chama, ChamaRules, FlatInterest


class ApiTestCase(unittest.TestCase):
    """Each test gets a fresh app with its own empty chama."""

    client: TestClient

    def setUp(self) -> None:
        rules = ChamaRules(
            Decimal("1000"),
            loan_multiple=3,
            max_term_months=6,
            monthly_interest_percent=Decimal("10"),
            interest_strategy=FlatInterest(),
        )
        self.client = TestClient(create_app(Chama("Test Chama", rules)))

    def add_member(self, name: str = "Alice", phone: str = "0712345678") -> int:
        """Create a member through the API and return the new id."""
        response = self.client.post("/members", json={"name": name, "phone": phone})
        self.assertEqual(response.status_code, 201)
        return int(response.json()["id"])

    def contribute(self, member_id: int, amount: str, paid_on: str = "2026-01-03") -> None:
        """Record a contribution through the API."""
        response = self.client.post(
            f"/members/{member_id}/contributions",
            json={"amount": amount, "paid_on": paid_on},
        )
        self.assertEqual(response.status_code, 201)