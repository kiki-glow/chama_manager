"""The chama the server starts with (until persistence and settings exist)."""

from decimal import Decimal

from chama_manager import Chama, ChamaRules, ReducingBalanceInterest


def build_default_chama() -> Chama:
    """Create a chama with sensible starting rules."""
    rules = ChamaRules(
        Decimal("1000"),  # monthly contribution
        grace_days=5,
        late_fine=Decimal("50"),
        loan_multiple=3,
        max_term_months=12,
        monthly_interest_percent=Decimal("5"),
        interest_strategy=ReducingBalanceInterest(),
    )
    return Chama("Umoja Savers", rules)