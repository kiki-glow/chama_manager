"""Response shape for the dashboard summary."""

from decimal import Decimal

from pydantic import BaseModel

class SummaryOut(BaseModel):
    """Headline numbers and setting for the dashboard."""

    name: str
    member_count: int
    pool_total: Decimal
    available_funds: Decimal
    contribution_amount: Decimal
    grace_days: int
    monthly_interest_percent: Decimal
    loan_multiple: int
    max_term_months: int