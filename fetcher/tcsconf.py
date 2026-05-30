#!/usr/bin/env python3
"""Secondary source: tcs-conf.github.io (Theory / TCS), e.g. DISC.

Deadlines live in a hand-curated HTML table (index.html), not YAML, so this
adapter parses the table and normalizes free-form dates like "27 May / 1 June
2026" (multiple rounds, month/year carried right-to-left). All deadlines are
23:59 AoE (UTC-12) per the site convention.
"""
from __future__ import annotations

import re
import sys
import tempfile
from datetime import datetime
from pathlib import Path

import sources

REPO_URL = "https://github.com/tcs-conf/tcs-conf.github.io.git"

_MONTHS = {
    m: i
    for i, m in enumerate(
        [
            "january", "february", "march", "april", "may", "june",
            "july", "august", "september", "october", "november", "december",
        ],
        start=1,
    )
}

_ROW_RE = re.compile(r"<tr>(.*?)</tr>", re.S)
_NAME_RE = re.compile(r'class="confname"><a href="([^"]*)"[^>]*>([^<]+)</a>', re.S)
_TIP_RE = re.compile(r'class="tooltiptext">([^<]+)<')
_DL_RE = re.compile(r'class="(?:now-)?deadline">([^<]*)<')
_LOC_RE = re.compile(r'class="location">([^<]*)<')
_DATE_RE = re.compile(r'class="date">([^<]*)<')


def _month_num(tok: str) -> int | None:
    t = tok.strip().lower()
    if t in _MONTHS:
        return _MONTHS[t]
    for name, num in _MONTHS.items():  # 3-letter abbreviations (Sep, Jun, ...)
        if len(t) >= 3 and name.startswith(t[:3]):
            return num
    return None


def parse_deadline_cell(cell: str) -> list[str]:
    """Parse a deadline cell into ISO 'YYYY-MM-DD 23:59:00' strings.

    Handles "31 May 2026", "20/31 May 2026" (shared month/year) and
    "27 May / 1 June 2026" (shared year). Month/year are carried right-to-left
    from the most-complete (rightmost) token. Returns [] if unparseable.
    """
    cell = re.sub(r"\s+", " ", cell or "").strip()
    if not cell:
        return []
    year: int | None = None
    month: int | None = None
    parsed: list[tuple[int, int, int]] = []
    for part in reversed([p.strip() for p in cell.split("/")]):
        toks = part.split()
        if not toks:
            return []
        digits = re.sub(r"\D", "", toks[0])
        if not digits:
            return []
        day = int(digits)
        if len(toks) >= 2:
            mn = _month_num(toks[1])
            if mn:
                month = mn
        if len(toks) >= 3 and toks[2].isdigit():
            year = int(toks[2])
        if month is None or year is None:  # nothing to carry from — give up
            return []
        parsed.append((year, month, day))
    out: list[str] = []
    for y, m, d in reversed(parsed):
        try:
            datetime(y, m, d)
        except ValueError:
            continue
        out.append(f"{y:04d}-{m:02d}-{d:02d} 23:59:00")
    return out


def fetch_rows(wishlist: dict[str, str], already_tracked: set[str]) -> list[dict]:
    """Return rows for wishlist venues present in the tcs-conf deadline table."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "tcsconf"
        sources.clone(REPO_URL, repo)
        index = repo / "index.html"
        if not index.is_file():
            print(f"warn: tcsconf: {index} missing", file=sys.stderr)
            return []
        html = index.read_text(encoding="utf-8", errors="replace")

    rows: list[dict] = []
    seen: set[tuple[str, int]] = set()
    for m in _ROW_RE.finditer(html):
        block = m.group(1)
        nm = _NAME_RE.search(block)
        if not nm:
            continue
        link, name = nm.group(1).strip(), nm.group(2).strip()
        key = name.lower()
        if key not in wishlist or key in already_tracked:
            continue
        dlm = _DL_RE.search(block)
        if not dlm:
            continue
        dls = parse_deadline_cell(dlm.group(1))
        if not dls:  # need at least one concrete deadline
            continue
        year = int(dls[0][:4])
        if (key, year) in seen:
            continue
        seen.add((key, year))
        tip = _TIP_RE.search(block)
        loc = _LOC_RE.search(block)
        date = _DATE_RE.search(block)
        rows.append(
            sources.row(
                title=name,
                area=wishlist[key],
                source="tcsconf",
                year=year,
                description=tip.group(1).strip() if tip else None,
                link=link,
                place=loc.group(1).strip() if loc else None,
                date=date.group(1).strip() if date else None,
                tz="UTC-12",
                timeline=[
                    {"deadline": d, "abstract_deadline": None, "comment": None}
                    for d in dls
                ],
            )
        )
    return rows
