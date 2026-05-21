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

REPO_URL = "https://github.com/ccfddl/ccf-deadlines.git"
ROOT = Path(__file__).resolve().parent.parent
ALLOWLIST_PATH = ROOT / "allowlist.yml"
OUT_PATH = ROOT / "data" / "conferences.json"


def load_allowlist() -> dict[str, str]:
    """Return {lowercased_title: area} from allowlist.yml."""
    with open(ALLOWLIST_PATH) as f:
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
            }
        )
    return rows


def main() -> int:
    allow = load_allowlist()
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

    payload = {
        "fetched_at": datetime.now(timezone.utc).isoformat(),
        "source": "https://github.com/ccfddl/ccf-deadlines",
        "matched": len(matched_titles),
        "unmatched": unmatched,
        "row_count": len(rows),
        "conferences": rows,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"wrote {OUT_PATH} ({len(rows)} rows, {len(matched_titles)} confs)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
