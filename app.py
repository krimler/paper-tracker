"""Lucid Research — CS Conference Deadlines dashboard."""
from __future__ import annotations

import base64
import json
from pathlib import Path
from urllib.parse import quote

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

DATA_PATH = Path(__file__).parent / "data" / "conferences.json"
LOGO_PATH = Path(__file__).parent / "assets" / "logo.jpg"


@st.cache_data
def logo_data_uri() -> str:
    if not LOGO_PATH.is_file():
        return ""
    b = LOGO_PATH.read_bytes()
    mime = "image/jpeg" if LOGO_PATH.suffix.lower() in (".jpg", ".jpeg") else "image/png"
    return f"data:{mime};base64,{base64.b64encode(b).decode()}"

AREA_LABELS = {
    "theory": "Theory",
    "security": "Security",
    "distributed_systems": "Distributed Sys",
    "networking": "Networking",
    "systems": "Systems",
    "databases": "Databases",
    "software_engineering": "SE / PL",
    "ai_ml": "AI / ML",
    "biomedical": "Biomedical",
}

AREA_COLORS = {
    "theory":               "#8B5CF6",
    "security":             "#EF4444",
    "distributed_systems":  "#F59E0B",
    "networking":           "#06B6D4",
    "systems":              "#10B981",
    "databases":            "#3B82F6",
    "software_engineering": "#EC4899",
    "ai_ml":                "#A855F7",
    "biomedical":           "#14B8A6",
}

CORE_BADGE = {
    "A*": ("#FCD34D", "#78350F"),
    "A":  ("#86EFAC", "#14532D"),
    "B":  ("#93C5FD", "#1E3A8A"),
    "C":  ("#D1D5DB", "#374151"),
    "N":  ("#F3F4F6", "#9CA3AF"),
}

CCF_BADGE = {
    "A": ("#FCA5A5", "#7F1D1D"),
    "B": ("#FCD34D", "#78350F"),
    "C": ("#A5F3FC", "#155E75"),
    "N": ("#F3F4F6", "#9CA3AF"),
}

CORE_ORDER = {"A*": 0, "A": 1, "B": 2, "C": 3, "N": 4}

