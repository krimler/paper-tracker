#!/usr/bin/env python3
"""Secondary source: sec-deadlines.github.io (Security & Privacy).

Schema differs from ai-deadlines: entries use `name` and `deadline` is a list of
submission-round timestamps.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import yaml

import sources

REPO_URL = "https://github.com/sec-deadlines/sec-deadlines.github.io.git"


def fetch_rows(wishlist: dict[str, str], already_tracked: set[str]) -> list[dict]:
    """Return rows for wishlist venues present in sec-deadlines but not yet sourced."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "secdl"
        sources.clone(REPO_URL, repo)
        data_path = repo / "_data" / "conferences.yml"
        if not data_path.is_file():
            print(f"warn: secdeadlines: {data_path} missing", file=sys.stderr)
            return []
        data = yaml.safe_load(data_path.read_text()) or []

    rows: list[dict] = []
    seen: set[tuple[str, object]] = set()
    for e in data:
        if not isinstance(e, dict):
            continue
        name = (e.get("name") or "").strip()
        key = name.lower()
        if key not in wishlist or key in already_tracked:
            continue
        dls = e.get("deadline")
        if isinstance(dls, str):
            dls = [dls]
        comment = sources.strip_html(e.get("comment")) or None
        timeline = [
            {"deadline": str(d).strip(), "abstract_deadline": None, "comment": comment}
            for d in (dls or [])
            if sources.parse_iso(d) is not None
        ]
        if not timeline:  # need at least one concrete deadline
            continue
        year = e.get("year")
        if (key, year) in seen:
            continue
        seen.add((key, year))
        rows.append(
            sources.row(
                title=name,
                area=wishlist[key],
                source="secdeadlines",
                year=year,
                description=sources.strip_html(e.get("description")) or None,
                link=e.get("link"),
                place=e.get("place"),
                date=e.get("date"),
                tz=e.get("timezone"),
                dblp=e.get("dblp", ""),
                timeline=timeline,
            )
        )
    return rows
