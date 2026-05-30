#!/usr/bin/env python3
"""Secondary deadline source: sec-deadlines.github.io (Security & Privacy).

Same role as aideadlines.py but a different schema: entries use `name` (not
`title`) and `deadline` is a *list* of submission-round timestamps. CI-safe —
a plain `git clone`, no web search, so a GitHub Action cannot be rate-limited.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

REPO_URL = "https://github.com/sec-deadlines/sec-deadlines.github.io.git"

# Source spelling -> our untracked.yml wishlist key, for the rare case a feed
# abbreviates a venue differently than our wishlist. Empty today; add entries
# here if a sec-deadlines `name` needs remapping.
ALIASES: dict[str, str] = {}

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
    """Parse a timestamp; return None for unparseable or rolling-template dates."""
    if not s:
        return None
    s = str(s).strip()
    if "%" in s:  # rolling templates like "%y-%m-15 23:59" — not a concrete date
        return None
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
    """Return supplementary rows for wishlist venues present in sec-deadlines."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "secdl"
        _clone(repo)
        data_path = repo / "_data" / "conferences.yml"
        if not data_path.is_file():
            print(f"warn: secdeadlines: {data_path} missing", file=sys.stderr)
            return []
        with open(data_path) as f:
            data = yaml.safe_load(f) or []

    rows: list[dict] = []
    seen: set[tuple[str, object]] = set()
    for e in data:
        if not isinstance(e, dict):
            continue
        name = (e.get("name") or "").strip()
        key = ALIASES.get(name.lower(), name.lower())
        if key not in wishlist or key in already_tracked:
            continue
        dls = e.get("deadline")
        if isinstance(dls, str):
            dls = [dls]
        comment = _strip_html(e.get("comment")) or None
        timeline = [
            {"deadline": str(d).strip(), "abstract_deadline": None, "comment": comment}
            for d in (dls or [])
            if _parse_deadline(d) is not None
        ]
        if not timeline:  # verification gate: need at least one concrete deadline
            continue
        year = e.get("year")
        if min_year and year and int(year) < min_year:
            continue
        dk = (key, year)
        if dk in seen:
            continue
        seen.add(dk)
        rows.append(
            {
                "title": name,
                "description": _strip_html(e.get("description")) or name,
                "sub": "",
                "area": wishlist[key],
                "ccfddl_category": None,
                "ccf": None,
                "core": None,
                "thcpl": None,
                "dblp": e.get("dblp", ""),
                "year": year,
                "id": None,
                "link": e.get("link"),
                "timezone": e.get("timezone"),
                "date": e.get("date"),
                "place": e.get("place"),
                "timeline": timeline,
                "source": "secdeadlines",
                "hindex": None,
            }
        )
    return rows
