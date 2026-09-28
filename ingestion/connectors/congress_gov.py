import json
import os

import httpx
from dotenv import load_dotenv

from ingestion.connectors.base import BaseConnector, ParsedRecord, ValidationError
from ingestion.connectors.config import CONGRESS_CONFIG


class CongressGovConnector(BaseConnector):
    source_type = "government"

    def fetch(self):
        load_dotenv()
        key = os.getenv("CONGRESS_API_KEY")
        if not key:
            raise RuntimeError("Congress API key is not set")

        cfg = CONGRESS_CONFIG
        collected = 0
        offset = 0

        while collected < cfg["max_bills"]:
            try:
                resp = httpx.get(
                    f"{cfg['base_url']}/bill/{cfg['congress']}",
                    params={
                        "api_key": key,
                        "format": "json",
                        "limit": cfg["page_size"],
                        "offset": offset,
                        "sort": cfg["sort"],
                    },
                    timeout=30,
                )
            except httpx.HTTPError as exc:
                print(f"[{cfg['source_id']}] list request failed: {type(exc).__name__}")
                break
            if resp.status_code != 200:
                print(f"[{cfg['source_id']}] list request failed: HTTP {resp.status_code}")
                break

            bills = resp.json()["bills"][: cfg["max_bills"] - collected]
            if not bills:
                break

            for item in bills:
                collected += 1
                detail = self._get_detail(item["url"], key)
                if detail is None:
                    continue
                yield cfg["source_id"], json.dumps(self._build_record(detail, item["url"]))

            offset += cfg["page_size"]
    
    def detail(self, url, key):
        ...  # you write this one, see below

    def parse(self, raw):
        fields = json.loads(raw.raw_content)
        return ParsedRecord(raw=raw, fields=fields)

    def validate(self, parsed):
        fields = parsed.fields
        for name in ("congress", "bill_type", "bill_number", "title", "source_url"):
            if not fields.get(name):
                raise ValidationError(f"Missing {name}")

    def normalize(self, parsed):
        raise NotImplementedError

    def store(self, raw, normalized):
        raise NotImplementedError

    def _build_record(self, detail, source_url):
    sponsors = [
        {
            "bioguide_id": s.get("bioguideId"),
            "full_name": s.get("fullName"),
            "party": s.get("party"),
            "state": s.get("state"),
            "district": s.get("district"),
        }
        for s in detail.get("sponsors", [])
    ]
    latest = detail.get("latestAction") or {}
    policy = detail.get("policyArea") or {}

    return {
        "source_url": source_url,
        "congress": detail.get("congress"),
        "bill_type": detail.get("type"),
        "bill_number": detail.get("number"),
        "title": detail.get("title"),
        "introduced_date": detail.get("introducedDate"),
        "update_date": detail.get("updateDate"),
        "latest_action_date": latest.get("actionDate"),
        "latest_action_text": latest.get("text"),
        "policy_area": policy.get("name"),
        "sponsors": sponsors,
    }