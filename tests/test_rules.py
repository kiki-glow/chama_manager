"""Tests for ChamaRules validation and defaults."""

import unittest
from decimal import Decimal

from chama_manager import ChamaRules, InvalidAmountError, InvalidRulesError, ReducingBalanceInterest


class RulesTests(unittest.TestCase):
    """ChamaRules refuses impossible settings."""

    def test_rejects_zero_contribution(self) -> None:
        with self.assertRaises(InvalidAmountError):
            ChamaRules(Decimal("0"))

    def test_rejects_negative_grace_days(self) -> None:
        with self.assertRaises(InvalidRulesError):
            ChamaRules(Decimal("1000"), grace_days=-1)

    def test_zero_fine_means_no_fine(self) -> None:
        self.assertEqual(ChamaRules(Decimal("1000")).late_fine, Decimal("0.00"))

    def test_loan_defaults(self) -> None:
        rules = ChamaRules(Decimal("1000"))
        self.assertEqual(rules.monthly_rate, Decimal("0.05"))
        self.assertIsInstance(rules.interest_strategy, ReducingBalanceInterest)

    def test_rejects_impossible_loan_settings(self) -> None:
        with self.assertRaises(InvalidRulesError):
            ChamaRules(Decimal("1000"), loan_multiple=0)
        with self.assertRaises(InvalidRulesError):
            ChamaRules(Decimal("1000"), max_term_months=0)
        with self.assertRaises(InvalidRulesError):
            ChamaRules(Decimal("1000"), monthly_interest_percent=Decimal("101"))


if __name__ == "__main__":
    unittest.main()