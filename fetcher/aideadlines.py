#!/usr/bin/env python3
"""Secondary source: paperswithcode/ai-deadlines (AI / ML). YAML, schema close to ccfddl."""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import yaml

import sources

REPO_URL = "https://github.com/paperswithcode/ai-deadlines.git"


def fetch_rows(wishlist: dict[str, str], already_tracked: set[str]) -> list[dict]:
    """Return rows for wishlist venues present in ai-deadlines but not yet sourced."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "aidl"
        sources.clone(REPO_URL, repo)
        data_path = repo / "_data" / "conferences.yml"
        if not data_path.is_file():
            print(f"warn: aideadlines: {data_path} missing", file=sys.stderr)
            return []
        data = yaml.safe_load(data_path.read_text()) or []

    rows: list[dict] = []
    seen: set[tuple[str, object]] = set()
    for e in data:
        if not isinstance(e, dict):
            continue
        title = (e.get("title") or "").strip()
        key = title.lower()
        if key not in wishlist or key in already_tracked:
            continue
        if sources.parse_iso(e.get("deadline")) is None:  # need a real deadline
            continue
        year = e.get("year")
        if (key, year) in seen:
            continue
        seen.add((key, year))
        note = sources.strip_html(e.get("note")) or None
        abstract = e.get("abstract_deadline")
        rows.append(
            sources.row(
                title=title,
                area=wishlist[key],
                source="aideadlines",
                year=year,
                description=note,
                link=e.get("link"),
                place=e.get("place"),
                date=e.get("date"),
                tz=e.get("timezone"),
                sub=e.get("sub", ""),
                conf_id=e.get("id"),
                timeline=[
                    {
                        "deadline": str(e["deadline"]),
                        "abstract_deadline": str(abstract) if abstract else None,
                        "comment": note,
                    }
                ],
            )
        )
    return rows
