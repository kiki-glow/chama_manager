"""Request and response shapes for members."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, Field


class MemberCreate(BaseModel):
    """Body of POST /members."""

    name: str = Field(min_length=1, examples=["Glory Kinya"])
    phone: str = Field(examples=["0712 345 678"])

class MemberOut(BaseModel):
    """A member plus two figures the UI always wants next to them."""

    id: int
    name: str
    phone: str
    joined_on: date
    total_savings: Decimal
    max_loan: Decimal

# Pydantic checks the incoming data automatically, so a missing name is rejected before the code runs.