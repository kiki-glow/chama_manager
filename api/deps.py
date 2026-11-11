"""FastAPI dependencies shared by all routes."""

from typing import Annotated

from fastapi import Depends, Request

from chama_manager import Chama


def get_chama(request: Request) -> Chama:
    """Return the Chama stored on the app (one chama per running server)."""
    chama: Chama = request.app.state.chama
    return chama

# use a parameter type in a route: async def handler(chama: ChamaDep)
ChamaDep = Annotated[Chama, Depends(get_chama)]