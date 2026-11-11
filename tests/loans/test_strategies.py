"""Tests for the interest strategies (flat and reducing balance)."""

import unittest
from datetime import date
from decimal import Decimal

from chama_manager import FlatInterest, ReducingBalanceInterest


class FlatInterestTests(unittest.TestCase):
    """Flat interest: same principal and interest every month."""

    def test_even_installments(self) -> None:
        schedule = FlatInterest().build_schedule(
            Decimal("3000.00"), Decimal("0.10"), 3, date(2026, 1, 10)
        )
        self.assertEqual(len(schedule), 3)
        self.assertEqual({i.payment for i in schedule}, {Decimal("1300.00")})

    def test_rounding_remainder_lands_on_last_installment(self) -> None:
        schedule = FlatInterest().build_schedule(
            Decimal("1000.00"), Decimal("0.10"), 3, date(2026, 1, 10)
        )
        self.assertEqual(sum((i.principal for i in schedule), Decimal("0")), Decimal("1000.00"))
        self.assertEqual(sum((i.interest for i in schedule), Decimal("0")), Decimal("300.00"))
        self.assertEqual(schedule[-1].principal, Decimal("333.34"))

    def test_due_dates_are_monthly_from_issue_date(self) -> None:
        schedule = FlatInterest().build_schedule(
            Decimal("900.00"), Decimal("0.10"), 3, date(2026, 1, 31)
        )
        self.assertEqual(
            [i.due_date for i in schedule],
            [date(2026, 2, 28), date(2026, 3, 31), date(2026, 4, 30)],
        )


class ReducingBalanceTests(unittest.TestCase):
    """Reducing balance: interest falls as the principal is paid down."""

    def setUp(self) -> None:
        self.schedule = ReducingBalanceInterest().build_schedule(
            Decimal("1200.00"), Decimal("0.01"), 12, date(2026, 1, 10)
        )

    def test_principals_add_up_exactly(self) -> None:
        total = sum((i.principal for i in self.schedule), Decimal("0"))
        self.assertEqual(total, Decimal("1200.00"))

    def test_first_interest_is_on_full_principal(self) -> None:
        self.assertEqual(self.schedule[0].interest, Decimal("12.00"))

    def test_interest_falls_every_month(self) -> None:
        pairs = zip(self.schedule, self.schedule[1:])
        self.assertTrue(all(a.interest > b.interest for a, b in pairs))

    def test_level_payment_except_possibly_the_last(self) -> None:
        payments = {i.payment for i in self.schedule[:-1]}
        self.assertEqual(len(payments), 1)

    def test_zero_rate_splits_principal_only(self) -> None:
        schedule = ReducingBalanceInterest().build_schedule(
            Decimal("1200.00"), Decimal("0"), 4, date(2026, 1, 10)
        )
        self.assertEqual({i.principal for i in schedule}, {Decimal("300.00")})
        self.assertEqual({i.interest for i in schedule}, {Decimal("0.00")})

    def test_single_month_loan(self) -> None:
        schedule = ReducingBalanceInterest().build_schedule(
            Decimal("500.00"), Decimal("0.05"), 1, date(2026, 1, 10)
        )
        self.assertEqual(schedule[0].principal, Decimal("500.00"))
        self.assertEqual(schedule[0].interest, Decimal("25.00"))

    def test_cheaper_than_flat_for_the_same_terms(self) -> None:
        flat = FlatInterest().build_schedule(
            Decimal("1200.00"), Decimal("0.01"), 12, date(2026, 1, 10)
        )
        flat_interest = sum((i.interest for i in flat), Decimal("0"))
        reducing_interest = sum((i.interest for i in self.schedule), Decimal("0"))
        self.assertLess(reducing_interest, flat_interest)


if __name__ == "__main__":
    unittest.main()