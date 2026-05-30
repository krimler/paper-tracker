"""Lucid Research — CS Conference Deadlines dashboard."""
from __future__ import annotations

import base64
import json
from pathlib import Path

import pandas as pd
import streamlit as st

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
[data-testid="stAppViewContainer"] {
    background: linear-gradient(180deg, #FAF5FF 0%, #FFFFFF 40%);
}
section[data-testid="stSidebar"] > div {
    background: linear-gradient(180deg, #F5F3FF, #FFFFFF);
}
.block-container { padding-top: 2rem; }

.lucid-header { display: flex; align-items: center; gap: 1rem; }
.lucid-logo {
    width: 72px; height: 72px; border-radius: 16px;
    box-shadow: 0 8px 22px -10px rgba(67, 56, 202, 0.55);
    object-fit: cover; flex-shrink: 0;
}
.lucid-title {
    font-size: 3rem; font-weight: 900; letter-spacing: -0.04em;
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
    return df


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
    next30 = len(upcoming[upcoming["days_left"] <= 30])
    next90 = len(upcoming[upcoming["days_left"] <= 90])
    a_star = df[df["core"] == "A*"]["title"].nunique()
    total = df["title"].nunique()
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(metric_card("Venues tracked", total, "#7C3AED", "#A855F7"), unsafe_allow_html=True)
    c2.markdown(metric_card("CORE A* venues", a_star, "#F59E0B", "#FBBF24"), unsafe_allow_html=True)
    c3.markdown(metric_card("Deadlines · next 30d", next30, "#EC4899", "#F472B6"), unsafe_allow_html=True)
    c4.markdown(metric_card("Deadlines · next 90d", next90, "#06B6D4", "#22D3EE"), unsafe_allow_html=True)


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
            place = html_escape(row.place or "")
            title_short = f"{row.title} &lsquo;{str(row.year)[-2:]}"
            title_attr = html_escape(f"{row.description or row.title} — {link}")

            inner = (
                f'<div class="{card_cls}">'
                f'  <div class="conf-row">{area_pill(row.area)}'
                f'    <span>{core_badge(row.core)}{ccf_badge(row.ccf)}</span>'
                f'  </div>'
                f'  <div class="conf-title">{title_short}</div>'
                f'  <div class="conf-deadline">{deadline}</div>'
                f'  <div class="conf-days {d_class}">{d_text}</div>'
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


def render_table(df: pd.DataFrame):
    display = df[
        [
            "title", "description", "area", "ccf", "core", "year",
            "next_deadline", "days_left", "date", "place", "link",
        ]
    ].rename(
        columns={
            "title": "Conf", "description": "Full name", "area": "Area",
            "ccf": "CCF", "core": "CORE", "year": "Year",
            "next_deadline": "Next deadline (UTC)", "days_left": "Days left",
            "date": "Conf date", "place": "Location", "link": "URL",
        }
    ).copy()
    display["Area"] = display["Area"].map(lambda a: AREA_LABELS.get(a, a))
    display["Days left"] = display["Days left"].round(1)
    display["CORE"] = display["CORE"].fillna("N")
    display["CCF"] = display["CCF"].fillna("N")
    st.dataframe(
        style_table(display),
        column_config={
            "URL": st.column_config.LinkColumn("URL", display_text="open"),
            "Next deadline (UTC)": st.column_config.DatetimeColumn(
                "Next deadline (UTC)", format="YYYY-MM-DD HH:mm"
            ),
        },
        hide_index=True,
        use_container_width=True,
        height=640,
    )


RANK_TIERS = {"A* only": ["A*"], "A & above": ["A*", "A"], "B & above": ["A*", "A", "B"]}
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
    for k in ("area_choice", "min_rank", "horizon", "search",
              "year_choice", "view_mode", "sort_by"):
        st.session_state.pop(k, None)


def main():
    st.set_page_config(
        page_title="Lucid Research — Conference Deadlines",
        page_icon=str(LOGO_PATH) if LOGO_PATH.is_file() else None,
        layout="wide",
        initial_sidebar_state="expanded",
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

    # ---------- header ----------
    render_header(data, df["title"].nunique())
    st.write("")
    render_metrics(df)
    st.write("")

    # ---------- sidebar ----------
    sb = st.sidebar
    sb.markdown("### Filters")
    search = sb.text_input("Search", placeholder="Title or keyword…", key="search")
    area_choice = sb.multiselect(
        "Area",
        options=areas,
        default=[],
        format_func=lambda a: AREA_LABELS.get(a, a),
        placeholder="All areas",
        key="area_choice",
    )
    min_rank = sb.selectbox(
        "Rank (CORE)",
        options=["All ranks", "A* only", "A & above", "B & above"],
        key="min_rank",
    )
    sort_by = sb.selectbox(
        "Sort by",
        options=["Deadline", "CORE rank", "Alphabetical"],
        key="sort_by",
    )
    view_mode = sb.segmented_control(
        "View", options=["Cards", "Table"], default="Cards", key="view_mode"
    ) or "Cards"

    with sb.expander("More filters"):
        horizon = st.selectbox(
            "Upcoming within",
            options=["Any time"] + list(HORIZON_DAYS),
            key="horizon",
        )
        years = sorted({int(y) for y in df["year"].dropna().unique()})
        year_choice = st.selectbox("Year", options=["All"] + years, key="year_choice")

    sb.button("Reset filters", on_click=reset_filters, use_container_width=True)

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

    # ---------- output ----------
    tab_up, tab_past = st.tabs(
        [f"Upcoming · {upcoming['title'].nunique()}",
         f"Past · {past['title'].nunique()}"]
    )
    with tab_up:
        if upcoming.empty:
            st.info("No upcoming deadlines match these filters.")
        elif view_mode == "Table":
            render_table(upcoming)
        else:
            render_cards(upcoming)
    with tab_past:
        if past.empty:
            st.info("No past deadlines match these filters.")
        elif view_mode == "Table":
            render_table(past)
        else:
            render_cards(past)


if __name__ == "__main__":
    main()