CUSTOM_CSS = """
<style>
/* hide Streamlit's top toolbar/decoration so the header isn't cropped under it */
header[data-testid="stHeader"] { display: none; }
[data-testid="stDecoration"] { display: none; }

[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #FAF5FF 0%, #FFFFFF 40%);
}
section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, #F5F3FF, #FFFFFF);
}
.block-container { padding-top: 2.2rem; padding-bottom: 1rem; max-width: 100% !important; }

/* compact inline metrics next to the header */
.stat-row { display:flex; gap:0.5rem; justify-content:flex-end; flex-wrap:wrap; align-items:center; height:100%; }
.stat-box { text-align:center; padding:0.35rem 0.8rem; border-radius:12px;
    background:#F5F3FF; border:1px solid #EDE9FE; }
.stat-box b { display:block; font-size:1.35rem; font-weight:800; color:#7C3AED; line-height:1; }
.stat-box span { font-size:0.62rem; color:#6B7280; text-transform:uppercase; letter-spacing:0.05em; font-weight:700; }

.lucid-header { display: flex; align-items: center; gap: 1rem; }
.lucid-logo {
    width: 72px; height: 72px; border-radius: 16px;
    box-shadow: 0 8px 22px -10px rgba(67, 56, 202, 0.55);
    object-fit: cover; flex-shrink: 0;
}
.lucid-title {
    font-size: 2.1rem; font-weight: 900; letter-spacing: -0.04em;
    background: linear-gradient(120deg, #7C3AED 0%, #EC4899 50%, #F59E0B 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    line-height: 1; margin: 0;
}
.lucid-sub { color: #6B7280; font-size: 0.95rem; margin-top: 0.35rem; }
.lucid-by {
    color: #6B7280; font-size: 0.85rem; margin-top: 0.15rem;
}
.lucid-by a {
    color: #7C3AED !important; text-decoration: none !important; font-weight: 600;
}
.lucid-by a:hover { text-decoration: underline !important; }

.social { display: flex; justify-content: flex-end; gap: 0.7rem; margin: 0 0 0.4rem; }
.social a { line-height: 0; }
.social img { display: block; opacity: 0.8; transition: opacity .12s ease, transform .12s ease; }
.social a:hover img { opacity: 1; transform: translateY(-2px); }
.social-copy { background: none; border: none; padding: 0; cursor: pointer; line-height: 0; }
.social-copy:hover img { opacity: 1; transform: translateY(-2px); }

.metric-card {
    border-radius: 16px; padding: 0.95rem 1.1rem; color: white;
    box-shadow: 0 8px 20px -10px rgba(0,0,0,0.18);
}
.mc-label { font-size: 0.7rem; opacity: 0.9; text-transform: uppercase; letter-spacing: 0.08em; font-weight: 700; }
.mc-value { font-size: 1.9rem; font-weight: 800; margin-top: 0.2rem; line-height: 1; }

.area-pill {
    display: inline-block; padding: 3px 10px; border-radius: 999px;
    color: white; font-size: 0.7rem; font-weight: 700;
}
.badge {
    display: inline-block; padding: 2px 8px; border-radius: 6px;
    font-size: 0.72rem; font-weight: 800; margin-right: 0.25rem;
}

a.conf-link { text-decoration: none !important; color: inherit !important; display: block; }
.conf-wrap { position: relative; margin-bottom: 0.85rem; }

.conf-card {
    border: 1px solid #E5E7EB; border-radius: 16px;
    padding: 1rem 1.1rem; background: white; height: 100%;
    box-shadow: 0 6px 18px -12px rgba(0,0,0,0.15);
    transition: transform .15s ease, box-shadow .15s ease, border-color .15s ease;
    cursor: pointer;
}
.conf-wrap:hover .conf-card {
    transform: translateY(-2px);
    box-shadow: 0 14px 28px -10px rgba(124,58,237,0.35);
    border-color: #DDD6FE;
}

.conf-row { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; }
.conf-title { font-size: 1.3rem; font-weight: 800; color: #111827; margin: 0.45rem 0 0; line-height: 1.15; }
.conf-deadline {
    font-size: 1rem; font-weight: 700; color: #111827;
    margin-top: 0.55rem; padding: 0.35rem 0.55rem;
    background: #FAF5FF; border-radius: 8px; border-left: 3px solid #7C3AED;
}
.conf-days { color: #7C3AED; font-size: 0.82rem; font-weight: 600; margin-top: 0.2rem; }
.countdown { font-variant-numeric: tabular-nums; }
.conf-days.past { color: #9CA3AF; }
.conf-days.soon { color: #EF4444; font-weight: 700; }
.conf-place { color: #6B7280; font-size: 0.82rem; margin-top: 0.45rem; }

.conf-card.expired {
    background: #F9FAFB; border-color: #E5E7EB;
    opacity: 0.6;
}
.conf-card.expired .conf-title { color: #6B7280; }
.conf-card.expired .conf-deadline {
    background: #F3F4F6; border-left-color: #9CA3AF; color: #6B7280;
}
.conf-card.expired .conf-days { color: #9CA3AF; font-weight: 500; }
.conf-card.expired .area-pill { filter: grayscale(0.6); }
.conf-card.expired .badge { filter: grayscale(0.55); opacity: 0.9; }
.conf-wrap:hover .conf-card.expired { opacity: 0.95; }

.conf-tip {
    position: absolute; left: 0; right: 0; bottom: calc(100% + 6px);
    background: #111827; color: #F9FAFB;
    padding: 0.75rem 0.9rem; border-radius: 12px;
    box-shadow: 0 16px 36px -8px rgba(0,0,0,0.45);
    font-size: 0.82rem; line-height: 1.45;
    opacity: 0; transform: translateY(6px);
    transition: opacity .12s ease, transform .12s ease;
    pointer-events: none; z-index: 999;
}
.conf-tip strong { color: #FFFFFF; }
.conf-tip .tip-row { margin-top: 0.25rem; color: #D1D5DB; }
.conf-tip .tip-url { color: #C4B5FD; word-break: break-all; margin-top: 0.5rem; font-size: 0.78rem; }
.conf-tip .tip-dls { color: #FBBF24; margin-top: 0.4rem; }
.conf-wrap:hover .conf-tip { opacity: 1; transform: translateY(0); pointer-events: auto; }

/* keep tooltips from being clipped by Streamlit column wrappers */
div[data-testid="column"] { overflow: visible !important; }
div[data-testid="stHorizontalBlock"] { overflow: visible !important; }

hr { border-color: #E5E7EB; }

/* next-deadlines strip */
.strip-cap { text-align: right; font-size: 0.875rem; font-weight: 600; color: #374151; margin: 0 0 0.3rem; }
.strip { display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0; justify-content: flex-end; }
.strip-chip {
    display: inline-flex; align-items: baseline; gap: 0.4rem;
    border: 1px solid #E5E7EB; border-left-width: 4px; border-radius: 10px;
    padding: 0.3rem 0.7rem; background: #fff; text-decoration: none !important;
    box-shadow: 0 4px 12px -10px rgba(0,0,0,0.3); transition: transform .12s ease, box-shadow .12s ease;
}
.strip-chip:hover { transform: translateY(-1px); box-shadow: 0 10px 20px -12px rgba(124,58,237,0.4); }
.strip-chip b { color: #111827; font-size: 0.9rem; }
.strip-chip span { color: #7C3AED; font-size: 0.78rem; font-weight: 700; }
.strip-chip .ago { color: #9CA3AF; }

/* filter-bar label — matches the Streamlit widget label style (e.g. "Area") */
.filter-cap { font-size: 0.875rem; font-weight: 600; color: #374151;
    margin: 0 0 0.25rem; }
</style>
"""


