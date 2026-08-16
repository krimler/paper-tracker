#!/usr/bin/env python3
"""Generate static RSS (feed.xml) and iCal (deadlines.ics) from the data snapshot.

Runs after the daily fetcher and writes both files to the repo root so GitHub
Pages serves them at:
    https://krimler.github.io/paper-tracker/feed.xml
    https://krimler.github.io/paper-tracker/deadlines.ics

Stdlib only (no third-party deps) so it is cheap to run in CI. Deadlines are
treated as UTC, matching the directory page (index.html reads them the same way).
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "conferences.json"
RSS_PATH = ROOT / "feed.xml"
ICS_PATH = ROOT / "deadlines.ics"

SITE = "https://krimler.github.io/paper-tracker/"
TITLE = "Lucid Research — CS conference deadlines"
DESC = "Upcoming submission deadlines for top CS conferences, refreshed daily."

# How many upcoming deadlines to publish. Keeps the feed focused on what is
# actionable rather than the full multi-year history.
MAX_ITEMS = 200

AREA_LABELS = {
    "theory": "Theory", "security": "Security",
    "distributed_systems": "Distributed Sys", "networking": "Networking",
    "systems": "Systems", "databases": "Databases",
    "software_engineering": "SE / PL", "ai_ml": "AI / ML",
    "biomedical": "Biomedical",
}

# Try the shapes the snapshot actually contains, then a couple of ISO fallbacks.
_DT_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d")


def parse_dt(value) -> datetime | None:
    if not value:
        return None
    s = str(value).strip().replace("Z", "")
    for fmt in _DT_FORMATS:
        try:
            return datetime.strptime(s, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def fmt_year(year) -> str:
    try:
        return str(int(year))
    except (TypeError, ValueError):
        return ""


def collect_deadlines(data: dict, now: datetime) -> list[dict]:
    """One entry per upcoming (conference, deadline-kind), sorted soonest first."""
    out: list[dict] = []
    for conf in data.get("conferences", []):
        year = fmt_year(conf.get("year"))
        title = conf.get("title", "?")
        for i, t in enumerate(conf.get("timeline") or []):
            for kind, key in (("Abstract", "abstract_deadline"),
                              ("Submission", "deadline")):
                dt = parse_dt(t.get(key))
                if dt is None or dt < now:
                    continue
                out.append({
                    "dt": dt,
                    "kind": kind,
                    "title": title,
                    "year": year,
                    "area": AREA_LABELS.get(conf.get("area"), conf.get("area") or ""),
                    "core": conf.get("core") or "N",
                    "place": conf.get("place") or "",
                    "link": conf.get("link") or SITE,
                    "description": conf.get("description") or title,
                    "comment": t.get("comment") or "",
                    "uid": f"{title}-{year}-{kind.lower()}-{i}".replace(" ", "_"),
                })
    out.sort(key=lambda r: r["dt"])
    return out[:MAX_ITEMS]


def rfc822(dt: datetime) -> str:
    return dt.strftime("%a, %d %b %Y %H:%M:%S +0000")


def build_rss(items: list[dict], built: datetime) -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        f"<title>{xml_escape(TITLE)}</title>",
        f"<link>{SITE}</link>",
        f"<description>{xml_escape(DESC)}</description>",
        "<language>en-us</language>",
        f"<lastBuildDate>{rfc822(built)}</lastBuildDate>",
        f'<atom:link href="{SITE}feed.xml" rel="self" type="application/rss+xml" />',
    ]
    for it in items:
        when = it["dt"].strftime("%Y-%m-%d %H:%M UTC")
        item_title = f"{it['title']} {it['year']} — {it['kind']} deadline {when}"
        bits = [f"{it['area']} · CORE {it['core']}"]
        if it["place"]:
            bits.append(it["place"])
        if it["comment"]:
            bits.append(it["comment"])
        body = it["description"] + " — " + " · ".join(bits)
        parts += [
            "<item>",
            f"<title>{xml_escape(item_title)}</title>",
            f"<link>{xml_escape(it['link'])}</link>",
            f'<guid isPermaLink="false">{xml_escape(it["uid"])}</guid>',
            f"<pubDate>{rfc822(built)}</pubDate>",
            f"<description>{xml_escape(body)}</description>",
            "</item>",
        ]
    parts += ["</channel>", "</rss>"]
    return "\n".join(parts)


def _ics_escape(s) -> str:
    return (str(s or "").replace("\\", "\\\\").replace(",", "\\,")
            .replace(";", "\\;").replace("\n", "\\n"))


def build_ics(items: list[dict], built: datetime) -> str:
    stamp = built.strftime("%Y%m%dT%H%M%SZ")
    lines = [
        "BEGIN:VCALENDAR", "VERSION:2.0",
        "PRODID:-//Lucid Research//Conference Deadlines//EN",
        "CALSCALE:GREGORIAN", "METHOD:PUBLISH",
        "X-WR-CALNAME:CS Conference Deadlines",
        "X-WR-CALDESC:Upcoming CS conference submission deadlines (Lucid Research)",
        "REFRESH-INTERVAL;VALUE=DURATION:P1D",
        "X-PUBLISHED-TTL:P1D",
    ]
    for it in items:
        dt = it["dt"].strftime("%Y%m%dT%H%M%SZ")
        summary = f"{it['title']} {it['year']} — {it['kind']} deadline"
        desc = f"{it['description']} ({it['area']}, CORE {it['core']})"
        if it["comment"]:
            desc += f" — {it['comment']}"
        lines += [
            "BEGIN:VEVENT",
            f"UID:{it['uid']}@lucid-research",
            f"DTSTAMP:{stamp}",
            f"DTSTART:{dt}",
            f"DTEND:{dt}",
            f"SUMMARY:{_ics_escape(summary)}",
            f"DESCRIPTION:{_ics_escape(desc)}",
            f"URL:{_ics_escape(it['link'])}",
        ]
        if it["place"]:
            lines.append(f"LOCATION:{_ics_escape(it['place'])}")
        # Two reminders: a week out and a day out.
        for trig, label in (("-P7D", "7 days"), ("-P1D", "1 day")):
            lines += [
                "BEGIN:VALARM", "ACTION:DISPLAY",
                f"TRIGGER:{trig}",
                f"DESCRIPTION:{_ics_escape(summary + f' in {label}')}",
                "END:VALARM",
            ]
        lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def main() -> int:
    with open(DATA_PATH) as f:
        data = json.load(f)
    built = datetime.now(timezone.utc)
    items = collect_deadlines(data, built)

    RSS_PATH.write_text(build_rss(items, built), encoding="utf-8")
    ICS_PATH.write_text(build_ics(items, built), encoding="utf-8")
    print(f"wrote {RSS_PATH.name} and {ICS_PATH.name} ({len(items)} upcoming deadlines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
