# app.py — WellNest (100% local, no OpenAI)
import os
import sqlite3
from contextlib import contextmanager
from datetime import date

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

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
        conn.execute("""
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

# ---------------- Safety / local chat ----------------
CRISIS_KEYWORDS = [
    # direct self-harm phrases
    "suicide","kill myself","end my life","self harm","overdose","harm myself",
    "i want to die","hurt myself","cut myself","jump off","no reason to live",
    # feeling unsafe / hopeless
    "i dont feel safe","i don't feel safe","not safe","no longer safe",
    "i feel hopeless","cant go on","can't go on","nothing matters","give up"
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

def local_supportive_reply(_: str) -> str:
    tips = [
        "Try a 4-7-8 breath: inhale 4, hold 7, exhale 8.",
        "Grounding: name 3 things you see, 2 you can touch, 1 you can hear.",
        "Pick one small action you can finish in 10 minutes."
    ]
    return (
        "I hear you. It sounds like a lot. Here are a few gentle steps you might try: "
        f"{tips[0]}  •  {tips[1]}  •  {tips[2]}"
    )

# ---------------- App ----------------
DEFAULTS = {"dt": date.today(), "mood": 3, "sleep": 7.0, "study": 2.0, "note": ""}

def main():
    st.set_page_config(page_title="WellNest: Mood & Support", layout="centered")
    init_db()

    st.markdown(
        "<h1 style='text-align:center;margin-bottom:0'>WellNest</h1>"
        "<p style='text-align:center;color:#888;margin-top:4px'>Mood tracking + supportive chat (privacy-first, 100% local)</p>",
        unsafe_allow_html=True
    )
    st.caption("This tool is not medical care. If you're in crisis, use the resources listed below.")

    for k, v in DEFAULTS.items():
        st.session_state.setdefault(k, v)

    tab1, tab2 = st.tabs(["📈 Mood Tracker", "💬 Supportive Chat"])

    # ---------- Mood Tracker ----------
    with tab1:
        st.subheader("Log your day")

        # form to avoid rerun warnings
        with st.form("log_form", clear_on_submit=False):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state.dt = st.date_input("Date", value=st.session_state.dt)
                st.session_state.mood = st.slider("Mood (1 = low, 5 = high)", 1, 5, st.session_state.mood)
            with col2:
                st.session_state.sleep = st.number_input("Sleep (hours)", 0.0, 24.0, st.session_state.sleep, 0.5)
                st.session_state.study = st.number_input("Study/Focus (hours)", 0.0, 24.0, st.session_state.study, 0.5)

            st.session_state.note = st.text_area("Notes (optional)", value=st.session_state.note)

            save_col, clear_col = st.columns([3,1])
            with save_col:
                save_clicked = st.form_submit_button("💾 Save entry", use_container_width=True)
            with clear_col:
                clear_clicked = st.form_submit_button("🧹 Clear form", use_container_width=True)

        if save_clicked:
            insert_entry(
                str(st.session_state.dt),
                int(st.session_state.mood),
                float(st.session_state.sleep),
                float(st.session_state.study),
                st.session_state.note.strip()
            )
            st.toast("Saved ✅", icon="✅")

        if clear_clicked:
            for k, v in DEFAULTS.items():
                st.session_state[k] = v
            st.toast("Form cleared 🧹", icon="🧹")

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
                if st.button("↩️ Delete last entry"):
                    delete_last_entry()
                    st.success("Deleted last entry.")
                sure = st.checkbox("I'm sure — delete **ALL** entries")
                if st.button("🗑️ Clear all entries", type="secondary", disabled=not sure):
                    clear_all_entries()
                    st.success("All entries cleared.")

            # Plot with readable date ticks
            try:
                df_plot = df.copy()
                df_plot["ts"] = pd.to_datetime(df_plot["ts"]).dt.date
                df_plot = df_plot.sort_values("ts")

                fig, ax = plt.subplots(figsize=(6.5, 3.5))
                ax.plot(df_plot["ts"], df_plot["mood"], marker="o", linestyle="-")
                ax.set_title("Mood over time")
                ax.set_xlabel("Date")
                ax.set_ylabel("Mood (1–5)")
                ax.set_ylim(1, 5)

                locator = mdates.AutoDateLocator(minticks=3, maxticks=6)
                formatter = mdates.ConciseDateFormatter(locator)
                ax.xaxis.set_major_locator(locator)
                ax.xaxis.set_major_formatter(formatter)
                fig.autofmt_xdate()

                st.pyplot(fig)
            except Exception as e:
                st.warning(f"Couldn't render chart: {e}")

    # ---------- Supportive Chat (local only) ----------
    with tab2:
        st.subheader("Supportive Chat")
        st.write("Private by default; no PII logging. Replies are generated locally with simple supportive tips (no internet required).")

        user_text = st.text_area("What's on your mind?", height=140)

        if user_text and looks_like_crisis(user_text):
            render_crisis_banner()

        if st.button("Send", use_container_width=True):
            with st.spinner("Thinking..."):
                reply = local_supportive_reply(user_text)
                st.write(reply)

if __name__ == "__main__":
    main()
