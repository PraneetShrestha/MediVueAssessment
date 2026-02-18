from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.db import Base, engine
from app.routes.tasks import router as tasks_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="MediVue Task Management API",
        description="""
Task Management API with filtering, tagging, and deadlines.

- **Tasks**: Create, list (with filters), get, partial update (PATCH), and soft-delete.
- **Filtering**: By `completed`, `priority`, and `tags` (CSV).
- **Pagination**: `limit` and `offset` on list.
        """.strip(),
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
        servers=[
            {"url": "http://127.0.0.1:8000", "description": "Local development"},
            {"url": "http://localhost:8000", "description": "Local (localhost)"},
        ],
    )

    # Include task routes
    app.include_router(tasks_router)

    @app.get("/", include_in_schema=False)
    def root():
        """Redirect root to Swagger UI."""
        return RedirectResponse(url="/docs", status_code=302)

    @app.on_event("startup")
    def on_startup() -> None:
        # For the purposes of this assessment we use simple metadata.create_all.
        # In a real-world app you'd likely use Alembic migrations instead.
        Base.metadata.create_all(bind=engine)

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