@st.cache_data(ttl=600)
def load_data() -> dict:
    with open(DATA_PATH) as f:
        return json.load(f)


def soonest_deadline(timeline, now):
    parsed = []
    for t in timeline or []:
        for key in ("deadline", "abstract_deadline"):
            v = t.get(key)
            if not v:
                continue
            ts = pd.to_datetime(v, utc=True, errors="coerce")
            if ts is not pd.NaT and not pd.isna(ts):
                parsed.append(ts)
    if not parsed:
        return None
    upcoming = [p for p in parsed if p >= now]
    return min(upcoming) if upcoming else max(parsed)


def build_dataframe(data: dict) -> pd.DataFrame:
    df = pd.DataFrame(data["conferences"])
    if df.empty:
        return df
    now = pd.Timestamp.now(tz="UTC")
    df["next_deadline"] = df["timeline"].apply(lambda tl: soonest_deadline(tl, now))
    df["days_left"] = (df["next_deadline"] - now).dt.total_seconds() / 86400
    df["vid"] = df.index.astype(str)  # stable per-row id for detail links
    return df


def fmt_year(year) -> str:
    return str(int(year)) if pd.notna(year) else ""


def area_pill(area: str) -> str:
    color = AREA_COLORS.get(area, "#6B7280")
    label = AREA_LABELS.get(area, area)
    return f'<span class="area-pill" style="background:{color}">{label}</span>'


def core_badge(core) -> str:
    val = core if core else "N"
    bg, fg = CORE_BADGE.get(val, CORE_BADGE["N"])
    return f'<span class="badge" style="background:{bg};color:{fg}">CORE {val}</span>'


def ccf_badge(ccf) -> str:
    val = ccf if ccf else "N"
    bg, fg = CCF_BADGE.get(val, CCF_BADGE["N"])
    return f'<span class="badge" style="background:{bg};color:{fg}">CCF {val}</span>'


def metric_card(label: str, value, c1: str, c2: str) -> str:
    return (
        f'<div class="metric-card" style="background:linear-gradient(135deg,{c1},{c2});">'
        f'<div class="mc-label">{label}</div>'
        f'<div class="mc-value">{value}</div>'
        f'</div>'
    )


