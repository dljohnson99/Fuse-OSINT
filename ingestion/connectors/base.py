"""
Base connector interface every source connector must implement.

See docs/ingestion.md for the full contract. Keeping this interface small
and stable is what lets Phase 1 -> Phase 5 add new sources without
rewriting the rest of the pipeline (project guide, section 8).
"""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Iterable


@dataclass
class RawRecord:
    """Mirrors docs/data-model.md RawRecord. Immutable once created."""

    source_id: str
    source_type: str  # "news" | "government" | "corporate" | "geospatial" | "dataset"
    raw_content: str
    source_url: str | None = None
    published_at: datetime | None = None
    retrieved_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc)
    )
    content_hash: str = field(init=False)

    def __post_init__(self) -> None:
        self.content_hash = hashlib.sha256(
            self.raw_content.encode("utf-8")
        ).hexdigest()


@dataclass
class ParsedRecord:
    """Source-specific structured record, pre-normalization."""

    raw: RawRecord
    fields: dict[str, Any]


class ValidationError(Exception):
    """Raised by validate() for a record that must not proceed to normalization."""


class BaseConnector(ABC):
    """
    Every connector implements: fetch -> parse -> validate -> normalize -> store.

    Subclasses should NOT override run(); override the five stage methods.
    """

    source_id: str
    source_type: str

    @abstractmethod
    def fetch(self) -> Iterable[str]:
        """Retrieve raw payloads (e.g. article bodies, API response bodies).

        Must be safe to call repeatedly without side effects beyond network
        I/O; deduplication happens downstream via RawRecord.content_hash.
        """
        raise NotImplementedError

    @abstractmethod
    def parse(self, raw: RawRecord) -> ParsedRecord:
        """Turn a raw payload into source-specific structured fields.

        Raise a clear exception on unexpected schema changes rather than
        silently dropping fields.
        """
        raise NotImplementedError

    @abstractmethod
    def validate(self, parsed: ParsedRecord) -> None:
        """Raise ValidationError if the record must not be normalized.

        Should not raise for merely low-confidence data -- only for
        structurally broken records (missing required fields, unparseable
        dates, etc).
        """
        raise NotImplementedError

    @abstractmethod
    def normalize(self, parsed: ParsedRecord) -> dict[str, Any]:
        """Map source-specific fields onto the canonical Document/Entity shape
        described in docs/data-model.md.
        """
        raise NotImplementedError

    @abstractmethod
    def store(self, raw: RawRecord, normalized: dict[str, Any] | None) -> None:
        """Persist the RawRecord unconditionally, and the normalized Document
        if normalization succeeded. Raw preservation must not depend on
        downstream success (docs/ingestion.md).
        """
        raise NotImplementedError

    def run(self) -> None:
        """Drives one full fetch->store cycle. Not meant to be overridden."""
        for payload in self.fetch():
            raw = RawRecord(
                source_id=self.source_id,
                source_type=self.source_type,
                raw_content=payload,
            )
            normalized: dict[str, Any] | None = None
            try:
                parsed = self.parse(raw)
                self.validate(parsed)
                normalized = self.normalize(parsed)
            except ValidationError as exc:
                # Logged, not raised further -- one bad record shouldn't
                # stop the run. Raw content is still stored below.
                print(f"[{self.source_id}] validation failed: {exc}")
            except Exception as exc:  # noqa: BLE001 - connector-level catch-all
                print(f"[{self.source_id}] parse/normalize failed: {exc}")
            finally:
                self.store(raw, normalized)
