"""Members: the Member model, phone validation and MemberRegistry."""

import re
from dataclasses import dataclass
from datetime import date
from typing import Final

from .exceptions import DuplicateMemberError, InvalidMemberError, MemberNotFoundError

# Kenyan mobiles: 07xx / 01xx locally, or 254 / +254 internationally.
_PHONE_RE: Final = re.compile(r"^(?:\+?254|0)([17]\d{8})$")

def normalize_phone(raw: str) -> str:
    """Return a Kenyan mobile number in 254XXXXXXXXX form.
    
    Raises InvalidMemberError if it does not look like a Kenyan mobile.
    """
    # strip spaces and dashes
    cleaned = re.sub(r"[\s-]", "", str(raw))
    match = _PHONE_RE.match(cleaned)
    if not match:
        raise InvalidMemberError(f"Invalid Kenyan phone number: {raw!r}")
    return "254" + match.group(1)

@dataclass(frozen=True)
class Member:
    """A chama member.
    
    Frozen (immutable) so a member's identity can't change by accident.
    Name and phone are cleaned up automatically on creation.
    """

    id: int
    name: str
    phone: str
    joined_on: date

    def __post_init__(self) -> None:
        """Validate ad normalise fields (frozen, so use object.__setattr__)."""
        name = self.name.strip() if isinstance(self.name, str) else ""
        if not name:
            raise InvalidMemberError("Member name cannot be blank.")
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "phone", normalize_phone(self.phone))

class MemberRegistry:
    """Holds the chama's members and keeps phone numbers unique."""

    def __init__(self) -> None:
        """Start with no members."""
        self._members: dict[int, Member] = {}
        self._next_id: int = 1 # simple auto-increment

    def add(self, name: str, phone: str, joined_on: date | None = None) -> Member:
        """Register a new member; a repeated phone number is ejected."""
        member = Member(self._next_id, name, phone, joined_on or date.today())

        # compare normalised numbers so "0712..." and "+254712..." clash
        if any(m.phone == member.phone for m in self._members.values()):
            raise DuplicateMemberError(f"Phone {member.phone} is already registered.")

        # only consume the id once the member is accepted
        self._members[member.id] = member
        self._next_id += 1
        return member

    def get(self, member_id: int) -> Member:
        """Return a member by id or raise MemberNotFoundError."""
        try:
            return self._members[member_id]
        except KeyError:
            raise MemberNotFoundError(f"No member with id {member_id}.") from None

    def all(self) -> list[Member]:
        """All members, in the order they joined"""
        return list(self._members.values())