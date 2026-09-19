"""Points the app at an isolated copy of artifacts/logs for the test
session, so running the suite never mutates the live demo's adaptive
model state (its learn_one updates and version counters)."""

import os
import shutil
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = PROJECT_ROOT / "backend"
sys.path.insert(0, str(BACKEND_DIR))


@pytest.fixture(scope="session")
def test_env(tmp_path_factory):
    tmp_root = tmp_path_factory.mktemp("spam_detection_test_artifacts")

    artifacts_src = PROJECT_ROOT / "artifacts"
    artifacts_dst = tmp_root / "artifacts"
    shutil.copytree(artifacts_src, artifacts_dst)

    logs_dst = tmp_root / "logs"
    logs_dst.mkdir()

    os.environ["ARTIFACTS_DIR"] = str(artifacts_dst)
    os.environ["LOGS_DIR"] = str(logs_dst)
    os.environ["DATA_DIR"] = str(PROJECT_ROOT / "data")

    from app.core.config import get_settings
    get_settings.cache_clear()

    return {"artifacts_dir": artifacts_dst, "logs_dir": logs_dst}


@pytest.fixture(scope="session")
def client(test_env):
    from fastapi.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        yield c
