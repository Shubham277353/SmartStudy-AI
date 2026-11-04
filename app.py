"""
app.py
------
Main Streamlit application for SmartStudy AI.
All UI lives here; logic is delegated to scheduler.py and data_manager.py.
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import date, timedelta

import data_manager as dm
import scheduler as sc

# ── Page config ───────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="SmartStudy AI",
    page_icon="📚",
    layout="wide",
)

st.title("📚 SmartStudy AI – Student Timetable Assistant")
st.caption("AI-powered rule-based study planner for MCA students")

tabs = st.tabs([
    "🗂 Setup",
    "📅 Exams",
    "⚙️ Preferences",
    "📋 Timetable",
    "📊 Analytics",
    "🔄 Reschedule",
])


# ── Tab 1 – Setup (Subjects) ──────────────────────────────────────────────────

with tabs[0]:
    st.subheader("Manage Subjects")

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("**Add a Subject**")
        name = st.text_input("Subject Name", key="subj_name")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="subj_diff")
        priority = st.slider("Priority (1 = Low, 5 = High)", 1, 5, 3, key="subj_prio")

        if st.button("➕ Add Subject"):
            if name.strip():
                try:
                    dm.add_subject(name.strip(), difficulty, priority)
                    st.success(f"Added '{name.strip()}'")
                    st.rerun()
                except ValueError as e:
                    st.error(str(e))
            else:
                st.warning("Please enter a subject name.")

    with col2:
        st.markdown("**Current Subjects**")
        subjects = dm.get_subjects()
        if subjects:
            df = pd.DataFrame(subjects)
            st.dataframe(df, use_container_width=True, hide_index=True)

            remove_name = st.selectbox(
                "Select subject to remove", [s["name"] for s in subjects], key="remove_subj"
            )
            if st.button("🗑️ Remove Subject"):
                dm.remove_subject(remove_name)
                st.success(f"Removed '{remove_name}'")
                st.rerun()
        else:
            st.info("No subjects added yet.")


# ── Tab 2 – Exams ─────────────────────────────────────────────────────────────

with tabs[1]:
    st.subheader("Exam Dates")

    subjects = dm.get_subjects()
    exams = dm.get_exams()

    if not subjects:
        st.info("Add subjects first in the Setup tab.")
    else:
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("**Schedule an Exam**")
            exam_subject = st.selectbox(
                "Subject", [s["name"] for s in subjects], key="exam_subj"
            )
            min_date = date.today() + timedelta(days=1)
            exam_date = st.date_input("Exam Date", min_value=min_date, key="exam_date")

            if st.button("📌 Save Exam Date"):
                dm.add_exam(exam_subject, str(exam_date))
                st.success(f"Exam for '{exam_subject}' set to {exam_date}")
                st.rerun()

        with col2:
            st.markdown("**Scheduled Exams**")
            if exams:
                df_exams = pd.DataFrame(exams)
                df_exams["days_left"] = df_exams["date"].apply(
                    lambda d: (date.fromisoformat(d) - date.today()).days
                )
                st.dataframe(df_exams, use_container_width=True, hide_index=True)

                remove_exam_subj = st.selectbox(
                    "Remove exam for", [e["subject"] for e in exams], key="remove_exam"
                )
                if st.button("🗑️ Remove Exam"):
                    dm.remove_exam(remove_exam_subj)
                    st.rerun()
            else:
                st.info("No exams scheduled yet.")


# ── Tab 3 – Preferences ───────────────────────────────────────────────────────

with tabs[2]:
    st.subheader("Study Preferences")
    prefs = dm.get_preferences()

    daily_hours = st.slider(
        "Daily Available Study Hours", 1.0, 12.0, float(prefs["daily_hours"]), 0.5
    )
    block_size = st.select_slider(
        "Study Block Size (hours)", options=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0],
        value=float(prefs["block_size"])
    )
    break_minutes = st.slider(
        "Break Between Blocks (minutes)", 5, 30, int(prefs["break_minutes"]), 5
    )

    slots_per_day = int(daily_hours // block_size)
    st.info(
        f"With these settings you'll have **{slots_per_day} study block(s)** per day "
        f"({block_size}h each, {break_minutes}-min breaks)."
    )

    if st.button("💾 Save Preferences"):
        dm.save_preferences(daily_hours, block_size, break_minutes)
        st.success("Preferences saved!")


# ── Tab 4 – Timetable ─────────────────────────────────────────────────────────

with tabs[3]:
    st.subheader("Weekly Study Timetable")

    subjects = dm.get_subjects()
    exams = dm.get_exams()
    prefs = dm.get_preferences()

    if not subjects:
        st.info("Add subjects in the Setup tab to generate a timetable.")
    else:
        if st.button("⚡ Generate Timetable"):
            tt = sc.generate_timetable(subjects, exams, prefs)
            dm.save_timetable(tt)
            st.success("Timetable generated!")
            st.rerun()

        timetable = dm.get_timetable()

        if timetable:
            # Build a display DataFrame: rows = slots, columns = days
            max_slots = max(len(timetable[d]) for d in sc.DAYS if d in timetable)
            rows = []
            for i in range(max_slots):
                row = {}
                for day in sc.DAYS:
                    slots = timetable.get(day, [])
                    if i < len(slots):
                        slot = slots[i]
                        label = slot["subject"] or "—"
                        if slot.get("missed"):
                            label = f"❌ {label}"
                        elif slot.get("rescheduled"):
                            label = f"🔄 {label}"
                        row[day] = f"{slot['start']} | {label}"
                    else:
                        row[day] = ""
                rows.append(row)

            df_tt = pd.DataFrame(rows)
            df_tt.index = [f"Block {i+1}" for i in range(len(rows))]
            st.dataframe(df_tt, use_container_width=True)
        else:
            st.info("Click 'Generate Timetable' to create your schedule.")


# ── Tab 5 – Analytics ─────────────────────────────────────────────────────────

with tabs[4]:
    st.subheader("Study Analytics")

    timetable = dm.get_timetable()
    subjects = dm.get_subjects()
    exams = dm.get_exams()

    if not timetable:
        st.info("Generate a timetable first to see analytics.")
    else:
        prefs = dm.get_preferences()
        block_size = prefs["block_size"]

        # Hours per subject
        hours_map: dict[str, float] = {}
        for day, slots in timetable.items():
            for slot in slots:
                subj = slot.get("subject")
                if subj and not slot.get("missed"):
                    hours_map[subj] = hours_map.get(subj, 0) + block_size

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("**Hours Allocated per Subject**")
            fig, ax = plt.subplots(figsize=(5, 3))
            ax.barh(list(hours_map.keys()), list(hours_map.values()), color="#4C72B0")
            ax.set_xlabel("Hours")
            ax.set_title("Weekly Study Hours")
            plt.tight_layout()
            st.pyplot(fig)
            plt.close(fig)

        with col2:
            st.markdown("**Subject Scores (Priority Ranking)**")
            if subjects:
                scored = sorted(
                    [
                        {
                            "Subject": s["name"],
                            "Difficulty": s["difficulty"],
                            "Priority": s["priority"],
                            "Score": sc.score_subject(s, exams),
                        }
                        for s in subjects
                    ],
                    key=lambda x: x["Score"],
                    reverse=True,
                )
                st.dataframe(pd.DataFrame(scored), use_container_width=True, hide_index=True)

        # Exam urgency indicators
        st.markdown("**Exam Urgency**")
        if exams:
            for exam in sorted(exams, key=lambda e: e["date"]):
                days_left = (date.fromisoformat(exam["date"]) - date.today()).days
                color = "🔴" if days_left <= 7 else "🟡" if days_left <= 14 else "🟢"
                st.write(f"{color} **{exam['subject']}** — {days_left} day(s) until exam ({exam['date']})")
        else:
            st.info("No exams scheduled.")


# ── Tab 6 – Reschedule ────────────────────────────────────────────────────────

with tabs[5]:
    st.subheader("Reschedule Missed Sessions")

    timetable = dm.get_timetable()

    if not timetable:
        st.info("Generate a timetable first.")
    else:
        missed = dm.get_missed_sessions()
        st.markdown("**Mark sessions you missed:**")

        for day in sc.DAYS:
            slots = timetable.get(day, [])
            if not slots:
                continue
            st.markdown(f"*{day}*")
            cols = st.columns(len(slots))
            for i, slot in enumerate(slots):
                label = slot.get("subject") or "Free"
                is_missed = {"day": day, "slot_index": i} in missed
                with cols[i]:
                    checked = st.checkbox(
                        f"{slot['start']}\n{label}",
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
        if st.button("🔄 Reschedule Missed Sessions"):
            missed = dm.get_missed_sessions()
            updated_tt = sc.reschedule_missed(timetable, missed)
            dm.save_rescheduled_timetable(updated_tt)
            st.success("Missed sessions rescheduled! Check the Timetable tab.")
            st.rerun()
