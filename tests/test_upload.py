from datetime import datetime

from app.statuses import ALL_STATUSES, UPLOADED
from tests.conftest import MINIMAL_PDF


def test_valid_pdf_upload_sets_uploaded_status(client, pdf_bytes):
    response = client.post(
        "/invoices",
        files={"file": ("invoice.pdf", pdf_bytes, "application/pdf")},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["original_filename"] == "invoice.pdf"
    assert body["current_status"] == UPLOADED
    assert body["file_hash_sha256"]
    assert len(body["file_hash_sha256"]) == 64
    assert body["finalized_at"] is None
    assert set(body["status_timestamps"]) == set(ALL_STATUSES)
    assert body["status_timestamps"][UPLOADED] == body["uploaded_at"]
    for status in ALL_STATUSES:
        if status != UPLOADED:
            assert body["status_timestamps"][status] is None


def test_non_pdf_is_rejected_with_clear_error(client):
    response = client.post(
        "/invoices",
        files={"file": ("notes.txt", b"this is not a pdf", "text/plain")},
    )
    assert response.status_code == 400
    assert "Only PDF files are accepted" in response.json()["detail"]


def test_pdf_extension_with_non_pdf_content_is_rejected(client):
    response = client.post(
        "/invoices",
        files={"file": ("fake.pdf", b"not-a-pdf", "application/pdf")},
    )
    assert response.status_code == 400
    assert "Only PDF files are accepted" in response.json()["detail"]


def test_metadata_persists_after_upload(client, data_dir, pdf_bytes):
    created = client.post(
        "/invoices",
        files={"file": ("dhl-sample.pdf", pdf_bytes, "application/pdf")},
    ).json()
    invoice_id = created["id"]

    fetched = client.get(f"/invoices/{invoice_id}")
    assert fetched.status_code == 200
    stored = fetched.json()
    assert stored["id"] == invoice_id
    assert stored["original_filename"] == "dhl-sample.pdf"
    assert stored["file_hash_sha256"] == created["file_hash_sha256"]
    assert stored["current_status"] == UPLOADED
    assert stored["uploaded_at"] == created["uploaded_at"]

    db_path = data_dir / "invoices.sqlite"
    assert db_path.is_file()
    stored_pdf = data_dir / "uploads" / stored["stored_filename"]
    assert stored_pdf.is_file()
    assert stored_pdf.read_bytes() == pdf_bytes
    assert stored_pdf.name.endswith(".pdf")


def test_upload_timestamp_is_created(client, pdf_bytes):
    response = client.post(
        "/invoices",
        files={"file": ("invoice.pdf", pdf_bytes, "application/pdf")},
    )
    body = response.json()
    uploaded_at = datetime.fromisoformat(body["uploaded_at"])
    assert uploaded_at.tzinfo is not None
    assert body["status_timestamps"]["uploaded"] == body["uploaded_at"]
    assert body["finalized_at"] is None
    # Turnaround time later: finalized_at - uploaded_at once approved or rejected.


def test_rejected_upload_does_not_create_records(client, data_dir):
    client.post(
        "/invoices",
        files={"file": ("notes.txt", b"hello", "text/plain")},
    )
    assert client.app.state.store.count() == 0
    uploads = data_dir / "uploads"
    assert list(uploads.iterdir()) == []


def test_minimal_pdf_bytes_are_not_dataset_samples():
    assert MINIMAL_PDF.startswith(b"%PDF")
    assert b"DHL" not in MINIMAL_PDF
