"""Member endpoints: create, list and fetch."""

from fastapi import APIRouter

from api.deps import ChamaDep
from api.schemas.members import MemberCreate, MemberOut
from chama_manager import Chama, Member

router = APIRouter(prefix="/members", tags=["members"])


def to_member_out(chama: Chama, member: Member) -> MemberOut:
    """Combine a member with their savings figures for the response."""
    return MemberOut(
        id=member.id,
        name=member.name,
        phone=member.phone,
        joined_on=member.joined_on,
        total_savings=chama.total_savings(member.id),
        max_loan=chama.max_loan_for(member.id),
    )


@router.post("", response_model=MemberOut, status_code=201)
async def create_member(body: MemberCreate, chama: ChamaDep) -> MemberOut:
    """Register a member. Duplicate phone -> 409, bad phone -> 422."""
    return to_member_out(chama, chama.add_member(body.name, body.phone))


@router.get("", response_model=list[MemberOut])
async def list_members(chama: ChamaDep) -> list[MemberOut]:
    """All members, in join order."""
    return [to_member_out(chama, m) for m in chama.members]


@router.get("/{member_id}", response_model=MemberOut)
async def get_member(member_id: int, chama: ChamaDep) -> MemberOut:
    """One member. Unknown id -> 404."""
    return to_member_out(chama, chama.get_member(member_id))