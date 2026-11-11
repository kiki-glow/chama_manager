"""Tests for contributions: the model, payments, overdue checks and reports."""

import unittest
from datetime import date
from decimal import Decimal
from typing import Any

from chama_manager import (
    Chama,
    ChamaRules,
    InvalidAmountError,
    Member,
    MemberNotFoundError,
)
from chama_manager.contributions import Contribution

JAN = date(2026, 1, 1)
FEB = date(2026, 2, 1)


class ContributionModelTests(unittest.TestCase):
    """Contribution validates the amount and snaps period to month start."""

    def test_period_snaps_to_first_of_month(self) -> None:
        c = Contribution(1, Decimal("500"), date(2026, 3, 17), date(2026, 3, 17))
        self.assertEqual(c.period, date(2026, 3, 1))
        self.assertEqual(c.amount, Decimal("500.00"))

    def test_rejects_float_and_zero_amounts(self) -> None:
        cases: tuple[Any, ...] = (99.5, 0)
        for bad in cases:
            with self.subTest(bad=bad):
                with self.assertRaises(InvalidAmountError):
                    Contribution(1, bad, date(2026, 3, 1), date(2026, 3, 1))


class ContributionTestCase(unittest.TestCase):
    """Base class: a fresh chama with one member before every test."""

    chama: Chama
    alice: Member

    def setUp(self) -> None:
        rules = ChamaRules(Decimal("1000"), grace_days=5, late_fine=Decimal("50"))
        self.chama = Chama("Test Chama", rules)
        self.alice = self.chama.add_member("Alice", "0712345678", JAN)


class RecordingTests(ContributionTestCase):
    """Partial payments, overpayments and per-month grouping."""

    def test_partial_payments_accumulate(self) -> None:
        self.chama.record_contribution(self.alice.id, 400, date(2026, 1, 3))
        self.chama.record_contribution(self.alice.id, 300, date(2026, 1, 9))
        self.assertEqual(self.chama.paid_for_period(self.alice.id, JAN), Decimal("700.00"))
        self.assertEqual(self.chama.balance_due(self.alice.id, JAN), Decimal("300.00"))

    def test_overpayment_never_gives_negative_balance(self) -> None:
        self.chama.record_contribution(self.alice.id, 1500, date(2026, 1, 3))
        self.assertEqual(self.chama.balance_due(self.alice.id, JAN), Decimal("0.00"))

    def test_months_are_tracked_separately(self) -> None:
        self.chama.record_contribution(self.alice.id, 1000, date(2026, 1, 3))
        self.assertEqual(self.chama.balance_due(self.alice.id, FEB), Decimal("1000.00"))

    def test_can_pay_late_for_an_earlier_month(self) -> None:
        # Paid in February but explicitly for January.
        self.chama.record_contribution(self.alice.id, 1000, date(2026, 2, 10), JAN)
        self.assertEqual(self.chama.balance_due(self.alice.id, JAN), Decimal("0.00"))

    def test_float_amount_rejected(self) -> None:
        bad: Any = 250.5  # deliberately the wrong type
        with self.assertRaises(InvalidAmountError):
            self.chama.record_contribution(self.alice.id, bad, JAN)

    def test_unknown_member_rejected(self) -> None:
        with self.assertRaises(MemberNotFoundError):
            self.chama.record_contribution(99, 500, JAN)


class OverdueTests(ContributionTestCase):
    """A month is overdue only after the grace period, and only if unpaid."""

    def test_grace_period_boundary(self) -> None:
        # Jan 1 + 5 grace days = Jan 6 is the last on-time day.
        self.assertFalse(self.chama.is_overdue(self.alice.id, JAN, date(2026, 1, 6)))
        self.assertTrue(self.chama.is_overdue(self.alice.id, JAN, date(2026, 1, 7)))

    def test_fully_paid_is_never_overdue(self) -> None:
        self.chama.record_contribution(self.alice.id, 1000, date(2026, 1, 2))
        self.assertFalse(self.chama.is_overdue(self.alice.id, JAN, date(2026, 3, 1)))


class ReportTests(ContributionTestCase):
    """Totals and statements."""

    def test_totals_and_statement_order(self) -> None:
        bob = self.chama.add_member("Bob", "0722345678", JAN)
        self.chama.record_contribution(self.alice.id, 1000, date(2026, 2, 2))
        self.chama.record_contribution(self.alice.id, 1000, date(2026, 1, 2))
        self.chama.record_contribution(bob.id, 500, date(2026, 1, 4))

        self.assertEqual(self.chama.total_savings(self.alice.id), Decimal("2000.00"))
        self.assertEqual(self.chama.total_pool(), Decimal("2500.00"))
        dates = [c.paid_on for c in self.chama.statement(self.alice.id)]
        self.assertEqual(dates, [date(2026, 1, 2), date(2026, 2, 2)])


if __name__ == "__main__":
    unittest.main()