def render_header(data: dict, total_confs: int):
    fetched = data.get("fetched_at", "")[:10]
    logo_uri = logo_data_uri()
    logo_html = f'<img class="lucid-logo" src="{logo_uri}" alt="Lucid Research">' if logo_uri else ""
    st.markdown(
        f'<div class="lucid-header">'
        f'  {logo_html}'
        f'  <div>'
        f'    <div class="lucid-title">LUCID RESEARCH</div>'
        f'    <div class="lucid-sub">{total_confs} CS conference venues · refreshed {fetched}</div>'
        f'    <div class="lucid-by">by <a href="https://www.linkedin.com/in/alignops/" '
        f'target="_blank" rel="noopener">Madhava Gaikwad</a></div>'
        f'  </div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_metrics(df: pd.DataFrame):
    upcoming = df[df["days_left"] >= 0]
    stats = [
        (df["title"].nunique(), "venues"),
        (df[df["core"] == "A*"]["title"].nunique(), "CORE A*"),
        (len(upcoming[upcoming["days_left"] <= 30]), "next 30d"),
        (len(upcoming[upcoming["days_left"] <= 90]), "next 90d"),
    ]
    boxes = "".join(f'<div class="stat-box"><b>{v}</b><span>{lbl}</span></div>' for v, lbl in stats)
    st.markdown(f'<div class="stat-row">{boxes}</div>', unsafe_allow_html=True)


LANDING_URL = "https://krimler.github.io/paper-tracker/"
SHARE_TEXT = ("Every%20CS%20conference%20deadline%20in%20one%20place%20%E2%80%94%20"
              "free%2C%20daily%2C%20across%209%20areas.")
_ENC_URL = "https%3A%2F%2Fkrimler.github.io%2Fpaper-tracker%2F"

_ICON_PATHS = {
    "github": "M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.51 11.51 0 0112 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222 0 1.606-.014 2.898-.014 3.293 0 .322.216.694.825.576C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12",
    "x": "M18.901 1.153h3.68l-8.04 9.19L24 22.846h-7.406l-5.8-7.584-6.638 7.584H.474l8.6-9.83L0 1.154h7.594l5.243 6.932ZM17.61 20.644h2.039L6.486 3.24H4.298Z",
    "linkedin": "M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 01-2.063-2.065 2.064 2.064 0 112.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.225 0z",
    "copy": "M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z",
    "check": "M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z",
}


def _icon_uri(name: str, color: str) -> str:
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
           f'fill="#{color}"><path d="{_ICON_PATHS[name]}"/></svg>')
    return "data:image/svg+xml," + quote(svg)


def render_social():
    gh = "https://github.com/krimler/paper-tracker"
    x = f"https://twitter.com/intent/tweet?text={SHARE_TEXT}&url={_ENC_URL}"
    li = f"https://www.linkedin.com/sharing/share-offsite/?url={_ENC_URL}"
    st.markdown(
        '<div class="social">'
        f'<a href="{gh}" target="_blank" rel="noopener" title="GitHub repository">'
        f'<img src="{_icon_uri("github", "24292F")}" width="22"></a>'
        f'<a href="{x}" target="_blank" rel="noopener" title="Share on X">'
        f'<img src="{_icon_uri("x", "000000")}" width="20"></a>'
        f'<a href="{li}" target="_blank" rel="noopener" title="Share on LinkedIn">'
        f'<img src="{_icon_uri("linkedin", "0A66C2")}" width="22"></a>'
        f'<button id="lucid-copy" class="social-copy" title="Copy link">'
        f'<img src="{_icon_uri("copy", "6B7280")}" width="20"></button>'
        '</div>',
        unsafe_allow_html=True,
    )


def render_social_js():
    """Wire the copy-link button (in the parent doc) from a components iframe."""
    components.html(
        f"""<script>
        (function () {{
          var doc = window.parent.document;
          var btn = doc.getElementById('lucid-copy');
          if (!btn || btn.dataset.wired) return;
          btn.dataset.wired = '1';
          var orig = btn.innerHTML;
          var check = '<img src="{_icon_uri('check', '16A34A')}" width="20">';
          btn.addEventListener('click', function () {{
            var cb = window.parent.navigator.clipboard || navigator.clipboard;
            cb.writeText('{LANDING_URL}');
            btn.innerHTML = check;
            setTimeout(function () {{ btn.innerHTML = orig; }}, 1500);
          }});
        }})();
        </script>""",
        height=0,
    )


def render_about(total_confs: int):
    with st.expander("About this tracker"):
        st.markdown(
            f"""
**Lucid Research** tracks submission deadlines for {total_confs}+ top computer
science conferences across nine research areas, refreshed daily.

Most CS work is published at conferences that open once a year, so a missed
deadline can cost months. The per-field trackers we build on —
[ai-deadlines](https://github.com/paperswithcode/ai-deadlines),
[sec-deadlines](https://sec-deadlines.github.io),
[tcs-conf](https://tcs-conf.github.io), and
[ccfddl](https://github.com/ccfddl/ccf-deadlines) — are each excellent but
siloed by field. This pulls them into one curated, ranked, cross-area view,
plus a hand-kept list for what they miss.

The data is open and downloadable as
[JSON](https://raw.githubusercontent.com/krimler/paper-tracker/main/data/conferences.json).

Missing a venue, or want something added? Email **yavanat [at] outlook [dot] com**.

[Landing page](https://krimler.github.io/paper-tracker/)
· [source](https://github.com/krimler/paper-tracker)
· by [Madhava Gaikwad](https://www.linkedin.com/in/alignops/)
"""
        )
        st.markdown(
            "**Share** &nbsp;"
            "[X](https://twitter.com/intent/tweet?text=Every%20CS%20conference%20"
            "deadline%20in%20one%20place%20%E2%80%94%20free%2C%20daily%2C%20across"
            "%209%20areas.&url=https%3A%2F%2Fkrimler.github.io%2Fpaper-tracker%2F)"
            " · [LinkedIn](https://www.linkedin.com/sharing/share-offsite/?url="
            "https%3A%2F%2Fkrimler.github.io%2Fpaper-tracker%2F) · or copy:"
        )
        st.code("https://krimler.github.io/paper-tracker/", language=None)


