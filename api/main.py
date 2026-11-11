"""The FastAPI app: wires routes, error handling and CORS together.

Run with:  uvicorn api.main:app --reload
Interactive docs: http://127.0.0.1:8000/docs
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.defaults import build_default_chama
from api.errors import register_error_handlers
from api.routes import contributions, demo, loans, members, summary
from chama_manager import Chama


def create_app(chama: Chama | None = None) -> FastAPI:
    """Build the app. Tests pass their own Chama; the server uses the default."""
    app = FastAPI(title="Chama Manager API", version="0.1.0")
    app.state.chama = chama or build_default_chama()

    register_error_handlers(app)

    # Allow the Vite dev server (the frontend) to call this API from the browser.
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_methods=["*"],
        allow_headers=["*"],
    )

    for router in (summary.router, members.router, contributions.router,
                   loans.router, demo.router):
        app.include_router(router)
    return app


app = create_app()