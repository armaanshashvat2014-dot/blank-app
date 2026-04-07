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

# --- DATABASE ---
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

# --- LOGGING ---
def log_activity(user, action, detail):
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

# --- RECOMMENDATION SYSTEM ---
def get_recommendations(user):
    logs = db.get("logs", [])
    user_logs = [l["detail"].lower() for l in logs if l["user"] == user]

    recs = []

    for q in user_logs:
        if any(w in q for w in ["math", "algebra", "geometry"]):
            recs.append(("Khan Academy", "https://www.khanacademy.org"))

        if any(w in q for w in ["science", "physics", "biology"]):
            recs.append(("National Geographic", "https://www.nationalgeographic.com"))

        if any(w in q for w in ["history", "ancient", "war"]):
            recs.append(("Wikipedia", "https://www.wikipedia.org"))

        if any(w in q for w in ["coding", "python", "ai"]):
            recs.append(("Coursera", "https://www.coursera.org"))

    return list(dict.fromkeys(recs))[:5]

# --- SESSION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# =====================
# 🔐 LOGIN
# =====================
if not st.session_state.logged_in:
    st.title("🧭 MentorLoop EDU Compass")

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
            st.success("Registered!")

# =====================
# 🧭 MAIN
# =====================
else:
    user = st.session_state.user

    # SIDEBAR
    st.sidebar.title("🧭 EDU Compass")
    st.sidebar.write(f"👤 {user}")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # 📚 LEARNING APPS
    st.sidebar.markdown("## 📚 Learning Apps")

    apps = {
        "Khan Academy": "https://www.khanacademy.org",
        "MentorLoop EDU":"https://armaanshashvat2014dot.github.io/MentorLoop-EDU/",
        "Wikipedia": "https://www.wikipedia.org",
        "National Geographic": "https://www.nationalgeographic.com"
    }

    selected_app = st.sidebar.radio("Open App", list(apps.keys()))

    if st.sidebar.button("Launch App"):
        st.session_state.selected_url = apps[selected_app]

    # 🎯 PERSONAL RECOMMENDATIONS
    st.sidebar.markdown("## 🎯 Recommended for You")

    recs = get_recommendations(user)

    if recs:
        for name, link in recs:
            if st.sidebar.button(f"👉 {name}"):
                st.session_state.selected_url = link
    else:
        st.sidebar.write("Start learning to get recommendations 🚀")

    # =====================
    # 🧑‍🏫 TEACHER
    # =====================
    if is_teacher(user):
        st.title("🧑‍🏫 Teacher Dashboard")

        st.subheader("📊 Logs")
        for log in reversed(db["logs"][-50:]):
            st.write(f"{log['user']} → {log['action']} ({log['detail']})")

        st.subheader("🚫 Block Sites")
        site = st.text_input("Site")

        if st.button("Block"):
            if site not in db["blocked"]:
                db["blocked"].append(site)
                save_db(db)

        for s in db["blocked"]:
            if st.button(f"Remove {s}"):
                db["blocked"].remove(s)
                save_db(db)
                st.rerun()

        st.subheader("🧪 Exam Mode")
        t = st.number_input("Minutes", 1, 180)

        if st.button("Start Exam"):
            db["exam_mode"] = True
            db["exam_timer"] = t * 60
            db["exam_start"] = time.time()
            save_db(db)

        if st.button("Stop Exam"):
            db["exam_mode"] = False
            save_db(db)

    # =====================
    # 🎓 STUDENT
    # =====================
    else:

        # EXAM MODE
        if db.get("exam_mode"):
            st.title("🧪 EXAM MODE")

            remaining = int(db["exam_timer"] - (time.time() - db["exam_start"]))

            if remaining <= 0:
                st.error("⏰ Time up")
                db["exam_mode"] = False
                save_db(db)
                st.stop()

            st.warning(f"⏳ {remaining//60}:{remaining%60:02d}")

            ans = st.text_area("Answer")

            if st.button("Submit"):
                log_activity(user, "exam", ans)
                st.success("Submitted")

            st.stop()

        # MAIN UI
        st.title("🌐 Smart EDU Browser")

        # OPEN SELECTED APP
        if "selected_url" in st.session_state:
            st.components.v1.iframe(st.session_state.selected_url, height=500)

        mode = st.radio("Mode", ["🔍 Search", "💬 Chat"])

        query = st.text_input("Search or Ask")

        # CHAT MODE
        if mode == "💬 Chat":
            st.components.v1.iframe(AI_LINK, height=700)

        # SEARCH MODE
        else:
            if query:
                log_activity(user, "search", query)

                # MATH
                if re.match(r"^[0-9\+\-\*\/\(\)\.\s]+$", query):
                    try:
                        res = eval(query, {"__builtins__": None}, {})
                        st.success(f"🔢 Answer: {res}")
                        st.stop()
                    except:
                        pass

                # BLOCK
                for s in db["blocked"]:
                    if s.lower() in query.lower():
                        st.error("🚫 This site is blocked")
                        st.stop()

                # URL
                if re.search(r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', query):
                    url = query if query.startswith("http") else "https://" + query
                    st.components.v1.iframe(url, height=500)

                else:
                    st.subheader(f"🧠 AI Answer: {query}")
                    st.components.v1.iframe(f"{AI_LINK}?q={query}", height=700)

        # REPORT
        logs = [l for l in db["logs"] if l["user"] == user]
        st.subheader("📊 Report")
        st.write(f"Activity: {len(logs)}")
        st.progress(min(100, len(logs)*2))
