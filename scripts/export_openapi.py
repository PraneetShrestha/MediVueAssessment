"""
Export OpenAPI 3.0 schema from the FastAPI app to openapi.json and openapi.yaml.
Run from repo root: python scripts/export_openapi.py

Use openapi.yaml (or openapi.json) in Swagger Hub: Create API -> Import -> paste file or URL.
"""
import json
import sys
from pathlib import Path

# Run from repo root so app is importable
REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

import yaml
from app.main import app


def main() -> None:
    spec = app.openapi()
    out_dir = REPO_ROOT

    out_json = out_dir / "openapi.json"
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f"Wrote {out_json}")

    out_yaml = out_dir / "openapi.yaml"
    with open(out_yaml, "w", encoding="utf-8") as f:
        yaml.dump(
            spec,
            f,
            default_flow_style=False,
            sort_keys=False,
            allow_unicode=True,
        )
    print(f"Wrote {out_yaml}")


if __name__ == "__main__":
    main()
