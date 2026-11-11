"""API tests for contributions and balances."""

from .base import ApiTestCase


class ContributionEndpointTests(ApiTestCase):
    """Recording payments and reading balances."""

    def test_record_and_statement(self) -> None:
        member_id = self.add_member()
        self.contribute(member_id, "1000")
        statement = self.client.get(f"/members/{member_id}/contributions").json()
        self.assertEqual(len(statement), 1)
        self.assertEqual(statement[0]["amount"], "1000.00")

    def test_partial_payment_leaves_balance_and_overdue_flag(self) -> None:
        member_id = self.add_member()
        self.contribute(member_id, "400")
        balance = self.client.get(
            f"/members/{member_id}/balance", params={"period": "2026-01-01"}
        ).json()
        self.assertEqual(balance["paid"], "400.00")
        self.assertEqual(balance["due"], "600.00")
        self.assertTrue(balance["overdue"])

    def test_unknown_member_is_404(self) -> None:
        response = self.client.post("/members/99/contributions", json={"amount": "500"})
        self.assertEqual(response.status_code, 404)

    def test_negative_amount_is_422(self) -> None:
        member_id = self.add_member()
        response = self.client.post(
            f"/members/{member_id}/contributions", json={"amount": "-5"}
        )
        self.assertEqual(response.status_code, 422)