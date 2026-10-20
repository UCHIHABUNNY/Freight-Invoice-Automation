"""PDF upload API. Does not extract, reconcile, draft, or change status after upload."""

from __future__ import annotations

import hashlib
import uuid
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile, status

from app.store import InvoiceStore

MAX_UPLOAD_BYTES = 20 * 1024 * 1024
PDF_MAGIC = b"%PDF"


def is_pdf(filename: str, content: bytes) -> bool:
    name = (filename or "").strip()
    if not name.lower().endswith(".pdf"):
        return False
    return content.startswith(PDF_MAGIC)


def create_app(data_dir: Path | None = None) -> FastAPI:
    root = Path(__file__).resolve().parent.parent
    store = InvoiceStore(Path(data_dir) if data_dir is not None else root / "data")
    app = FastAPI(title="Freight Invoice Automation", version="0.2.0")
    app.state.store = store

    @app.post("/invoices", status_code=status.HTTP_201_CREATED)
    async def upload_invoice(file: UploadFile = File(...)) -> dict:
        filename = file.filename or ""
        content = await file.read()
        if len(content) > MAX_UPLOAD_BYTES:
            raise HTTPException(
                status_code=400,
                detail="File is too large. Maximum size is 20 MB.",
            )
        if not content:
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are accepted. Empty files are rejected.",
            )
        if not is_pdf(filename, content):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are accepted. Non-PDF uploads are rejected.",
            )

        invoice_id = str(uuid.uuid4())
        file_hash = hashlib.sha256(content).hexdigest()
        record = store.save_upload(
            invoice_id=invoice_id,
            original_filename=filename,
            content=content,
            file_hash_sha256=file_hash,
        )
        return record

    @app.get("/invoices/{invoice_id}")
    def get_invoice(invoice_id: str) -> dict:
        record = store.get(invoice_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Invoice not found.")
        return record

    return app


app = create_app()
