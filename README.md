# WellNest — Mood Tracker & Supportive Chat (100% local)

Privacy-first daily check-ins with a mood timeline, CSV export, and a supportive chat with crisis resources (988/911).  
No sign-in, no cloud, no keys — runs entirely on your device (SQLite + Streamlit).

![Mood timeline](images/mood.png)
![Supportive chat](images/chat.png)

## Run locally
`powershell
python -m venv .venv
.venv\Scripts\Activate
pip install -r requirements.txt
python -m streamlit run app.py

Open the PR on GitHub → **Merge** → back in terminal:

`powershell
git checkout main
git pull
git tag v1.0.0
git push origin --tags

cd C:\Users\Varun\wellnest
.venv\Scripts\Activate

# make sure you have the latest local-only app.py + minimal reqs
ni .gitignore -Value @"
.venv/
__pycache__/
*.pyc
.streamlit/
wellnest.db
.DS_Store
Thumbs.db
.vscode/