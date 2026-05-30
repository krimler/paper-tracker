#!/usr/bin/env python3
"""Manual curated source — venues no feed carries. Reads the committed manual.yml,
so it makes no external call. An entry here is the record and is never re-searched.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

import sources

MANUAL_PATH = Path(__file__).resolve().parent.parent / "manual.yml"


def fetch_rows(wishlist: dict[str, str], already_tracked: set[str]) -> list[dict]:
    """Return rows from manual.yml for venues not already sourced elsewhere."""
    if not MANUAL_PATH.is_file():
        return []
    data = yaml.safe_load(MANUAL_PATH.read_text()) or []

    rows: list[dict] = []
    for e in data:
        if not isinstance(e, dict):
            continue
        title = (e.get("title") or "").strip()
        if not title or title.lower() in already_tracked:
            continue
        deadline = e.get("deadline")
        if not deadline:
            print(f"warn: manual: '{title}' has no deadline, skipped", file=sys.stderr)
            continue
        abstract = e.get("abstract_deadline")
        rows.append(
            sources.row(
                title=title,
                area=e.get("area") or wishlist.get(title.lower(), ""),
                source="manual",
                year=e.get("year"),
                description=e.get("description"),
                link=e.get("link"),
                place=e.get("place"),
                date=e.get("date"),
                tz=e.get("timezone"),
                dblp=e.get("dblp", ""),
                core=e.get("core"),
                ccf=e.get("ccf"),
                timeline=[
                    {
                        "deadline": str(deadline),
                        "abstract_deadline": str(abstract) if abstract else None,
                        "comment": e.get("comment"),
                    }
                ],
            )
        )
    return rows
