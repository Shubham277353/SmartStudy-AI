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
/* ===== SMARTSTUDY DESIGN SYSTEM ===== */

:root {
    --bg: #111318;
    --surface: #191d26;
    --surface-hover: #222735;
    --border: #2a3040;
    --text: #edf0f7;
    --muted: #929bad;
    --accent: #6685ff;
    --accent-soft: rgba(102, 133, 255, 0.13);
}

/* Main application */
html, body, [data-testid="stAppViewContainer"],
[data-testid="stMain"] {
    background: var(--bg);
    color: var(--text);
    font-family: Inter, system-ui, sans-serif;
}

[data-testid="stHeader"] {
    background: var(--bg);
}

[data-testid="stMainBlockContainer"] {
    padding-top: 1.5rem !important;
    padding-bottom: 3rem !important;
    max-width: 1500px;
}

#MainMenu, footer, [data-testid="stToolbar"] {
    display: none !important;
}

/* Typography */
h1 {
    color: var(--text) !important;
    font-size: 2.35rem !important;
    font-weight: 750 !important;
    letter-spacing: -1.2px !important;
}

h2, h3 {
    color: var(--text) !important;
    font-weight: 650 !important;
    letter-spacing: -0.3px;
}

p, label, span {
    color: inherit;
}

/* Header caption */
[data-testid="stCaptionContainer"] {
    color: var(--muted) !important;
    font-size: 0.95rem;
}

/* Tabs */
[data-testid="stTabs"] [role="tablist"] {
    gap: 8px;
    border-bottom: 1px solid var(--border);
}

[data-testid="stTabs"] [role="tab"] {
    color: var(--muted) !important;
    font-size: 0.88rem;
    font-weight: 550;
    padding: 0.75rem 1.1rem;
    border: none !important;
    border-bottom: 2px solid transparent !important;
    background: transparent !important;
    transition: all 0.2s ease;
}

[data-testid="stTabs"] [role="tab"]:hover {
    color: var(--text) !important;
    background: var(--accent-soft) !important;
}

[data-testid="stTabs"] [role="tab"][aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
}

/* Section headings */
.ss-section {
    color: #aeb9d0;
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.11em;
    text-transform: uppercase;
    margin: 1.1rem 0 0.9rem 0;
}

/* Buttons */
[data-testid="stButton"] > button {
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border);
    border-radius: 9px;
    font-size: 0.88rem;
    font-weight: 600;
    padding: 0.55rem 1.15rem;
    min-height: 2.6rem;
    transition: all 0.2s ease;
}

[data-testid="stButton"] > button:hover {
    background: var(--surface-hover);
    border-color: var(--accent);
    color: white;
    transform: translateY(-1px);
}

[data-testid="stButton"] > button[kind="primary"] {
    background: var(--accent);
    color: white;
    border: 1px solid var(--accent);
}

[data-testid="stButton"] > button[kind="primary"]:hover {
    background: #5272ef;
    border-color: #5272ef;
}

/* Text inputs */
[data-testid="stTextInput"] input,
[data-testid="stDateInput"] input {
    background: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 9px !important;
    min-height: 2.7rem;
}

[data-testid="stTextInput"] input:focus,
[data-testid="stDateInput"] input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 2px var(--accent-soft) !important;
}

/* Select boxes */
[data-testid="stSelectbox"] > div > div {
    background: var(--surface) !important;
    border-color: var(--border) !important;
    border-radius: 9px !important;
    color: var(--text) !important;
}

/* Sliders */
[data-testid="stSlider"] [role="slider"] {
    background: var(--accent) !important;
}

/* Checkboxes */
[data-testid="stCheckbox"] label {
    color: var(--text) !important;
}

/* Dataframes */
[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}

/* Alerts */
[data-testid="stAlert"] {
    border-radius: 9px;
    border: 1px solid var(--border);
}

/* Dividers */
hr {
    border-color: var(--border) !important;
}

/* Timetable */
.tt-scroll {
    overflow-x: auto;
    border: 1px solid var(--border);
    border-radius: 12px;
    -webkit-overflow-scrolling: touch;
}

.tt-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 0.82rem;
    min-width: 560px;
}

.tt-table th {
    background: #202635;
    color: #9db0ff;
    font-size: 0.73rem;
    font-weight: 700;
    letter-spacing: 0.07em;
    text-transform: uppercase;
    padding: 13px 10px;
    border: 1px solid var(--border);
    text-align: center;
}

.tt-table th.tt-block-col {
    color: var(--muted);
    min-width: 52px;
}

.tt-table td {
    border: 1px solid var(--border);
    padding: 12px 10px;
    vertical-align: middle;
    text-align: center;
    min-width: 90px;
}

.tt-time {
    font-size: 0.7rem;
    color: var(--muted);
    display: block;
    margin-bottom: 5px;
}

