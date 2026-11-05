"""
app.py
------
Main Streamlit application for SmartStudy AI.
All UI lives here; logic is delegated to scheduler.py and data_manager.py.
"""

import html
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from datetime import date, timedelta

import data_manager as dm
import scheduler as sc

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartStudy AI",
    page_icon="📚",
    layout="wide",
)

# ── Global CSS ────────────────────────────────────────────────────────────────

st.markdown("""
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"], [data-testid="stMain"] {
    background-color: #16181d;
    color: #e2e4e9;
    font-family: Inter, system-ui, -apple-system, sans-serif;
}
[data-testid="stHeader"] { background-color: #16181d; }
#MainMenu, footer, [data-testid="stToolbar"] { display: none !important; }
[data-testid="stMainBlockContainer"] { padding-top: 1.8rem !important; }


/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {
    border-bottom: 1px solid #2a2d36;
    gap: 0;
    background: transparent;
}
[data-testid="stTabs"] [role="tab"] {
    font-size: 0.82rem;
    font-weight: 500;
    color: #6b7280;
    padding: 0.5rem 1.1rem;
    background: transparent;
    border-radius: 0;
    /* reset every border so Streamlit's default red/coloured indicator can't show */
    border-top: 2px solid transparent !important;
    border-left: 2px solid transparent !important;
    border-right: 2px solid transparent !important;
    border-bottom: 2px solid transparent !important;
    outline: none !important;
    box-shadow: none !important;
}
[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: #e2e4e9 !important;
    border-top: 2px solid transparent !important;
    border-left: 2px solid transparent !important;
    border-right: 2px solid transparent !important;
    border-bottom: 2px solid #3b82f6 !important;
    background: transparent !important;
}
[data-testid="stTabs"] [role="tab"]:hover {
    color: #c9cdd6;
    border-bottom: 2px solid #4b5563 !important;
}

/* ── Section labels ── */
.ss-section {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #6b7280;
    margin: 1.2rem 0 0.5rem 0;
}

/* ── Buttons ── */
[data-testid="stButton"] > button {
    background-color: #1e2028;
    color: #e2e4e9;
    border: 1px solid #2a2d36;
    border-radius: 6px;
    font-size: 0.82rem;
    font-weight: 500;
    padding: 0.4rem 1rem;
    transition: background 0.15s, border-color 0.15s;
}
[data-testid="stButton"] > button:hover {
    background-color: #2a2d36;
    border-color: #3b82f6;
    color: #e2e4e9;
}
[data-testid="stButton"] > button[kind="primary"],
.ss-primary-btn [data-testid="stButton"] > button {
    background-color: #3b82f6;
    border-color: #3b82f6;
    color: #fff;
}
[data-testid="stButton"] > button[kind="primary"]:hover,
.ss-primary-btn [data-testid="stButton"] > button:hover {
    background-color: #2563eb;
    border-color: #2563eb;
}

/* ── Inputs / selects ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] > div > div,
[data-testid="stDateInput"] input {
    background-color: #1e2028 !important;
    border: 1px solid #2a2d36 !important;
    color: #e2e4e9 !important;
    border-radius: 6px !important;
    font-size: 0.83rem !important;
}
[data-testid="stTextInput"] input:focus,
[data-testid="stSelectbox"] > div > div:focus-within {
    border-color: #3b82f6 !important;
    box-shadow: none !important;
}

/* ── Sliders ── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] {
    background-color: #3b82f6 !important;
}
[data-testid="stSlider"] [data-baseweb="slider"] div[class*="Track"] {
    background-color: #2a2d36 !important;
}

/* ── Dataframes ── */
[data-testid="stDataFrame"] { border: 1px solid #2a2d36; border-radius: 6px; overflow: hidden; }
[data-testid="stDataFrame"] th {
    background-color: #1e2028 !important;
    color: #9ca3af !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.05em !important;
    text-transform: uppercase !important;
}
[data-testid="stDataFrame"] td {
    background-color: #16181d !important;
    color: #e2e4e9 !important;
    font-size: 0.82rem !important;
}

/* ── Info / success / warning / error boxes ── */
[data-testid="stAlert"] {
    border-radius: 6px !important;
    font-size: 0.82rem !important;
}

/* ── Divider ── */
hr { border-color: #2a2d36 !important; }

/* ── Timetable HTML table ── */
.tt-scroll { overflow-x: auto; -webkit-overflow-scrolling: touch; }
.tt-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.8rem;
    min-width: 560px;
}
.tt-table th {
    background: #1e2028;
    color: #3b82f6;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 8px 10px;
    border: 1px solid #2a2d36;
    text-align: center;
    white-space: nowrap;
}
.tt-table th.tt-block-col {
    color: #6b7280;
    font-size: 0.68rem;
    min-width: 52px;
}
.tt-table td {
    border: 1px solid #2a2d36;
    padding: 7px 10px;
    vertical-align: top;
    text-align: center;
    min-width: 90px;
}
.tt-time  { font-size: 0.68rem; color: #6b7280; display: block; margin-bottom: 2px; }
.tt-subj  { font-size: 0.82rem; color: #e2e4e9; font-weight: 500; }
.tt-empty { color: #3a3d47; font-size: 0.8rem; }
.tt-cell-missed      { background-color: #2d1f1f; }
.tt-cell-missed      .tt-subj { color: #ef4444; }
.tt-cell-rescheduled { background-color: #1a2535; }
.tt-cell-rescheduled .tt-subj { color: #60a5fa; }
.tt-cell-normal      { background-color: #16181d; }
.tt-block-label      { color: #4b5563; font-size: 0.72rem; font-weight: 500; }

/* ── Urgency badges ── */
.urg-critical { color: #ef4444; font-weight: 600; font-size: 0.78rem; }
.urg-soon     { color: #f59e0b; font-weight: 600; font-size: 0.78rem; }
.urg-upcoming { color: #10b981; font-weight: 600; font-size: 0.78rem; }

/* ── Reschedule day label ── */
.rs-day-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    color: #6b7280;
    margin: 1rem 0 0.3rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.title("SmartStudy AI")
st.caption("Student Timetable Assistant — Intelligent Study Planning")
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────

tabs = st.tabs(["Setup", "Exams", "Preferences", "Timetable", "Analytics", "Reschedule"])


# ── Tab 1 – Setup ─────────────────────────────────────────────────────────────

with tabs[0]:
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown('<p class="ss-section">Add Subject</p>', unsafe_allow_html=True)
        name       = st.text_input("Subject Name", key="subj_name", placeholder="e.g. Data Structures")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="subj_diff")
        priority   = st.slider("Priority", 1, 5, 3, key="subj_prio",
                               help="1 = lowest priority, 5 = highest priority")

        if st.button("Add Subject", key="btn_add_subj"):
            if name.strip():
                try:
                    dm.add_subject(name.strip(), difficulty, priority)
                    st.success(f"'{name.strip()}' added.")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
            else:
                st.warning("Enter a subject name.")

    with col2:
        st.markdown('<p class="ss-section">Current Subjects</p>', unsafe_allow_html=True)
        subjects = dm.get_subjects()
        if subjects:
            df = pd.DataFrame(subjects).rename(columns={
                "name": "Subject", "difficulty": "Difficulty", "priority": "Priority"
            })
            st.dataframe(df, use_container_width=True, hide_index=True)

            remove_name = st.selectbox(
                "Select subject to remove", [s["name"] for s in subjects], key="remove_subj"
            )
            if st.button("Remove Subject", key="btn_remove_subj"):
                dm.remove_subject(remove_name)
                st.success(f"'{remove_name}' removed.")
                st.rerun()
        else:
            st.info("No subjects added yet.")


# ── Tab 2 – Exams ─────────────────────────────────────────────────────────────

with tabs[1]:
    subjects = dm.get_subjects()
    exams    = dm.get_exams()

    if not subjects:
        st.info("Add subjects first in the Setup tab.")
    else:
        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown('<p class="ss-section">Schedule Exam</p>', unsafe_allow_html=True)
            exam_subject = st.selectbox("Subject", [s["name"] for s in subjects], key="exam_subj")
            min_date     = date.today() + timedelta(days=1)
            exam_date    = st.date_input("Exam Date", min_value=min_date, key="exam_date")

            if st.button("Save Exam Date", key="btn_save_exam"):
                dm.add_exam(exam_subject, str(exam_date))
                st.success(f"Exam for '{exam_subject}' set to {exam_date}.")
                st.rerun()

        with col2:
            st.markdown('<p class="ss-section">Scheduled Exams</p>', unsafe_allow_html=True)
            if exams:
                rows = []
                for e in sorted(exams, key=lambda x: x["date"]):
                    days_left = (date.fromisoformat(e["date"]) - date.today()).days
                    if days_left <= 7:
                        urgency = "Critical"
                    elif days_left <= 14:
                        urgency = "Soon"
                    else:
                        urgency = "Upcoming"
                    rows.append({
                        "Subject":   e["subject"],
                        "Date":      e["date"],
                        "Days Left": days_left,
                        "Urgency":   urgency,
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

                remove_exam_subj = st.selectbox(
                    "Remove exam for", [e["subject"] for e in exams], key="remove_exam"
                )
                if st.button("Remove Exam", key="btn_remove_exam"):
                    dm.remove_exam(remove_exam_subj)
                    st.rerun()
            else:
                st.info("No exams scheduled yet.")


# ── Tab 3 – Preferences ───────────────────────────────────────────────────────

with tabs[2]:
    prefs = dm.get_preferences()
    st.markdown('<p class="ss-section">Study Settings</p>', unsafe_allow_html=True)

    daily_hours   = st.slider("Daily Available Study Hours", 1.0, 12.0,
                              float(prefs["daily_hours"]), 0.5)
    block_size    = st.select_slider("Study Block Size (hours)",
                                     options=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
                                     value=float(prefs["block_size"]))
    break_minutes = st.slider("Break Between Blocks (minutes)", 5, 30,
                              int(prefs["break_minutes"]), 5)

    slots_per_day = int(daily_hours // block_size)
    st.markdown(
        f"**{slots_per_day}** study block(s) per day &nbsp;·&nbsp; "
        f"**{block_size}h** each &nbsp;·&nbsp; **{break_minutes} min** break",
        unsafe_allow_html=True,
    )

    if st.button("Save Preferences", key="btn_save_prefs"):
        dm.save_preferences(daily_hours, block_size, break_minutes)
        st.success("Preferences saved.")


# ── Tab 4 – Timetable ─────────────────────────────────────────────────────────

def _build_timetable_html(timetable: dict) -> str:
    """
    Build a styled HTML table from the timetable dict.
    All user-supplied values are html.escape()d before insertion.
    """
    max_slots = max((len(timetable[d]) for d in sc.DAYS if d in timetable), default=0)
    if max_slots == 0:
        return ""

    # Header row
    header_cells = '<th class="tt-block-col"></th>'
    for day in sc.DAYS:
        header_cells += f"<th>{html.escape(day)}</th>"

    rows_html = ""
    for i in range(max_slots):
        row_cells = f'<td class="tt-block-label">B{i + 1}</td>'
        for day in sc.DAYS:
            slots = timetable.get(day, [])
            if i >= len(slots):
                row_cells += '<td class="tt-cell-normal"><span class="tt-empty">—</span></td>'
                continue

            slot    = slots[i]
            subject = slot.get("subject") or ""
            missed  = slot.get("missed", False)
            rescheduled = slot.get("rescheduled", False)

            time_safe    = html.escape(slot.get("start", ""))
            subject_safe = html.escape(subject) if subject else "—"

            if missed:
                cell_class = "tt-cell-missed"
            elif rescheduled:
                cell_class = "tt-cell-rescheduled"
            else:
                cell_class = "tt-cell-normal"

            if subject:
                row_cells += (
                    f'<td class="{cell_class}">'
                    f'<span class="tt-time">{time_safe}</span>'
                    f'<span class="tt-subj">{subject_safe}</span>'
                    f"</td>"
                )
            else:
                row_cells += (
                    f'<td class="{cell_class}">'
                    f'<span class="tt-time">{time_safe}</span>'
                    f'<span class="tt-empty">—</span>'
                    f"</td>"
                )

        rows_html += f"<tr>{row_cells}</tr>"

    return (
        '<div class="tt-scroll">'
        '<table class="tt-table">'
        f"<thead><tr>{header_cells}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table></div>"
    )


with tabs[3]:
    subjects = dm.get_subjects()
    exams    = dm.get_exams()
    prefs    = dm.get_preferences()

    if not subjects:
        st.info("Add subjects in the Setup tab to generate a timetable.")
    else:
        col_btn, col_legend = st.columns([2, 3])
        with col_btn:
            if st.button("Generate Timetable", key="btn_gen_tt", type="primary"):
                tt = sc.generate_timetable(subjects, exams, prefs)
                dm.save_timetable(tt)
                st.success("Timetable generated.")
                st.rerun()
        with col_legend:
            st.markdown(
                '<span style="font-size:0.75rem;color:#6b7280;">'
                '<span style="color:#ef4444;">&#9632;</span> Missed &nbsp;&nbsp;'
                '<span style="color:#60a5fa;">&#9632;</span> Rescheduled'
                "</span>",
                unsafe_allow_html=True,
            )

        timetable = dm.get_timetable()
        if timetable:
            st.markdown(_build_timetable_html(timetable), unsafe_allow_html=True)
        else:
            st.info("Click 'Generate Timetable' to create your schedule.")


# ── Tab 5 – Analytics ─────────────────────────────────────────────────────────

with tabs[4]:
    timetable = dm.get_timetable()
    subjects  = dm.get_subjects()
    exams     = dm.get_exams()

    if not timetable:
        st.info("Generate a timetable first to see analytics.")
    else:
        prefs      = dm.get_preferences()
        block_size = prefs["block_size"]

        # Hours per subject (existing calculation — unchanged)
        hours_map: dict[str, float] = {}
        for day, slots in timetable.items():
            for slot in slots:
                subj = slot.get("subject")
                if subj and not slot.get("missed"):
                    hours_map[subj] = hours_map.get(subj, 0) + block_size

        col1, col2 = st.columns([1, 1], gap="large")

        with col1:
            st.markdown('<p class="ss-section">Weekly Hours per Subject</p>', unsafe_allow_html=True)

            # Build a palette that scales to any number of subjects
            _base_colors = ["#3b82f6", "#10b981", "#f59e0b", "#a78bfa",
                            "#f472b6", "#34d399", "#fb923c", "#60a5fa"]
            n = len(hours_map)
            if n <= len(_base_colors):
                bar_colors = _base_colors[:n]
            else:
                # Fall back to evenly spaced colours from a matplotlib colormap
                cmap = plt.get_cmap("tab10")
                bar_colors = [mcolors.to_hex(cmap(i / n)) for i in range(n)]

            fig, ax = plt.subplots(figsize=(5, max(2.2, 0.55 * n)))
            fig.patch.set_facecolor("#1e2028")
            ax.set_facecolor("#1e2028")

            bars = ax.barh(
                list(hours_map.keys()),
                list(hours_map.values()),
                color=bar_colors,
                height=0.55,
            )
            ax.set_xlabel("Hours", color="#9ca3af", fontsize=8)
            ax.tick_params(colors="#9ca3af", labelsize=8)
            for spine in ax.spines.values():
                spine.set_edgecolor("#2a2d36")
            ax.xaxis.label.set_color("#9ca3af")
            ax.set_axisbelow(True)
            ax.xaxis.grid(True, color="#2a2d36", linewidth=0.6)
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with col2:
            st.markdown('<p class="ss-section">Priority Ranking</p>', unsafe_allow_html=True)
            if subjects:
                scored = sorted(
                    [
                        {
                            "Subject":    s["name"],
                            "Difficulty": s["difficulty"],
                            "Priority":   s["priority"],
                            "Score":      sc.score_subject(s, exams),
                        }
                        for s in subjects
                    ],
                    key=lambda x: x["Score"],
                    reverse=True,
                )
                st.dataframe(pd.DataFrame(scored), use_container_width=True, hide_index=True)

        # Exam urgency
        st.markdown('<p class="ss-section">Exam Urgency</p>', unsafe_allow_html=True)
        if exams:
            for exam in sorted(exams, key=lambda e: e["date"]):
                days_left = (date.fromisoformat(exam["date"]) - date.today()).days
                if days_left <= 7:
                    cls, label = "urg-critical", "Critical"
                elif days_left <= 14:
                    cls, label = "urg-soon", "Soon"
                else:
                    cls, label = "urg-upcoming", "Upcoming"
                subj_safe = html.escape(exam["subject"])
                date_safe = html.escape(exam["date"])
                st.markdown(
                    f'<span class="{cls}">{label}</span>'
                    f'&nbsp; <strong>{subj_safe}</strong>'
                    f'<span style="color:#6b7280;font-size:0.8rem;"> — {days_left} day(s) &nbsp;({date_safe})</span>',
                    unsafe_allow_html=True,
                )
        else:
            st.info("No exams scheduled.")


# ── Tab 6 – Reschedule ────────────────────────────────────────────────────────

with tabs[5]:
    timetable = dm.get_timetable()

    if not timetable:
        st.info("Generate a timetable first.")
    else:
        missed = dm.get_missed_sessions()
        st.markdown('<p class="ss-section">Mark Missed Sessions</p>', unsafe_allow_html=True)

        for day in sc.DAYS:
            slots = timetable.get(day, [])
            if not slots:
                continue
            st.markdown(f'<p class="rs-day-label">{html.escape(day)}</p>', unsafe_allow_html=True)
            cols = st.columns(len(slots))
            for i, slot in enumerate(slots):
                label     = slot.get("subject") or "Free"
                is_missed = {"day": day, "slot_index": i} in missed
                with cols[i]:
                    checked = st.checkbox(
                        f"{slot['start']} · {label}",
                        value=is_missed,
                        key=f"miss_{day}_{i}",
                    )
                    if checked and not is_missed:
                        dm.mark_missed(day, i)
                        st.rerun()
                    elif not checked and is_missed:
                        dm.unmark_missed(day, i)
                        st.rerun()

        st.divider()
        if st.button("Reschedule Missed Sessions", key="btn_reschedule", type="primary",
                     use_container_width=True):
            missed      = dm.get_missed_sessions()
            updated_tt  = sc.reschedule_missed(timetable, missed)
            dm.save_rescheduled_timetable(updated_tt)
            st.success("Missed sessions rescheduled. Check the Timetable tab.")
            st.rerun()
