"""Contribution endpoints, nested under a member."""

from datetime import date

from fastapi import APIRouter

from api.deps import ChamaDep
from api.schemas.contributions import BalanceOut, ContributionCreate, ContributionOut
from chama_manager import Contribution
from chama_manager.dates import month_start

router = APIRouter(prefix="/members/{member_id}", tags=["contributions"])


@router.post("/contributions", response_model=ContributionOut, status_code=201)
async def record_contribution(
    member_id: int, body: ContributionCreate, chama: ChamaDep
) -> Contribution:
    """Record a payment (partial payments are fine)."""
    paid_on = body.paid_on or date.today()
    return chama.record_contribution(member_id, body.amount, paid_on, body.period)


@router.get("/contributions", response_model=list[ContributionOut])
async def get_statement(member_id: int, chama: ChamaDep) -> list[Contribution]:
    """The member's payments, oldest first."""
    return chama.statement(member_id)


@router.get("/balance", response_model=BalanceOut)
async def get_balance(
    member_id: int, chama: ChamaDep, period: date | None = None
) -> BalanceOut:
    """What the member owes for a month (defaults to the current month)."""
    month = month_start(period or date.today())
    return BalanceOut(
        period=month,
        expected=chama.rules.contribution_amount,
        paid=chama.paid_for_period(member_id, month),
        due=chama.balance_due(member_id, month),
        overdue=chama.is_overdue(member_id, month),
    )