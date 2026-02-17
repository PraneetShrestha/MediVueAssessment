## FastAPI backend

### Prereqs
- Python 3.11+ recommended

### Setup
From the repo root:

```bash
python -m venv .venv
.\.venv\Scripts\activate
python -m pip install -U pip
pip install -r requirements.txt
```

### Run (dev)
```bash
.\.venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Then open:
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`
- `http://127.0.0.1:8000/redoc`

### Env vars
Create `.env` (optional):
- `ENV=development|staging|production` (default: `development`)
- `ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000` (default: `*`)

