"""Dashboard summary endpoint."""

from fastapi import APIRouter

from api.deps import ChamaDep
from api.schemas.summary import SummaryOut

router = APIRouter(tags=["summary"])


@router.get("/summary", response_model=SummaryOut)
async def get_summary(chama: ChamaDep) -> SummaryOut:
    """Headline numbers for the dashboard."""
    rules = chama.rules
    return SummaryOut(
        name=chama.name,
        member_count=len(chama.members),
        pool_total=chama.total_pool(),
        available_funds=chama.available_funds(),
        contribution_amount=rules.contribution_amount,
        grace_days=rules.grace_days,
        monthly_interest_percent=rules.monthly_interest_percent,
        loan_multiple=rules.loan_multiple,
        max_term_months=rules.max_term_months
    )

# GET /summary reads a few numbers from Chama and returns them for the dashboard