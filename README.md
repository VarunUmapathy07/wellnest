# WellNest — Mood Tracker & Supportive Chat (100% Local)

**Privacy-first wellness tracker built with Streamlit + SQLite.**  
Log your daily mood, sleep, and study time, visualize trends, export to CSV, and chat with a supportive offline assistant — all stored locally on your device.

No sign-in, no cloud, no API keys — everything runs on your computer.

---

**Demo Video:** [Watch on YouTube](https://youtu.be/NWBWtQHVDMU)

---

## Features
- Daily logging — mood, sleep, study/focus hours, and notes  
- Timeline chart — auto-formatted date axis for easy tracking  
- CSV export — full data ownership, one click  
- Crisis guardrails — shows 988/911 resources on unsafe phrases  
- Supportive chat — grounding and reflection tips, works fully offline  
- Local persistence — SQLite database (no external servers)

---

## Run Locally

### 1. Set up environment
```powershell
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
2. Run the app
powershell
Copy code
python -m streamlit run app.py
Then open your browser at http://localhost:8501

Tech Stack
Streamlit — front-end UI

SQLite — local database

Matplotlib — charting

Python 3.12+ — runtime environment

Privacy & Safety
Runs entirely on your local machine

No accounts, network calls, or external APIs

Data stored in wellnest.db (git-ignored)

Automatically shows crisis resources when unsafe text is detected

Build Timeline (Retrospective + Ongoing)
Oct 21 2025 — Rebuilt WellNest as 100% local app; added crisis banner and readable chart

Oct 22 2025 — Added form reset and data-management tools

Oct 23 2025 — Recorded demo video and refined README

License
MIT License © 2025 Varun Umapathy
Fork or adapt for educational and personal use.

Links
Demo Video: https://youtu.be/NWBWtQHVDMU

GitHub Repo: https://github.com/VarunUmapathy07/wellnest