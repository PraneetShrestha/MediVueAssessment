# MediVue Task Management API

FastAPI backend for the MediVue backend assessment: task management with filtering, tagging, and deadlines.

## Setup

### Prerequisites

- Python 3.10+ (3.11 recommended)
- Docker and Docker Compose (for running PostgreSQL and optionally the API)

### Local development (API on host, DB in Docker)

1. Start PostgreSQL:
   ```bash
   docker-compose up -d db
   ```
2. Create a virtualenv and install dependencies:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\activate   # Windows
   pip install -r requirements.txt -r requirements-dev.txt
   ```
3. Run the API:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```
4. Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for Swagger UI.

**Environment (optional):** Set `DATABASE_URL` if your Postgres user/password/host differ. Default:
`postgresql+psycopg2://medivue:medivuepassword@localhost:5432/medivue_db`.

### Run app + DB with one command (Docker)

```bash
docker-compose up --build
```

- API: [http://localhost:8000](http://localhost:8000) (redirects to `/docs`)
- DB: port 5432, user `medivue`, password `medivuepassword`, database `medivue_db`

---

## Design decisions

- **Layered structure:** Routes → Pydantic schemas (validation/serialization) → service layer (business logic + DB) → SQLAlchemy models. Keeps HTTP, validation, and persistence separate and testable.
- **PostgreSQL:** Chosen over SQLite for the assessment to match the “preferred” requirement, support concurrent access, and use a production-style setup with Docker. The same code could target SQLite by switching `DATABASE_URL` and ensuring SQLite-compatible types if needed.
- **Soft delete:** See below.
- **Tagging:** Many-to-many via a join table; see “Tagging implementation” below.

---

## Soft delete (DELETE /tasks/{id})

**Choice:** Soft delete (set `is_deleted = True` on the task row).

**Justification:**

- **Audit and compliance:** History of tasks is preserved; you can still report on or restore deleted items.
- **Undo:** “Restore” can be implemented later by flipping `is_deleted` back to `False` without restoring from backups.
- **Referential integrity:** No need to cascade-delete or null out references; related data (e.g. tag links) stays consistent.
- **Implementation:** All read paths (list and get by id) filter with `is_deleted = False`, so deleted tasks never appear in the API. No change to table schema beyond one indexed boolean.

A hard delete would free space and simplify some queries but would lose history and make undo impossible without backups.

---

## Tagging implementation (Tasks ↔ Tags)

**Chosen approach:** Normalized **join table** (`task_tags`) linking `tasks.id` and `tags.id`. Each tag name lives once in `tags`; tasks reference tags via the association table.

**Trade-offs vs alternatives:**

| Approach | Pros | Cons |
|----------|------|------|
| **Join table (current)** | Normalized; no duplicate tag names; easy to query “all tasks with tag X” and “all tags for task Y”; standard SQL and indexes (e.g. on `tags.name`, FKs). | Extra table and joins; slightly more complex writes (resolve or create tag by name, then link). |
| **PostgreSQL ARRAY of text** | Single table; simple schema; good for “task has these strings.” | Duplicate strings across rows; filtering by tag requires array operators; less friendly to “tag as entity” (e.g. rename tag everywhere). |
| **PostgreSQL JSONB** | Flexible; can store lists or nested data. | Same duplication and query ergonomics as array; JSONB indexing is more involved for “tag in list” filters. |

**Why the join table:** We need filtering by tag and a stable list of tag names. The join table gives clear indexing (e.g. on `tags.name` and composite indexes if needed), simple “tasks containing any of these tags” queries, and one place to update a tag name. ARRAY/JSONB are better when the list is unstructured or rarely queried by value.

---

## Production readiness (improvements)

- **Migrations:** Replace `Base.metadata.create_all()` with Alembic (or similar) for versioned, reversible schema changes.
- **Config:** Load all settings from environment (or a config service); no hardcoded defaults for URLs/secrets in code.
- **Health:** Extend `/health` to check DB connectivity (e.g. run a simple query).
- **Security:** Use secrets for DB passwords; consider rate limiting, auth (e.g. API keys or JWT), and CORS restricted to known origins.
- **Observability:** Structured logging, metrics (e.g. request latency, error counts), and optional tracing.
- **Testing:** Broader test suite (see `tests/`), including integration tests against a real or test DB.
- **API versioning:** Prefix routes (e.g. `/api/v1/tasks`) and/or OpenAPI docs for future backward-compatible changes.

---

## Tests

```bash
pip install -r requirements-dev.txt
pytest
```

See `tests/` for pytest + httpx tests covering task creation, validation failures, list filtering (tags, priority), and PATCH partial updates.

---

## API overview

| Method | Path | Description |
|--------|------|-------------|
| POST | /tasks | Create task (title, description, priority, due_date, tags). |
| GET | /tasks | List tasks with optional filters: `completed`, `priority`, `tags` (CSV), `limit`, `offset`. |
| GET | /tasks/{id} | Get one task or 404. |
| PATCH | /tasks/{id} | Partial update; only sent fields are changed. |
| DELETE | /tasks/{id} | Soft delete (task is hidden from all reads). |

Full interactive docs: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs).

---

## Project layout

- `app/main.py` – FastAPI app, route registration, startup (create tables).
- `app/routes/tasks.py` – Task HTTP endpoints.
- `app/schema/tasks.py` – Pydantic models (TaskCreate, TaskUpdate, TaskRead, PaginatedTasks).
- `app/services/task_service.py` – Task and tag business logic and DB access.
- `app/models/` – SQLAlchemy models (Task, Tag, `task_tags`).
- `app/db.py` – Engine, session factory, `get_db` dependency.
- `tests/` – Pytest + httpx tests.
