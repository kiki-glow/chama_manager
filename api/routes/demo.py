"""Demo endpoint: fill an empty chama with sample data."""

from datetime import date

from fastapi import APIRouter, HTTPException

from api.deps import ChamaDep

router = APIRouter(prefix="/demo", tags=["demo"])


@router.post("/seed", status_code=201)
async def seed(chama: ChamaDep) -> dict[str, int]:
    """Add three members, some savings and one loan (only if the chama is empty)."""
    if chama.members:
        raise HTTPException(status_code=409, detail="Chama already has data.")
    
    kinya = chama.add_member("Kinya Glory", "0712 345 678", date(2026, 1, 1))
    amanda = chama.add_member("Amanda Jones", "0733 555 000", date(2026, 1, 1))
    lawliet = chama.add_member("Lawliet Ryuzaki", "0723 111 222", date(2026, 1, 1))

    for month in (1, 2, 3): # Kinya and Lawliet pay in full; Amanda only part of Jan
        chama.record_contribution(kinya.id, 1000, date(2026, month, 3))
        chama.record_contribution(lawliet.id, 1000, date(2026, month, 5))
    chama.record_contribution(amanda.id, 400, date(2026, 1, 4))

    loan = chama.issue_loan(kinya.id, 2000, 4, date(2026, 3, 10))
    chama.repay_loan(loan.id, 600, date(2026, 4, 10)) # pays 1st installment only
    
    return {"members": len(chama.members), "loans": 1}