import os
import tempfile
from pathlib import Path

# Settings are read when the app is imported, so set test values first.
_TMP = Path(tempfile.mkdtemp())
os.environ.update(
    {
        "APP_NAME": "galacticos-test",
        "MODE": "local",
        "OLLAMA_MODEL": "ollama_chat/gemma4:e2b",
        "OLLAMA_API_BASE": "http://localhost:11434",
        "GOOGLE_API_KEY": "test-key",
        "GEMINI_GEMMA_MODEL": "gemma-4-4b-it",
        "DATABASE_URL": f"sqlite:///{_TMP / 'test.db'}",
    }
)

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.db import models  # noqa: E402,F401  (registers the tables)
from app.db.database import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture()
def client():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    with TestClient(app) as test_client:
        yield test_client
