"""Tests for members: phone cleaning, the Member model and the registry."""

import unittest
from datetime import date

from chama_manager.exceptions import (
    DuplicateMemberError,
    InvalidMemberError,
    MemberNotFoundError,
)
from chama_manager.members import Member, MemberRegistry, normalize_phone

JAN = date(2026, 1, 1)


class NormalizePhoneTests(unittest.TestCase):
    """All common Kenyan formats collapse to one canonical form."""

    def test_accepts_common_formats(self) -> None:
        for raw in ("0712345678", "+254712345678", "254712345678", "0712 345-678"):
            with self.subTest(raw=raw):
                self.assertEqual(normalize_phone(raw), "254712345678")

    def test_accepts_01_prefix(self) -> None:
        self.assertEqual(normalize_phone("0112345678"), "254112345678")

    def test_rejects_bad_numbers(self) -> None:
        for raw in ("", "12345", "0812345678", "+25471234567"):
            with self.subTest(raw=raw):
                with self.assertRaises(InvalidMemberError):
                    normalize_phone(raw)


class MemberTests(unittest.TestCase):
    """Member cleans its fields and refuses empty names."""

    def test_cleans_name_and_phone(self) -> None:
        m = Member(1, "  Wanjiru ", "0712345678", JAN)
        self.assertEqual(m.name, "Wanjiru")
        self.assertEqual(m.phone, "254712345678")

    def test_rejects_empty_name(self) -> None:
        with self.assertRaises(InvalidMemberError):
            Member(1, "   ", "0712345678", JAN)


class RegistryTests(unittest.TestCase):
    """The registry hands out ids and keeps phone numbers unique."""

    def setUp(self) -> None:
        self.registry = MemberRegistry()
        self.alice = self.registry.add("Alice", "0712345678", JAN)

    def test_ids_increment(self) -> None:
        bob = self.registry.add("Bob", "0722345678", JAN)
        self.assertEqual((self.alice.id, bob.id), (1, 2))

    def test_duplicate_phone_in_other_format_is_rejected(self) -> None:
        with self.assertRaises(DuplicateMemberError):
            self.registry.add("Alice 2", "+254712345678", JAN)
        # A failed add must not burn an id.
        bob = self.registry.add("Bob", "0722345678", JAN)
        self.assertEqual(bob.id, 2)

    def test_unknown_member_raises(self) -> None:
        with self.assertRaises(MemberNotFoundError):
            self.registry.get(99)

    def test_all_lists_members_in_join_order(self) -> None:
        bob = self.registry.add("Bob", "0722345678", JAN)
        self.assertEqual(self.registry.all(), [self.alice, bob])


if __name__ == "__main__":
    unittest.main()