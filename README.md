# 📚 SmartStudy AI – AI-Based Student Timetable Assistant

A rule-based intelligent study planner built with Python and Streamlit.
Designed as an MCA mini project — functional, demonstrable, and beginner-friendly.

---

## Features

- Add subjects with difficulty levels (Easy / Medium / Hard) and priority ratings
- Schedule upcoming exam dates per subject
- Set daily available study hours and block sizes
- Auto-generate a personalized weekly timetable
- Prioritizes subjects by exam urgency, difficulty, and priority
- View analytics: hours per subject, priority scores, exam urgency
- Mark and reschedule missed study sessions

---

## Project Structure

```
SmartStudy-AI/
├── app.py              # Streamlit UI — all tabs and user interaction
├── scheduler.py        # Scheduling algorithm — scoring, slot generation, rescheduling
├── data_manager.py     # Data layer — read/write local JSON storage
├── data/
│   └── study_data.json # Auto-created local data file
├── requirements.txt
└── README.md
```

---

## Setup & Run

### 1. Clone or download the project

```bash
cd SmartStudy-AI
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

---

## How to Use

| Step | Tab | Action |
|------|-----|--------|
| 1 | 🗂 Setup | Add your subjects with difficulty and priority |
| 2 | 📅 Exams | Enter exam dates for each subject |
| 3 | ⚙️ Preferences | Set your daily study hours and block size |
| 4 | 📋 Timetable | Click "Generate Timetable" |
| 5 | 📊 Analytics | View hours allocation and urgency indicators |
| 6 | 🔄 Reschedule | Mark missed sessions and redistribute them |

---

## Scheduling Algorithm

Each subject receives a composite score:

```
score = (urgency × 0.5) + (difficulty × 0.3) + (priority × 0.2)
```

- **Urgency** — inverse of days until exam (closer = higher score)
- **Difficulty** — Easy=0, Medium=0.5, Hard=1
- **Priority** — user-defined 1–5 scale, normalised to 0–1

Subjects are ranked by score and distributed proportionally across the week's available time slots.

---

## Tech Stack

| Library | Purpose |
|---------|---------|
| Streamlit | Web UI |
| Pandas | Data display (DataFrames) |
| Matplotlib | Bar charts in Analytics tab |
| Python stdlib | JSON storage, date arithmetic |

---

## Data Storage

All data is stored locally in `data/study_data.json`. No database, no internet connection required.
