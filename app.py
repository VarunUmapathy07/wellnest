import os
import sqlite3
from contextlib import contextmanager
from datetime import date

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Optional OpenAI; app runs without it
try:
    from openai import OpenAI
except Exception:
    OpenAI = None

DB_PATH = os.path.join(os.path.dirname(__file__), "wellnest.db")

# ---------------- DB helpers ----------------
@contextmanager
def get_conn():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    try:
        yield conn
    finally:
        conn.commit()
        conn.close()

def init_db():
    with get_conn() as conn:
        cur = conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS mood_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ts TEXT NOT NULL,
                mood INTEGER NOT NULL CHECK(mood BETWEEN 1 AND 5),
                sleep_hours REAL,
                study_hours REAL,
                note TEXT
            )
        """)

def insert_entry(ts, mood, sleep_hours, study_hours, note):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO mood_entries (ts, mood, sleep_hours, study_hours, note) VALUES (?, ?, ?, ?, ?)",
            (ts, mood, sleep_hours, study_hours, note)
        )

def fetch_entries():
    with get_conn() as conn:
        df = pd.read_sql_query("SELECT * FROM mood_entries ORDER BY ts ASC, id ASC", conn)
    return df

def delete_last_entry():
    with get_conn() as conn:
        conn.execute("DELETE FROM mood_entries WHERE id = (SELECT MAX(id) FROM mood_entries)")

def clear_all_entries():
    with get_conn() as conn:
        conn.execute("DELETE FROM mood_entries")

# ---------------- Safety / AI ----------------
CRISIS_KEYWORDS = [
    "suicide","kill myself","end my life","self harm","overdose","harm myself",
    "i want to die","hurt myself","cut myself","jump off","no reason to live"
]

def looks_like_crisis(text: str) -> bool:
    t = (text or "").lower()
    return any(k in t for k in CRISIS_KEYWORDS)

def render_crisis_banner():
    st.error("If you are in crisis or thinking about harming yourself, please seek immediate help.")
    st.markdown(
        "- **United States:** Call or text **988** (Suicide & Crisis Lifeline) • 24/7  \n"
        "- **Emergency:** Dial **911**  \n"
        "- **Crisis Text Line:** Text **HOME** to **741741**"
    )

def therapist_response(user_text: str, model: str = "gpt-4o-mini", system_style: str = "supportive"):
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or OpenAI is None:
        tips = [
            "Try a 4-7-8 breath: inhale 4, hold 7, exhale 8.",
            "Grounding: name 3 things you see, 2 you can touch, 1 you can hear.",
            "Pick one small action you can finish in 10 minutes."
        ]
        return ("I hear you. It sounds like a lot. Here are a few gentle steps you might try: "
                f"{tips[0]}  •  {tips[1]}  •  {tips[2]}")

    try:
        client = OpenAI(api_key=api_key)
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role":"system","content":f"You are a brief, {system_style} CBT-style assistant. Avoid medical claims; encourage professional help as needed."},
                {"role":"user","content":user_text}
            ],
            temperature=0.3,
            max_tokens=300
        )
        return resp.choices[0].message.content.strip()
    except Exception:
        return ("(Local) I can't reach the AI service right now, but I'm here to help reflect. "
                "Consider a small action you can take in the next 10 minutes that aligns with your values.")

# ---------------- Form state helpers (use callbacks) ----------------
DEFAULTS = {"dt": date.today(), "mood": 3, "sleep": 7.0, "study": 2.0, "note": ""}

def ensure_defaults():
    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)

def reset_form():
    for k, v in DEFAULTS.items():
        st.session_state[k] = v
    st.rerun()

def save_current_entry():
    ss = st.session_state
    insert_entry(str(ss.dt), int(ss.mood), float(ss.sleep), float(ss.study), ss.note.strip())
    reset_form()  # will rerun

# ---------------- App ----------------
def main():
    st.set_page_config(page_title="WellNest: Mood & Support", layout="centered")
    init_db()

    st.markdown(
        "<h1 style='text-align:center;margin-bottom:0'>WellNest</h1>"
        "<p style='text-align:center;color:#888;margin-top:4px'>Mood tracking + supportive chat (privacy-first)</p>",
        unsafe_allow_html=True
    )
    st.caption("This tool is not medical care. If you're in crisis, use the resources listed below.")

    tab1, tab2 = st.tabs(["📈 Mood Tracker", "💬 Supportive Chat (AI)"])

    # ---------- Mood Tracker ----------
    with tab1:
        ensure_defaults()

        st.subheader("Log your day")
        col1, col2 = st.columns(2)

        with col1:
            st.date_input("Date", value=st.session_state.dt, key="dt")
            st.slider("Mood (1 = low, 5 = high)", 1, 5, st.session_state.mood, key="mood")
        with col2:
            st.number_input("Sleep (hours)", 0.0, 24.0, st.session_state.sleep, 0.5, key="sleep")
            st.number_input("Study/Focus (hours)", 0.0, 24.0, st.session_state.study, 0.5, key="study")

        st.text_area("Notes (optional)", key="note")

        save_col, clear_col = st.columns([3,1])
        with save_col:
            st.button("💾 Save entry", use_container_width=True, on_click=save_current_entry)
        with clear_col:
            st.button("🧹 Clear form", use_container_width=True, on_click=reset_form)

        st.divider()
        st.subheader("Your timeline")

        df = fetch_entries()
        if df.empty:
            st.info("No entries yet. Add your first one above.")
        else:
            st.dataframe(df.drop(columns=["id"]), use_container_width=True)

            csv_bytes = df.drop(columns=["id"]).to_csv(index=False).encode("utf-8")
            st.download_button("⬇️ Export CSV", data=csv_bytes, file_name="wellnest_moods.csv", mime="text/csv")

            with st.expander("Manage data"):
                st.button("↩️ Delete last entry", on_click=delete_last_entry)
                sure = st.checkbox("I'm sure — delete **ALL** entries")
                st.button("🗑️ Clear all entries", type="secondary", disabled=not sure, on_click=clear_all_entries)

            try:
                df_plot = df.copy()
                df_plot["ts"] = pd.to_datetime(df_plot["ts"])
                df_plot = df_plot.sort_values("ts")

                fig, ax = plt.subplots()
                ax.plot(df_plot["ts"], df_plot["mood"], marker="o", linestyle="-")
                ax.set_title("Mood over time")
                ax.set_xlabel("Date")
                ax.set_ylabel("Mood (1–5)")

                locator = mdates.AutoDateLocator()
                formatter = mdates.ConciseDateFormatter(locator)
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(formatter)
                fig.autofmt_xdate()

                st.pyplot(fig)
            except Exception as e:
                st.warning(f"Couldn't render chart: {e}")

    # ---------- Supportive Chat ----------
    with tab2:
        st.subheader("Supportive Chat")
        st.write("Private by default; no PII logging. Enter your **OpenAI API key** in Settings to use AI, or use the local helper.")

        with st.expander("Settings"):
            key = st.text_input("OPENAI_API_KEY (optional)", type="password")
            if key:
                os.environ["OPENAI_API_KEY"] = key

        user_text = st.text_area("What's on your mind?", height=140)

        if user_text and looks_like_crisis(user_text):
            render_crisis_banner()

        if st.button("Send", use_container_width=True):
            with st.spinner("Thinking..."):
                reply = therapist_response(user_text)
                st.write(reply)

if __name__ == "__main__":
    main()
