"""Lightweight structured JSON logging setup used by the backend.

This avoids adding external dependencies but emits a compact JSON object
for each log record so consumers (or systemd/journald) can parse it.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

try:
    from systemd import journal  # type: ignore
    _HAS_JOURNAL = True
except Exception:
    journal = None  # type: ignore
    _HAS_JOURNAL = False


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:  # type: ignore[override]
        payload: dict[str, Any] = {
            "ts": int(time.time()),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }

        # include any extra fields passed via the `extra` parameter
        if hasattr(record, "extra") and isinstance(record.extra, dict):
            payload.update(record.extra)

        # include exception text if present
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=False)


def setup_logging(level: int = logging.INFO) -> None:
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(JsonFormatter())

    # remove other handlers to keep output predictable in tests/runs
    for h in list(root.handlers):
        root.removeHandler(h)

    root.addHandler(handler)

    # If systemd.journal is available, also add a JournalHandler so logs
    # appear in journalctl with the same structured payload.
    if _HAS_JOURNAL:
        try:
            jh = journal.JournalHandler()
            jh.setLevel(level)
            jh.setFormatter(JsonFormatter())
            root.addHandler(jh)
        except Exception:
            # If adding the journal handler fails, keep going with stream.
            root.exception("Failed to attach JournalHandler")