def _ics_escape(s) -> str:
    return (str(s or "").replace("\\", "\\\\").replace(",", "\\,")
            .replace(";", "\\;").replace("\n", "\\n"))


def _ics_dt(v):
    ts = pd.to_datetime(v, utc=True, errors="coerce")
    return None if pd.isna(ts) else ts.strftime("%Y%m%dT%H%M%SZ")


def build_ics(row) -> str:
    title, year = row["title"], fmt_year(row["year"])
    lines = ["BEGIN:VCALENDAR", "VERSION:2.0",
             "PRODID:-//Lucid Research//Conference Tracker//EN", "CALSCALE:GREGORIAN"]
    for i, t in enumerate(row["timeline"] or []):
        for kind, key in (("abstract", "abstract_deadline"), ("submission", "deadline")):
            dt = _ics_dt(t.get(key))
            if not dt:
                continue
            lines += [
                "BEGIN:VEVENT",
                f"UID:{quote(title)}-{year}-{kind}-{i}@lucid-research",
                f"DTSTAMP:{dt}", f"DTSTART:{dt}", f"DTEND:{dt}",
                f"SUMMARY:{_ics_escape(f'{title} {year} {kind} deadline')}",
                f"URL:{row.get('link') or ''}",
                f"DESCRIPTION:{_ics_escape(row.get('description') or title)}",
                "END:VEVENT",
            ]
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)


def render_strip(df: pd.DataFrame):
    up = df[df["days_left"] >= 0].sort_values("days_left").head(6)
    if up.empty:
        return
    chips = ""
    for r in up.itertuples(index=False):
        d = int(round(r.days_left))
        color = AREA_COLORS.get(r.area, "#6B7280")
        href = r.link or "#"
        chips += (
            f'<a class="strip-chip" style="border-left-color:{color}" href="{href}" target="_blank" rel="noopener">'
            f'<b>{r.title} &lsquo;{fmt_year(r.year)[-2:]}</b>'
            f'<span>{d}d</span></a>'
        )
    st.markdown(
        f'<div class="strip-cap">Closing soon</div><div class="strip">{chips}</div>',
        unsafe_allow_html=True,
    )


def render_detail(df: pd.DataFrame):
    dv = st.session_state.get("detail_vid")
    if not dv:
        return
    match = df[df["vid"] == dv]
    if match.empty:
        st.session_state.pop("detail_vid", None)
        return
    r = match.iloc[0]
    with st.container(border=True):
        top, close = st.columns([5, 1])
        top.markdown(f"### {r['title']} {fmt_year(r['year'])}")
        if close.button("✕ Close", key="close_detail", use_container_width=True):
            for k in ("detail_vid", "tbl_up", "tbl_past"):
                st.session_state.pop(k, None)
            st.rerun()
        st.markdown(
            area_pill(r["area"]) + " " + core_badge(r["core"]) + ccf_badge(r["ccf"]),
            unsafe_allow_html=True,
        )
        if r.get("description") and r["description"] != r["title"]:
            st.write(r["description"])
        meta = []
        if r.get("place"):
            meta.append(f"📍 {r['place']}")
        if r.get("date"):
            meta.append(f"🗓 {r['date']}")
        if r.get("source"):
            meta.append(f"source: {r['source']}")
        if meta:
            st.caption(" · ".join(meta))
        st.markdown("**Deadlines** (UTC)")
        rounds = []
        for t in r["timeline"] or []:
            bits = []
            if t.get("abstract_deadline"):
                bits.append(f"abstract {t['abstract_deadline']}")
            if t.get("deadline"):
                bits.append(f"submission {t['deadline']}")
            line = " · ".join(bits) if bits else "TBA"
            if t.get("comment"):
                line += f" — {t['comment']}"
            rounds.append(f"- {line}")
        st.markdown("\n".join(rounds) if rounds else "- TBA")
        b1, b2 = st.columns(2)
        if r.get("link"):
            b1.link_button("Open call for papers ↗", r["link"], use_container_width=True)
        b2.download_button(
            "Add to calendar (.ics)",
            build_ics(r),
            file_name=f"{r['title']}_{fmt_year(r['year'])}.ics",
            mime="text/calendar",
            use_container_width=True,
        )


