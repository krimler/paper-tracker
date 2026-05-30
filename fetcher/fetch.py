#!/usr/bin/env python3
"""Fetch ccfddl conference deadlines, filter by allowlist, write JSON."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

import aideadlines
import manual
import secdeadlines
import tcsconf

# Secondary sources tried after ccfddl, in order. Each reads a git clone or a
# committed file (no web search) and exposes fetch_rows(wishlist, already_tracked).
# `manual` runs last, filling only what no structured feed resolved.
SECONDARY_SOURCES = [
    ("aideadlines", aideadlines),
    ("secdeadlines", secdeadlines),
    ("tcsconf", tcsconf),
    ("manual", manual),
]

REPO_URL = "https://github.com/ccfddl/ccf-deadlines.git"
ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_PATH = ROOT / "allowlist.yml"
UNTRACKED_PATH = ROOT / "untracked.yml"
OUT_PATH = ROOT / "data" / "conferences.json"


def load_yaml_mapping(path: Path) -> dict[str, str]:
    """Return {lowercased_title: area} from an allowlist-style YAML file."""
    if not path.is_file():
        return {}
    with open(path) as f:
        doc = yaml.safe_load(f) or {}
    mapping: dict[str, str] = {}
    for area, titles in doc.items():
        for t in titles or []:
            mapping[t.strip().lower()] = area
    return mapping


def clone_repo(dest: Path) -> None:
    subprocess.run(
        ["git", "clone", "--depth", "1", REPO_URL, str(dest)],
        check=True,
        capture_output=True,
    )


def parse_yaml_file(path: Path) -> dict | None:
    with open(path) as f:
        try:
            doc = yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"warn: skip {path.name}: {e}", file=sys.stderr)
            return None
    if isinstance(doc, list):
        if not doc:
            return None
        doc = doc[0]
    if not isinstance(doc, dict):
        return None
    return doc


def flatten(entry: dict, area: str, ccfddl_category: str) -> list[dict]:
    """One row per (conference, year)."""
    title = entry.get("title", "?")
    desc = entry.get("description", "")
    sub = entry.get("sub", "")
    rank = entry.get("rank") or {}
    dblp = entry.get("dblp", "")
    rows = []
    for conf in entry.get("confs") or []:
        timeline = []
        for t in conf.get("timeline") or []:
            timeline.append(
                {
                    "deadline": str(t.get("deadline")) if t.get("deadline") else None,
                    "abstract_deadline": str(t.get("abstract_deadline"))
                    if t.get("abstract_deadline")
                    else None,
                    "comment": t.get("comment"),
                }
            )
        rows.append(
            {
                "title": title,
                "description": desc,
                "sub": sub,
                "area": area,
                "ccfddl_category": ccfddl_category,
                "ccf": rank.get("ccf"),
                "core": rank.get("core"),
                "thcpl": rank.get("thcpl"),
                "dblp": dblp,
                "year": conf.get("year"),
                "id": conf.get("id"),
                "link": conf.get("link"),
                "timezone": conf.get("timezone"),
                "date": conf.get("date"),
                "place": conf.get("place"),
                "timeline": timeline,
                "source": "ccfddl",
            }
        )
    return rows


def main() -> int:
    allow = load_yaml_mapping(ALLOWLIST_PATH)
    print(f"allowlist: {len(allow)} conferences across {len(set(allow.values()))} areas")

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    matched_titles: set[str] = set()

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "ccfddl"
        clone_repo(repo)
        conf_dir = repo / "conference"
        if not conf_dir.is_dir():
            print(f"error: {conf_dir} not found", file=sys.stderr)
            return 1
        for cat_dir in sorted(conf_dir.iterdir()):
            if not cat_dir.is_dir():
                continue
            for yml in sorted(cat_dir.rglob("*.yml")):
                entry = parse_yaml_file(yml)
                if not entry:
                    continue
                title = (entry.get("title") or "").strip().lower()
                if title not in allow:
                    continue
                rows.extend(flatten(entry, allow[title], cat_dir.name))
                matched_titles.add(title)

    unmatched = sorted(set(allow) - matched_titles)
    if unmatched:
        print(
            f"warn: {len(unmatched)} allowlist titles unmatched in ccfddl:",
            file=sys.stderr,
        )
        for t in unmatched:
            print(f"  - {t}", file=sys.stderr)

    # Secondary sources: supplement wishlist venues ccfddl does not carry.
    # A source failure must never sink the trusted primary result, so we guard
    # each one. `resolved` grows as venues are found, so later sources skip what
    # earlier ones already supplied (each venue is recorded once per run).
    wishlist = load_yaml_mapping(UNTRACKED_PATH)
    resolved = {t.lower() for t in matched_titles}
    supplemented: dict[str, str] = {}  # title -> source that resolved it
    if wishlist:
        for sname, mod in SECONDARY_SOURCES:
            try:
                extra = mod.fetch_rows(wishlist, resolved)
            except Exception as e:  # network/parse failure — keep prior data
                print(f"warn: {sname} source failed: {e}", file=sys.stderr)
                continue
            if not extra:
                continue
            rows.extend(extra)
            found = sorted({r["title"] for r in extra})
            for t in found:
                supplemented.setdefault(t, sname)
                resolved.add(t.lower())
            print(f"{sname}: +{len(extra)} rows across {len(found)} wishlist venues")

    still_untracked = sorted(t for t in wishlist if t not in resolved)

    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "sources": [
            "https://github.com/ccfddl/ccf-deadlines",
            "https://github.com/paperswithcode/ai-deadlines",
            "https://github.com/sec-deadlines/sec-deadlines.github.io",
            "https://github.com/tcs-conf/tcs-conf.github.io",
            "manual.yml",
        ],
        "matched": len(matched_titles),
        "unmatched": unmatched,
        "supplemented": supplemented,
        "still_untracked": still_untracked,
        "row_count": len(rows),
        "conferences": rows,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(
        f"wrote {OUT_PATH} ({len(rows)} rows, "
        f"{len(matched_titles) + len(supplemented)} confs, "
        f"{len(still_untracked)} wishlist venues still unsourced)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
