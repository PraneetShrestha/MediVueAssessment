# Swagger Hub – MediVue Task Management API

Use the OpenAPI spec in **Swagger Hub** so you can view and try the API in the Swagger Hub UI.

## 1. Export the spec (optional)

The repo already includes `openapi.yaml` and `openapi.json`. To regenerate them after changing the API:

```bash
# From repo root, with venv activated
python scripts/export_openapi.py
```

## 2. Open in Swagger Hub UI

### Option A: Import from file (no account required for try-it)

1. Go to **[Swagger Editor](https://editor.swagger.io)** (or [Swagger Hub](https://app.swaggerhub.com) and create/import an API).
2. **File → Import file** (or paste):
   - Use the project’s **`openapi.yaml`** or **`openapi.json`** from the repo root.
3. The document will load and the right-hand side will show the **Swagger UI** with all endpoints.

### Option B: Swagger Hub (hosted doc + try-it)

1. Go to **[https://app.swaggerhub.com](https://app.swaggerhub.com)** and sign in (or create a free account).
2. Click **Create New → Create API**.
3. Choose **Import and Document API**.
4. Either:
   - **Paste** the contents of `openapi.yaml` or `openapi.json`, or  
   - **Upload** the file, or  
   - If your API is deployed, enter: `https://your-api-url/openapi.json`.
5. Set **API name** (e.g. `MediVue Task Management API`) and save.
6. Open the API and use the **Swagger UI** tab to browse and **Try it out** against your server.

## 3. Point the UI at your running API

- In the spec we set **servers** to `http://127.0.0.1:8000` and `http://localhost:8000`.
- Start your app locally:
  ```bash
  uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
  ```
- In Swagger Hub / Swagger Editor, use **Try it out** on any operation; requests will go to that server so you can run them against your real API.

If you deploy the API elsewhere, either:

- Regenerate the spec and add a new server entry (and re-import into Swagger Hub), or  
- In Swagger Hub, edit the API and add a server (e.g. `https://your-deployed-api.com`).

## Files

| File | Purpose |
|------|--------|
| `openapi.yaml` | OpenAPI 3 spec (YAML) – use this to import into Swagger Hub / Editor. |
| `openapi.json` | Same spec in JSON – alternative for import or URL. |
| `scripts/export_openapi.py` | Regenerates both files from the FastAPI app. |
