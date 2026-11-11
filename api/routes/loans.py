"""Loan endpoints: issue, list, fetch and repay."""

from datetime import date

from fastapi import APIRouter

from api.deps import ChamaDep
from api.schemas.loans import LoanCreate, LoanOut, RepaymentCreate
from chama_manager import Loan

router = APIRouter(prefix="/loans", tags=["loans"])


def to_loan_out(loan: Loan) -> LoanOut:
    """Convert a core Loan and flag which installments are overdue today."""
    out = LoanOut.model_validate(loan)
    out.overdue = [i.number for i in loan.overdue_installments(date.today())]
    return out


@router.post("", response_model=LoanOut, status_code=201)
async def issue_loan(body: LoanCreate, chama: ChamaDep) -> LoanOut:
    """Issue a loan if the chama's rules allow it."""
    loan = chama.issue_loan(body.member_id, body.principal, body.term_months, body.issued_on)
    return to_loan_out(loan)


@router.get("", response_model=list[LoanOut])
async def list_loans(chama: ChamaDep, member_id: int | None = None) -> list[LoanOut]:
    """All loans, or only one member's when ?member_id= is given."""
    loans = chama.all_loans() if member_id is None else chama.loans_for(member_id)
    return [to_loan_out(loan) for loan in loans]


@router.get("/{loan_id}", response_model=LoanOut)
async def get_loan(loan_id: int, chama: ChamaDep) -> LoanOut:
    """One loan with its schedule. Unknown id -> 404."""
    return to_loan_out(chama.get_loan(loan_id))


@router.post("/{loan_id}/repayments", response_model=LoanOut, status_code=201)
async def repay_loan(loan_id: int, body: RepaymentCreate, chama: ChamaDep) -> LoanOut:
    """Record a repayment and return the updated loan."""
    chama.repay_loan(loan_id, body.amount, body.paid_on)
    return to_loan_out(chama.get_loan(loan_id))