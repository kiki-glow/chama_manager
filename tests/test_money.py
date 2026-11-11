"""Tests for money.to_money: typing, rounding and rejection rules."""

import unittest
from decimal import Decimal
from typing import Any

from chama_manager.exceptions import InvalidAmountError
from chama_manager.money import to_money

class ToMoneyTests(unittest.TestCase):
    """Valid inputs are normalized; everything else raises."""

    def test_accepts_int_str_and_decimal(self) -> None:
        self.assertEqual(to_money(500), Decimal("500.00"))
        self.assertEqual(to_money("1000"), Decimal("1000.00"))
        self.assertEqual(to_money(Decimal("12.5")), Decimal("12.50"))

    def test_rounds_half_up_to_two_places(self) -> None:
        self.assertEqual(to_money("1000.505"), Decimal("1000.51"))

    def test_rejects_floats_and_bools(self) -> None:
        # `Any` lets us pass deliberately wrong types past the type checker.
        cases: tuple[Any, ...] = (0.1, True)
        for bad in cases:
            with self.subTest(bad=bad):
                with self.assertRaises(InvalidAmountError):
                    to_money(bad)

    def test_rejects_non_positive_and_garbage(self) -> None:
        cases: tuple[Any, ...] = (0, -5, "abc", "NaN", None, [1])
        for bad in cases:
            with self.subTest(bad=bad):
                with self.assertRaises(InvalidAmountError):
                    to_money(bad)

if __name__ == "__main__":
    unittest.main()