.tt-subj {
    font-size: 0.84rem;
    color: var(--text);
    font-weight: 600;
}

.tt-empty {
    color: #555e70;
    font-size: 0.8rem;
}

.tt-cell-missed {
    background: rgba(239, 68, 68, 0.10);
}

.tt-cell-missed .tt-subj {
    color: #fb7777;
}

.tt-cell-rescheduled {
    background: rgba(102, 133, 255, 0.12);
}

.tt-cell-rescheduled .tt-subj {
    color: #91a7ff;
}

.tt-cell-normal {
    background: var(--surface);
}

.tt-block-label {
    color: var(--muted);
    font-size: 0.72rem;
    font-weight: 600;
}

/* Urgency labels */
.urg-critical {
    color: #fb7777;
    font-weight: 650;
    font-size: 0.8rem;
}

.urg-soon {
    color: #f5bd60;
    font-weight: 650;
    font-size: 0.8rem;
}

.urg-upcoming {
    color: #56d6a0;
    font-weight: 650;
    font-size: 0.8rem;
}

/* Reschedule labels */
.rs-day-label {
    font-size: 0.76rem;
    font-weight: 700;
    letter-spacing: 0.09em;
    text-transform: uppercase;
    color: #9db0ff;
    margin: 1.2rem 0 0.6rem 0;
}
</style>

""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────

st.markdown(
    """
    <div style="
        display: flex;
        align-items: center;
        gap: 14px;
        margin-top: 12px;
        margin-bottom: 8px;
    ">
        <div style="
            background: rgba(102, 133, 255, 0.15);
            border: 1px solid rgba(102, 133, 255, 0.3);
            border-radius: 12px;
            padding: 10px 12px;
            font-size: 25px;
        ">📚</div>
        <div>
            <div style="
                font-size: 2rem;
                font-weight: 750;
                letter-spacing: -1px;
                color: #edf0f7;
            ">SmartStudy <span style="color: #6685ff;">AI</span></div>
            <div style="
                color: #929bad;
                font-size: 0.9rem;
                margin-top: 3px;
            ">Your intelligent study planning assistant</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)
st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────

tabs = st.tabs(["Setup", "Exams", "Preferences", "Timetable", "Analytics", "Reschedule"])



# ── Tab 1 – Setup ─────────────────────────────────────────────────────────────

with tabs[0]:
    subjects = dm.get_subjects()

    st.markdown(
        """
        <div style="margin: 12px 0 22px 0;">
            <div style="font-size: 1.45rem; font-weight: 700;
                        color: #edf0f7; letter-spacing: -0.5px;">
                Manage your subjects
            </div>
            <div style="font-size: 0.88rem; color: #929bad; margin-top: 5px;">
                Add the subjects you want to study and configure their importance.
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([0.9, 1.1], gap="large")

    # LEFT CARD — ADD SUBJECT
    with col1:
        with st.container(border=True):
            st.markdown("### ✨ Add a subject")
            st.caption("Enter the details of a new subject.")

            name = st.text_input(
                "Subject Name",
                key="subj_name",
                placeholder="e.g. Data Structures"
            )

            difficulty = st.selectbox(
                "Difficulty Level",
                ["Easy", "Medium", "Hard"],
                key="subj_diff"
            )

            priority = st.slider(
                "Study Priority",
                1, 5, 3,
                key="subj_prio",
                help="1 = lowest priority, 5 = highest priority"
            )

            priority_labels = {
                1: "Very Low",
                2: "Low",
                3: "Medium",
                4: "High",
                5: "Very High"
            }

            st.caption(f"Selected priority: **{priority_labels[priority]}**")

            st.write("")

            if st.button(
                "＋ Add Subject",
                key="btn_add_subj",
                type="primary",
                use_container_width=True
            ):
                if name.strip():
                    try:
                        dm.add_subject(name.strip(), difficulty, priority)
                        st.success(f"'{name.strip()}' added successfully.")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                else:
                    st.warning("Please enter a subject name.")

    # RIGHT CARD — CURRENT SUBJECTS
    with col2:
        with st.container(border=True):
            st.markdown("### 📚 Your subjects")
            st.caption("Your currently registered study subjects.")


            if subjects:
                df = pd.DataFrame(subjects).rename(columns={
                    "name": "Subject",
                    "difficulty": "Difficulty",
                    "priority": "Priority"
                })

                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                st.divider()

                st.markdown("**Remove a subject**")

                remove_name = st.selectbox(
                    "Select subject",
                    [s["name"] for s in subjects],
                    key="remove_subj",
                    label_visibility="collapsed"
                )

                if st.button(
                    "Remove Subject",
                    key="btn_remove_subj",
                    use_container_width=True
                ):
                    dm.remove_subject(remove_name)
                    st.success(f"'{remove_name}' removed.")
                    st.rerun()

            else:
                st.info("No subjects added yet. Add your first subject using the form.")



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
