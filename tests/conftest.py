from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import create_app

MINIMAL_PDF = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF\n"


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    return tmp_path / "data"


@pytest.fixture
def client(data_dir: Path) -> TestClient:
    return TestClient(create_app(data_dir))


@pytest.fixture
def pdf_bytes() -> bytes:
    return MINIMAL_PDF
