"""Tests for the month helpers in dates.py."""

import unittest
from datetime import date

from chama_manager.dates import add_months, month_start


class MonthStartTests(unittest.TestCase):
    """month_start snaps any date to the 1st of its month."""

    def test_first_of_month(self) -> None:
        self.assertEqual(month_start(date(2026, 12, 31)), date(2026, 12, 1))


class AddMonthsTests(unittest.TestCase):
    """add_months moves dates by whole months without overflowing."""

    def test_simple_shift(self) -> None:
        self.assertEqual(add_months(date(2026, 1, 10), 1), date(2026, 2, 10))

    def test_clamps_to_last_day_of_month(self) -> None:
        self.assertEqual(add_months(date(2026, 1, 31), 1), date(2026, 2, 28))
        self.assertEqual(add_months(date(2028, 1, 31), 1), date(2028, 2, 29))

    def test_crosses_year_boundary(self) -> None:
        self.assertEqual(add_months(date(2026, 11, 15), 3), date(2027, 2, 15))


if __name__ == "__main__":
    unittest.main()