def days_text(days):
    if pd.isna(days):
        return "", ""
    d = int(round(days))
    if d < 0:
        return f"{-d} days ago", "past"
    if d <= 14:
        return f"{d} days left", "soon"
    return f"{d} days left", ""


def html_escape(s) -> str:
    if not s:
        return ""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def build_tooltip_html(row, link: str) -> str:
    desc = html_escape(row.description or row.title)
    conf_date = html_escape(row.date or "")
    place = html_escape(row.place or "")
    tl_lines = []
    for t in row.timeline or []:
        bits = []
        if t.get("abstract_deadline"):
            bits.append(f"abs {html_escape(t['abstract_deadline'])}")
        if t.get("deadline"):
            bits.append(html_escape(t["deadline"]))
        if t.get("comment"):
            bits.append(f"({html_escape(t['comment'])})")
        if bits:
            tl_lines.append("&bull; " + " ".join(bits))
    pieces = [f'<strong>{desc}</strong>']
    if conf_date:
        pieces.append(f'<div class="tip-row">Conf: {conf_date}</div>')
    if place:
        pieces.append(f'<div class="tip-row">{place}</div>')
    if tl_lines:
        pieces.append(f'<div class="tip-dls">{"<br>".join(tl_lines)}</div>')
    pieces.append(f'<div class="tip-url">{html_escape(link)}</div>')
    return f'<div class="conf-tip">{"".join(pieces)}</div>'


def render_countdown_js():
    """Live-tick every .countdown element. Runs in a components iframe that reaches
    into the parent Streamlit document (inline <script> in st.markdown won't run)."""
    components.html(
        """<script>
        (function () {
          function pad(n){ return n < 10 ? '0' + n : '' + n; }
          function tick() {
            var doc = window.parent.document;
            var now = Date.now();
            doc.querySelectorAll('.countdown').forEach(function (e) {
              var dl = new Date(e.getAttribute('data-deadline')).getTime();
              if (isNaN(dl)) return;
              var diff = Math.floor((dl - now) / 1000);
              if (diff <= 0) { e.textContent = 'deadline passed'; return; }
              var d = Math.floor(diff / 86400); diff -= d * 86400;
              var h = Math.floor(diff / 3600); diff -= h * 3600;
              var m = Math.floor(diff / 60); var s = diff - m * 60;
              e.textContent = d + 'd ' + pad(h) + 'h ' + pad(m) + 'm ' + pad(s) + 's';
            });
          }
          tick();
          if (window.__lucidTimer) clearInterval(window.__lucidTimer);
          window.__lucidTimer = setInterval(tick, 1000);
        })();
        </script>""",
        height=0,
    )


def render_cards(df: pd.DataFrame, per_page: int = 90):
    if len(df) > per_page:
        st.caption(f"Showing first {per_page} of {len(df)} — narrow filters to see the rest.")
        df = df.head(per_page)
    cols = st.columns(3)
    for i, row in enumerate(df.itertuples(index=False)):
        col = cols[i % 3]
        with col:
            deadline = (
                row.next_deadline.strftime("%Y-%m-%d %H:%M UTC")
                if pd.notna(row.next_deadline)
                else "TBA"
            )
            d_text, d_class = days_text(row.days_left)
            is_expired = pd.notna(row.days_left) and row.days_left < 0
            card_cls = "conf-card expired" if is_expired else "conf-card"
            link = row.link or "#"
            accent = AREA_COLORS.get(row.area, "#6B7280")
            place = html_escape(row.place or "")
            title_short = f"{row.title} &lsquo;{str(row.year)[-2:]}"
            title_attr = html_escape(f"{row.description or row.title} — {link}")

            if pd.notna(row.next_deadline) and not is_expired:
                iso = row.next_deadline.strftime("%Y-%m-%dT%H:%M:%SZ")
                days_html = f'<div class="conf-days countdown {d_class}" data-deadline="{iso}">{d_text}</div>'
            else:
                days_html = f'<div class="conf-days {d_class}">{d_text}</div>'

            inner = (
                f'<div class="{card_cls}" style="border-left:5px solid {accent}">'
                f'  <div class="conf-row">{area_pill(row.area)}'
                f'    <span>{core_badge(row.core)}{ccf_badge(row.ccf)}</span>'
                f'  </div>'
                f'  <div class="conf-title">{title_short}</div>'
                f'  <div class="conf-deadline">{deadline}</div>'
                f'  {days_html}'
                + (f'  <div class="conf-place">{place}</div>' if place else "")
                + f'</div>'
            )
            html = (
                f'<div class="conf-wrap">'
                f'  {build_tooltip_html(row, link)}'
                f'  <a class="conf-link" href="{link}" target="_blank" rel="noopener" title="{title_attr}">'
                f'    {inner}'
                f'  </a>'
                f'</div>'
            )
            st.markdown(html, unsafe_allow_html=True)


