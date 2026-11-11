"""Translate chama_manager errors into HTTP responses."""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from chama_manager import (
    ActiveLoanExistsError,
    ChamaError, 
    DuplicateMemberError,
    LoanNotFoundError,
    MemberNotFoundError
)

# first match wins. any other ChamaError is a rule violation -> 422.
_STATUS_BY_ERROR: list[tuple[type[ChamaError], int]] = [
    (MemberNotFoundError, 404),
    (LoanNotFoundError, 404),
    (DuplicateMemberError, 409),
    (ActiveLoanExistsError, 409)
]

def status_for(error: Exception) -> int:
    """HTTP status code for a domain error."""
    for error_type, status in _STATUS_BY_ERROR:
        if isinstance(error, error_type):
            return status
    return 422

def register_error_handlers(app: FastAPI) -> None:
    """Make every ChamaError come back as {"error": ..., "detail": ...}."""

    @app.exception_handler(ChamaError)
    async def handle_chama_error(_: Request, error: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=status_for(error),
            content={"error": type(error).__name__, "detail": str(error)}
        )