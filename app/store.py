"""Persistent invoice file and metadata storage."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.statuses import ALL_STATUSES, UPLOADED, empty_status_timestamps

SCHEMA = """
CREATE TABLE IF NOT EXISTS invoices (
    id TEXT PRIMARY KEY,
    original_filename TEXT NOT NULL,
    stored_filename TEXT NOT NULL,
    file_hash_sha256 TEXT NOT NULL,
    uploaded_at TEXT NOT NULL,
    current_status TEXT NOT NULL,
    status_timestamps TEXT NOT NULL,
    finalized_at TEXT
);
"""


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


class InvoiceStore:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.uploads_dir = self.data_dir / "uploads"
        self.db_path = self.data_dir / "invoices.sqlite"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.execute(SCHEMA)

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def save_upload(
        self,
        invoice_id: str,
        original_filename: str,
        content: bytes,
        file_hash_sha256: str,
    ) -> dict[str, Any]:
        stored_filename = f"{invoice_id}.pdf"
        stored_path = self.uploads_dir / stored_filename
        stored_path.write_bytes(content)

        uploaded_at = utc_now_iso()
        timestamps = empty_status_timestamps()
        timestamps[UPLOADED] = uploaded_at

        record = {
            "id": invoice_id,
            "original_filename": original_filename,
            "stored_filename": stored_filename,
            "file_hash_sha256": file_hash_sha256,
            "uploaded_at": uploaded_at,
            "current_status": UPLOADED,
            "status_timestamps": timestamps,
            "finalized_at": None,
        }

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO invoices (
                    id, original_filename, stored_filename, file_hash_sha256,
                    uploaded_at, current_status, status_timestamps, finalized_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record["id"],
                    record["original_filename"],
                    record["stored_filename"],
                    record["file_hash_sha256"],
                    record["uploaded_at"],
                    record["current_status"],
                    json.dumps(record["status_timestamps"]),
                    record["finalized_at"],
                ),
            )
            conn.commit()
        return record

    def get(self, invoice_id: str) -> dict[str, Any] | None:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM invoices WHERE id = ?", (invoice_id,)
            ).fetchone()
        if row is None:
            return None
        return self._row_to_record(row)

    def count(self) -> int:
        with self._connect() as conn:
            (n,) = conn.execute("SELECT COUNT(*) FROM invoices").fetchone()
        return int(n)

    def _row_to_record(self, row: sqlite3.Row) -> dict[str, Any]:
        timestamps = json.loads(row["status_timestamps"])
        for status in ALL_STATUSES:
            timestamps.setdefault(status, None)
        return {
            "id": row["id"],
            "original_filename": row["original_filename"],
            "stored_filename": row["stored_filename"],
            "file_hash_sha256": row["file_hash_sha256"],
            "uploaded_at": row["uploaded_at"],
            "current_status": row["current_status"],
            "status_timestamps": timestamps,
            "finalized_at": row["finalized_at"],
        }

    def stored_pdf_path(self, stored_filename: str) -> Path:
        return self.uploads_dir / stored_filename
