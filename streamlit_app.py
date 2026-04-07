import streamlit as st
import hashlib
import json
import os
import re
import time
from datetime import datetime

# --- CONFIG ---
st.set_page_config(page_title="MentorLoop EDU Compass", page_icon="🧭", layout="wide")
DB_FILE = "database.json"
AI_LINK = "https://chatbot-79kdx1gk0gm.streamlit.app/"

# --- DATABASE (FIXED) ---
def load_db():
    default_db = {
        "users": {},
        "logs": [],
        "blocked": [],
        "exam_mode": False,
        "exam_timer": 0,
        "exam_start": 0
    }

    if not os.path.exists(DB_FILE):
        return default_db

    try:
        with open(DB_FILE, "r") as f:
            data = json.load(f)
    except:
        return default_db

    # 🔥 Auto-fix missing keys
    for key in default_db:
        if key not in data:
            data[key] = default_db[key]

    return data


def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)


def hash_pass(p):
    return hashlib.sha256(str.encode(p)).hexdigest()


db = load_db()

# --- LOGGING (SAFE) ---
def log_activity(user, action, detail):
    if "logs" not in db:
        db["logs"] = []

    db["logs"].append({
        "user": user,
        "action": action,
        "detail": detail,
        "time": str(datetime.now())
    })
    save_db(db)


# --- ROLE ---
def is_teacher(username):
    return username.startswith("teacher_")


# --- SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False


# =====================
# 🔐 AUTH SYSTEM
# =====================
if not st.session_state.logged_in:
    st.title("🧭 MentorLoop EDU Compass")
    st.markdown("### Secure Academic Gateway")

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")

        if st.button("Login"):
            if u in db["users"] and db["users"][u] == hash_pass(p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Invalid credentials")

    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        role = st.selectbox("Role", ["student", "teacher"])

        if st.button("Register"):
            if role == "teacher":
                nu = "teacher_" + nu

            db["users"][nu] = hash_pass(np)
            save_db(db)
            st.success("Registered successfully!")


# =====================
# 🧭 MAIN SYSTEM
# =====================
else:
    user = st.session_state.user

    st.sidebar.title("🧭 EDU Compass")
    st.sidebar.write(f"👤 {user}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # =====================
    # 🧑‍🏫 TEACHER DASHBOARD
    # =====================
    if is_teacher(user):
        st.title("🧑‍🏫 Teacher Dashboard")

        # -------- Logs --------
        st.subheader("📊 Student Activity Logs")
        for log in reversed(db["logs"][-50:]):
            st.write(f"{log['time']} | {log['user']} → {log['action']} ({log['detail']})")

        # -------- Block System --------
        st.subheader("🚫 Manage Blocked Websites")

        new_block = st.text_input("Enter site (e.g. youtube.com)")

        if st.button("Add Block"):
            if new_block and new_block not in db["blocked"]:
                db["blocked"].append(new_block)
                save_db(db)
                st.success("Site blocked!")

        st.write("### Currently Blocked:")
        for site in db["blocked"]:
            col1, col2 = st.columns([3, 1])
            col1.write(site)
            if col2.button(f"Remove {site}"):
                db["blocked"].remove(site)
                save_db(db)
                st.rerun()

        # -------- Exam Mode --------
        st.subheader("🧪 Exam Mode Control")

        exam_time = st.number_input("Set Exam Time (minutes)", min_value=1, max_value=180)

        if st.button("Start Exam Mode"):
            db["exam_mode"] = True
            db["exam_timer"] = exam_time * 60
            db["exam_start"] = time.time()
            save_db(db)
            st.success("Exam Mode Activated!")

        if st.button("Stop Exam Mode"):
            db["exam_mode"] = False
            save_db(db)
            st.warning("Exam Mode Stopped")

        # -------- Report --------
        st.subheader("📈 Weekly Report")

        user_stats = {}
        for log in db["logs"]:
            u = log["user"]
            user_stats[u] = user_stats.get(u, 0) + 1

        st.bar_chart(user_stats)
        st.info("Focus Score = Activity Count")

    # =====================
    # 🎓 STUDENT SIDE
    # =====================
    else:

        # -------- EXAM MODE LOCK --------
        if db.get("exam_mode"):
            st.title("🧪 EXAM MODE ACTIVE")

            remaining = int(db["exam_timer"] - (time.time() - db["exam_start"]))

            if remaining <= 0:
                st.error("⏰ Exam Finished")
                db["exam_mode"] = False
                save_db(db)
                st.stop()

            mins = remaining // 60
            secs = remaining % 60

            st.warning(f"⏳ Time Left: {mins}:{secs:02d}")

            answer = st.text_area("✍️ Enter your answer here:")

            if st.button("Submit Answer"):
                log_activity(user, "exam_submission", answer)
                st.success("Submitted successfully!")

            st.stop()

        # -------- NORMAL BROWSER --------
        st.title("🌐MentorLoop EDU Compass")

        query = st.text_input("Search or Enter URL")

        if query:
            log_activity(user, "search", query)

            # Block check
            for site in db.get("blocked", []):
                if site.lower() in query.lower():
                    st.error("🚫 This site is blocked by your teacher.")
                    log_activity(user, "blocked_attempt", query)
                    st.stop()

            url_pattern = r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'
            is_url = re.search(url_pattern, query)

            if is_url:
                url = query if query.startswith("http") else "https://" + query
                log_activity(user, "visit", url)

                st.success(f"Opening: {url}")
                st.link_button("🚀 Open Website", url)
                st.components.v1.iframe(url, height=600)

            else:
                st.success(f"📘 Learning about: {query}")
                st.link_button("✨ Explain with AI", f"{AI_LINK}?q={query}")

        # -------- STUDENT REPORT --------
        st.subheader("📊 Your Weekly Report")

        my_logs = [l for l in db["logs"] if l["user"] == user]

        st.write(f"Total Activity: {len(my_logs)}")

        focus_score = min(100, len(my_logs) * 2)
        st.progress(focus_score)

        st.write(f"Focus Score: {focus_score}/100")
