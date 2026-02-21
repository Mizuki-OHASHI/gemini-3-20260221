"""Generate openapi.yaml without requiring real credentials."""
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock

# Mock Firebase so the app can be imported without serviceAccountKey
sys.modules["firebase_admin"] = MagicMock()
sys.modules["firebase_admin.credentials"] = MagicMock()
sys.modules["firebase_admin.firestore"] = MagicMock()
sys.modules["firebase_admin.storage"] = MagicMock()

os.environ.setdefault("GEMINI_API_KEY", "dummy")
os.environ.setdefault("FIREBASE_STORAGE_BUCKET", "dummy")

from app.main import app  # noqa: E402

import yaml  # noqa: E402

spec = app.openapi()
out = Path(__file__).resolve().parent.parent.parent / "web" / "openapi.yaml"
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(yaml.dump(spec, allow_unicode=True, sort_keys=False))
print(f"Generated: {out}")