def style_table(df: pd.DataFrame):
    def core_style(val):
        bg, fg = CORE_BADGE.get(val, ("", ""))
        return f"background-color: {bg}; color: {fg}; font-weight: 800" if bg else ""

    def ccf_style(val):
        bg, fg = CCF_BADGE.get(val, ("", ""))
        return f"background-color: {bg}; color: {fg}; font-weight: 800" if bg else ""

    def dim_expired(row):
        days = row.get("Days left")
        if pd.notna(days) and days < 0:
            return ["background-color: #F3F4F6; color: #9CA3AF; font-weight: 500"] * len(row)
        return [""] * len(row)

    styler = df.style
    styler = styler.map(core_style, subset=["CORE"])
    styler = styler.map(ccf_style, subset=["CCF"])
    # Apply row dim AFTER cell colors so it overrides on expired rows only.
    styler = styler.apply(dim_expired, axis=1)
    return styler


def render_table(df: pd.DataFrame, key: str):
    display = df[
        [
            "area", "title", "year", "core", "ccf",
            "next_deadline", "days_left", "place", "link",
        ]
    ].rename(
        columns={
            "area": "Area", "title": "Venue", "year": "Year",
            "core": "CORE", "ccf": "CCF",
            "next_deadline": "Deadline (UTC)", "days_left": "Days",
            "place": "Location", "link": "CFP",
        }
    ).copy()
    display["Area"] = display["Area"].map(lambda a: AREA_LABELS.get(a, a))
    display["Days"] = display["Days"].round(0)
    display["CORE"] = display["CORE"].fillna("N")
    display["CCF"] = display["CCF"].fillna("N")
    sel = st.dataframe(
        style_table(display),
        column_config={
            "Area": st.column_config.TextColumn("Area", width="small"),
            "Venue": st.column_config.TextColumn("Venue", width="small"),
            "Year": st.column_config.NumberColumn("Year", format="%d"),
            "Days": st.column_config.NumberColumn("Days", format="%d d", help="Days until the next deadline (negative = passed)"),
            "CFP": st.column_config.LinkColumn("CFP", display_text="open ↗"),
            "Deadline (UTC)": st.column_config.DatetimeColumn(
                "Deadline (UTC)", format="YYYY-MM-DD HH:mm"
            ),
        },
        hide_index=True,
        use_container_width=True,
        height=620,
        on_select="rerun",
        selection_mode="single-row",
        key=key,
    )
    rows = sel.selection.get("rows", []) if sel and sel.selection else []
    if rows:
        chosen = df.iloc[rows[0]]["vid"]
        if st.session_state.get("detail_vid") != chosen:
            st.session_state["detail_vid"] = chosen
            st.rerun()
    st.caption("Tip: click a row to see full deadlines and add it to your calendar.")


RANK_LABELS = {"All": "All ranks", "astar": "A*", "a": "A & up", "b": "B & up"}
RANK_TIERS = {"astar": ["A*"], "a": ["A*", "A"], "b": ["A*", "A", "B"]}
HORIZON_DAYS = {"30 days": 30, "90 days": 90, "6 months": 182, "1 year": 365}


def sort_df(f: pd.DataFrame, sort_by: str, ascending: bool = True) -> pd.DataFrame:
    if sort_by.startswith("CORE"):
        return (
            f.assign(_o=f["core"].fillna("N").map(CORE_ORDER))
            .sort_values(["_o", "next_deadline"], na_position="last")
            .drop(columns="_o")
        )
    if sort_by.startswith("Alpha"):
        return f.sort_values(["title", "year"])
    return f.sort_values("next_deadline", ascending=ascending, na_position="last")


def reset_filters():
    for k in ("area_pills", "rank_pills", "sort_pills", "horizon", "search",
              "year_choice", "view_mode", "detail_vid", "tbl_up", "tbl_past"):
        st.session_state.pop(k, None)


