"""Request and response shapes for loans."""

from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class LoanCreate(BaseModel):
    """Body of POST /loans. The chama's rules decide if it is allowed."""

    member_id: int
    principal: Decimal = Field(gt=0, examples=["2000"])
    term_months: int
    issued_on: date | None = None # defaults to today

class RepaymentCreate(BaseModel):
    """Body of POST /loans/{id}/repayments."""

    amount: Decimal = Field(gt=0, examples=["700"])
    paid_on: date | None = None

class InstallmentOut(BaseModel):
    """One line of the repayment schedule."""

    model_config = ConfigDict(from_attributes=True)

    number: int
    due_date: date
    principal: Decimal
    interest: Decimal
    payment: Decimal

class LoanOut(BaseModel):
    """A loan with its totals, schedule and which installments are late."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    member_id: int
    principal: Decimal
    term_months: int
    monthly_rate: Decimal
    issued_on: date
    total_interest: Decimal
    total_repayable: Decimal
    total_repaid: Decimal
    balance: Decimal
    is_active: bool
    schedule: list[InstallmentOut]
    overdue: list[int] = [] # installment numbers; filled in by the route