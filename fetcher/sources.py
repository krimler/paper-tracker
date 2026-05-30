"""Shared helpers for the secondary deadline sources (see fetch.py)."""
from __future__ import annotations

import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

_TAG_RE = re.compile(r"<[^>]+>")


def clone(repo_url: str, dest: Path) -> None:
    subprocess.run(
        ["git", "clone", "--depth", "1", repo_url, str(dest)],
        check=True,
        capture_output=True,
    )


def strip_html(s: str | None) -> str:
    return _TAG_RE.sub("", s or "").strip()


def parse_iso(s) -> datetime | None:
    """Parse an ISO-ish timestamp; None if unparseable or a rolling template."""
    if not s:
        return None
    s = str(s).strip()
    if "%" in s:  # rolling templates like "%y-%m-15 23:59"
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def row(
    *,
    title: str,
    area: str,
    source: str,
    timeline: list[dict],
    year=None,
    description: str | None = None,
    link=None,
    place=None,
    date=None,
    tz=None,
    sub: str = "",
    dblp: str = "",
    core=None,
    ccf=None,
    conf_id=None,
) -> dict:
    """Build a conference row matching the schema fetch.flatten() emits."""
    return {
        "title": title,
        "description": description or title,
        "sub": sub,
        "area": area,
        "ccfddl_category": None,
        "ccf": ccf,
        "core": core,
        "thcpl": None,
        "dblp": dblp,
        "year": year,
        "id": conf_id,
        "link": link,
        "timezone": tz,
        "date": date,
        "place": place,
        "timeline": timeline,
        "source": source,
    }
