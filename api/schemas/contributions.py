"""Request and response shapes for contributions."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ContributionCreate(BaseModel):
    """Body of POST /members/{id}/contributions."""

    amount: Decimal = Field(gt=0, examples=["1000"])
    paid_on: date | None = None # defaults to today
    period: date | None = None # defaults to the month of paid_on

class ContributionOut(BaseModel):
    """One recorded payment."""

    model_config = ConfigDict(from_attributes=True) # read straight from core objects

    member_id: int
    amount: Decimal
    paid_on: date
    period: date

class BalanceOut(BaseModel):
    """How one member stands for one month."""

    period: date
    expected: Decimal
    paid: Decimal
    due: Decimal
    overdue: bool