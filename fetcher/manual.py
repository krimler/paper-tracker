#!/usr/bin/env python3
"""Manual curated deadline source — for venues no structured feed carries.

Reads manual.yml, which is committed to the repo. The GitHub Action makes NO
external call for these entries, so it can never be rate-limited or denied.

This file IS the record: once a venue's deadline is entered here it is "found"
and nothing re-searches it. Update an entry once a year when the next CFP drops.
"""
from __future__ import annotations

import sys
from pathlib import Path

import yaml

MANUAL_PATH = Path(__file__).resolve().parent.parent / "manual.yml"


def fetch_rows(
    wishlist: dict[str, str],
    already_tracked: set[str],
    *,
    min_year: int | None = None,
) -> list[dict]:
    """Return rows from manual.yml for venues not already sourced elsewhere."""
    if not MANUAL_PATH.is_file():
        return []
    with open(MANUAL_PATH) as f:
        data = yaml.safe_load(f) or []

    rows: list[dict] = []
    for e in data:
        if not isinstance(e, dict):
            continue
        title = (e.get("title") or "").strip()
        if not title or title.lower() in already_tracked:
            continue
        deadline = e.get("deadline")
        if not deadline:  # a deadline tracker entry must carry a deadline
            print(f"warn: manual: '{title}' has no deadline, skipped", file=sys.stderr)
            continue
        year = e.get("year")
        if min_year and year and int(year) < min_year:
            continue
        area = e.get("area") or wishlist.get(title.lower(), "")
        rows.append(
            {
                "title": title,
                "description": e.get("description") or title,
                "sub": "",
                "area": area,
                "ccfddl_category": None,
                "ccf": e.get("ccf"),
                "core": e.get("core"),
                "thcpl": None,
                "dblp": e.get("dblp", ""),
                "year": year,
                "id": None,
                "link": e.get("link"),
                "timezone": e.get("timezone"),
                "date": e.get("date"),
                "place": e.get("place"),
                "timeline": [
                    {
                        "deadline": str(deadline),
                        "abstract_deadline": str(e["abstract_deadline"])
                        if e.get("abstract_deadline")
                        else None,
                        "comment": e.get("comment"),
                    }
                ],
                "source": "manual",
                "hindex": None,
            }
        )
    return rows