def main():
    st.set_page_config(
        page_title="Lucid Panel",
        page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else None,
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

    try:
        data = load_data()
    except FileNotFoundError:
        st.error("No data yet. Run `python fetcher/fetch.py`.")
        return

    df = build_dataframe(data)
    if df.empty:
        st.warning("Data file is empty.")
        return

    areas = sorted(df["area"].dropna().unique())

    # ---------- top-right social / share / copy ----------
    render_social()

    # ---------- header band: title + About left, metrics + closing-soon right ----------
    hcol, mcol = st.columns([5, 7], vertical_alignment="center")
    with hcol:
        render_header(data, df["title"].nunique())
        render_about(df["title"].nunique())
    with mcol:
        render_metrics(df)
        render_strip(df)

    # ---------- area pills (full width) ----------
    area_choice = st.pills(
        "Area", options=areas, selection_mode="multi",
        default=["ai_ml"] if "ai_ml" in areas else [],
        format_func=lambda a: AREA_LABELS.get(a, a), key="area_pills",
    ) or []

    # ---------- filter bar (full width, horizontal) ----------
    c_search, c_rank, c_sort, c_view, c_more = st.columns([3, 2, 2, 1.4, 1.0])
    with c_search:
        search = st.text_input(
            "Search", placeholder="Search title or keyword…", key="search",
        )
    with c_rank:
        min_rank = st.pills(
            "Rank", options=list(RANK_LABELS), selection_mode="single",
            default="All", format_func=lambda r: RANK_LABELS[r], key="rank_pills",
        ) or "All"
    with c_sort:
        sort_by = st.pills(
            "Sort", options=["Deadline", "CORE rank", "Alphabetical"],
            selection_mode="single", default="Deadline", key="sort_pills",
        ) or "Deadline"
    with c_view:
        view_mode = st.segmented_control(
            "View", options=["Cards", "Table"], default="Cards", key="view_mode",
            format_func=lambda v: {"Cards": "▦ Cards", "Table": "≣ Table"}[v],
        ) or "Cards"
    with c_more:
        st.markdown('<div class="filter-cap">More</div>', unsafe_allow_html=True)
        with st.popover("⚙", use_container_width=True):
            horizon = st.selectbox(
                "Upcoming within", options=["Any time"] + list(HORIZON_DAYS), key="horizon",
            )
            years = sorted({int(y) for y in df["year"].dropna().unique()})
            year_choice = st.selectbox("Year", options=["All"] + years, key="year_choice")
            st.button("Reset filters", on_click=reset_filters, use_container_width=True)

    # ---------- filter ----------
    f = df.copy()
    if area_choice:
        f = f[f["area"].isin(area_choice)]
    if min_rank in RANK_TIERS:
        f = f[f["core"].fillna("N").isin(RANK_TIERS[min_rank])]
    if year_choice != "All":
        f = f[f["year"] == year_choice]
    if search:
        s = search.lower()
        f = f[
            f["title"].str.lower().str.contains(s, na=False)
            | f["description"].str.lower().str.contains(s, na=False)
        ]

    # ---------- split: upcoming (incl. undated) vs past ----------
    is_past = f["days_left"] < 0  # NaN -> False, so undated venues stay in Upcoming
    upcoming = sort_df(f[~is_past], sort_by, ascending=True)
    past = sort_df(f[is_past], sort_by, ascending=False)

    if horizon in HORIZON_DAYS:
        within = HORIZON_DAYS[horizon]
        upcoming = upcoming[upcoming["days_left"].notna() & (upcoming["days_left"] <= within)]

    # ---------- detail panel (opened by clicking a card/row/chip) ----------
    render_detail(df)

    # ---------- output ----------
    tab_up, tab_past = st.tabs(
        [f"Upcoming · {upcoming['title'].nunique()}",
         f"Past · {past['title'].nunique()}"]
    )
    with tab_up:
        if upcoming.empty:
            st.info("No upcoming deadlines match these filters.")
        elif view_mode == "Table":
            render_table(upcoming, "tbl_up")
        else:
            render_cards(upcoming)
    with tab_past:
        if past.empty:
            st.info("No past deadlines match these filters.")
        elif view_mode == "Table":
            render_table(past, "tbl_past")
        else:
            render_cards(past)

    if view_mode == "Cards":
        render_countdown_js()
    render_social_js()


if __name__ == "__main__":
    main()
