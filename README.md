# WellNest — Mood Tracker & Supportive Chat

Privacy-first daily check-ins with a timeline chart, CSV export, and a supportive chat with crisis keyword guardrails (988/911).  
Runs entirely local by default (SQLite). Optional OpenAI key for CBT-style responses.

![Mood timeline](images/mood.png)
![Supportive chat](images/chat.png)

## Tech
- **Streamlit** UI
- **SQLite** persistence
- **Matplotlib** chart
- Optional **OpenAI** (fallback works without any key)

## Run locally
```bash
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python -m streamlit run app.py
