#!/usr/bin/env python3
"""Secondary deadline source: paperswithcode/ai-deadlines.

ccfddl (see fetch.py) is the trusted primary source. This module supplements it
for wishlist venues (untracked.yml) that ccfddl does not carry but ai-deadlines
does. It returns rows in the same schema as fetch.flatten(), tagged with
`source="aideadlines"` so consumers can distinguish provenance.

Designed as a pluggable source: a future WikiCFP scraper can expose the same
`fetch_rows(wishlist, already_tracked)` signature and be merged the same way.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_URL = "https://github.com/paperswithcode/ai-deadlines.git"
_TAG_RE = re.compile(r"<[^>]+>")


def _clone(dest: Path) -> None:
    subprocess.run(
        ["git", "clone", "--depth", "1", REPO_URL, str(dest)],
        check=True,
        capture_output=True,
    )


def _strip_html(s: str | None) -> str:
    return _TAG_RE.sub("", s or "").strip()


def _parse_deadline(s) -> datetime | None:
    """Parse ai-deadlines timestamps; return None if unparseable (a sanity gate)."""
    if not s:
        return None
    s = str(s).strip()
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def fetch_rows(
    wishlist: dict[str, str],
    already_tracked: set[str],
    *,
    min_year: int | None = None,
) -> list[dict]:
    """Return supplementary rows for wishlist venues present in ai-deadlines.

    wishlist:        {lowercased_title: area} of venues we want but ccfddl lacks.
    already_tracked: lowercased titles already sourced from ccfddl (skip these).
    min_year:        drop entries older than this year (stale-data guard).
    """
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "aidl"
        _clone(repo)
        data_path = repo / "_data" / "conferences.yml"
        if not data_path.is_file():
            print(f"warn: aideadlines: {data_path} missing", file=sys.stderr)
            return []
        with open(data_path) as f:
            data = yaml.safe_load(f) or []

    rows: list[dict] = []
    seen: set[tuple[str, object]] = set()
    for e in data:
        if not isinstance(e, dict):
            continue
        title = (e.get("title") or "").strip()
        key = title.lower()
        if key not in wishlist or key in already_tracked:
            continue
        # verification gate: a deadline tracker entry must carry a real deadline
        if _parse_deadline(e.get("deadline")) is None:
            continue
        year = e.get("year")
        if min_year and year and int(year) < min_year:
            continue
        dk = (key, year)
        if dk in seen:  # one row per (venue, year)
            continue
        seen.add(dk)
        note = _strip_html(e.get("note"))
        rows.append(
            {
                "title": title,
                "description": note or title,
                "sub": e.get("sub", ""),
                "area": wishlist[key],
                "ccfddl_category": None,
                "ccf": None,
                "core": None,
                "thcpl": None,
                "dblp": "",
                "year": year,
                "id": e.get("id"),
                "link": e.get("link"),
                "timezone": e.get("timezone"),
                "date": e.get("date"),
                "place": e.get("place"),
                "timeline": [
                    {
                        "deadline": str(e["deadline"]) if e.get("deadline") else None,
                        "abstract_deadline": str(e["abstract_deadline"])
                        if e.get("abstract_deadline")
                        else None,
                        "comment": note or None,
                    }
                ],
                "source": "aideadlines",
                "hindex": e.get("hindex"),
            }
        )
    return rows
