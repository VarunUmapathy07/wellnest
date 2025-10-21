# WellNest (Streamlit)
A single-page app with two tabs:
- **Mood Tracker:** log mood/sleep/study notes to a local SQLite DB + simple chart
- **Supportive Chat (AI):** optional OpenAI-powered, CBT-style reflections with crisis keyword guardrails

> This tool is *not* medical care.

## Quick start
```bash
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
streamlit run app.py
