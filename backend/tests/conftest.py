"""Make `backend/` importable as the root package dir for tests."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
# db/session.py builds an engine at import time; give it a syntactically valid URL.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test")
