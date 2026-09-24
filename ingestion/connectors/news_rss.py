import json
import feedparser

from ingestion.connectors.base import BaseConnector, ParsedRecord, ValidationError
from ingestion.connectors.config import NEWS_FEEDS
from dateutil import parser as date_parser
from pathlib import Path

RAW_DIR = Path("raw") / "news"

class NewsRSSConnector(BaseConnector):
    source_type = "news"

    def fetch(self):
        for feed in NEWS_FEEDS:
            source_id = feed["source_id"]
            feed_url = feed["feed_url"]

            parsed_feed = feedparser.parse(feed_url)

            for entry in parsed_feed.entries:
                record = {
                    "title": entry.get("title"),
                    "link": entry.get("link"),
                    "summary": entry.get("summary"),
                    "published": entry.get("published"),
                    "author": entry.get("author", None),
                    "guid": entry.get("id"), # Feedparser normalized guid to id
                }
                yield source_id, json.dumps(record)

    def parse(self, raw):
        fields = json.loads(raw.raw_content)
        return ParsedRecord(raw=raw, fields=fields)

    def validate(self, parsed):
        fields = parsed.fields

        if not fields.get("title"):
            raise ValidationError("Missing Title")

        if not fields.get("link"):
            raise ValidationError("Missing Link")

    def normalize(self, parsed):
        fields = parsed.fields

        published_date = None
        if fields.get("published"):
            try:
                published_date = date_parser.parse(fields["published"]).date()
            except (ValueError, TypeError):
                published_date = None

        return {
            "source": parsed.raw.source_id,
            "title": fields.get("title"),
            "author": fields.get("author"),
            "published_date": published_date,
            "retrieved_date": parsed.raw.retrieved_at.date(),
            "text": fields.get("summary"),
            "url": fields.get("link"),
        }

    def store(self, raw, normalized):
        RAW_DIR.mkdir(parents=True, exist_ok=True)

        raw_path = RAW_DIR / f"{raw.content_hash}.raw.json"

        if raw_path.exists():
            return  # already ingested — dedup via content hash

        raw_payload = {
            "source_id": raw.source_id,
            "source_type": raw.source_type,
            "retrieved_at": raw.retrieved_at.isoformat(),
            "content_hash": raw.content_hash,
            "raw_content": raw.raw_content,
        }
        raw_path.write_text(json.dumps(raw_payload, indent=2))

        if normalized is not None:
            norm_path = RAW_DIR / f"{raw.content_hash}.normalized.json"
            norm_path.write_text(json.dumps(normalized, default=str, indent=2))