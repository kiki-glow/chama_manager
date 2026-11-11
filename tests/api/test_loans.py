"""API tests for issuing, listing and repaying loans."""

from .base import ApiTestCase


class LoanEndpointTests(ApiTestCase):
    """Alice saves 2,000 and Bob 4,000, so the pool is 6,000."""

    def setUp(self) -> None:
        super().setUp()
        self.alice = self.add_member("Alice", "0712345678")
        self.bob = self.add_member("Bob", "0722345678")
        self.contribute(self.alice, "2000")
        self.contribute(self.bob, "4000")

    def issue(self, member_id: int, principal: str = "3000", term: int = 3) -> dict[str, object]:
        """Issue a loan through the API and return the JSON."""
        response = self.client.post(
            "/loans",
            json={"member_id": member_id, "principal": principal,
                  "term_months": term, "issued_on": "2026-01-10"},
        )
        self.assertEqual(response.status_code, 201, response.text)
        body: dict[str, object] = response.json()
        return body

    def test_issue_returns_totals_and_schedule(self) -> None:
        loan = self.issue(self.alice)
        self.assertEqual(loan["total_repayable"], "3900.00")
        self.assertEqual(len(loan["schedule"]), 3)  # type: ignore[arg-type]

    def test_list_all_and_by_member(self) -> None:
        self.issue(self.alice)
        self.assertEqual(len(self.client.get("/loans").json()), 1)
        self.assertEqual(len(self.client.get("/loans", params={"member_id": self.bob}).json()), 0)

    def test_over_limit_is_422(self) -> None:
        response = self.client.post(
            "/loans", json={"member_id": self.alice, "principal": "6001", "term_months": 3}
        )
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"], "LoanLimitExceededError")

    def test_second_active_loan_is_409(self) -> None:
        self.issue(self.alice)
        response = self.client.post(
            "/loans", json={"member_id": self.alice, "principal": "100", "term_months": 1}
        )
        self.assertEqual(response.status_code, 409)

    def test_repayment_reduces_balance(self) -> None:
        loan = self.issue(self.alice)
        response = self.client.post(f"/loans/{loan['id']}/repayments", json={"amount": "1300"})
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["balance"], "2600.00")

    def test_overpayment_is_422(self) -> None:
        loan = self.issue(self.alice)
        response = self.client.post(f"/loans/{loan['id']}/repayments", json={"amount": "5000"})
        self.assertEqual(response.status_code, 422)
        self.assertEqual(response.json()["error"], "RepaymentExceedsBalanceError")

    def test_unknown_loan_is_404(self) -> None:
        self.assertEqual(self.client.get("/loans/99").status_code, 404)