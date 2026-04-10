
import streamlit as st
import hashlib
import json
import os
import re
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="MentorLoop EDU Compass", page_icon="🧭", layout="wide")

AI_LINK = "https://chatbot-79kdx1gk0gm.streamlit.app/"
DB_FILE = "database.json"

BANNED_PLATFORMS = ["facebook.com", "instagram.com", "youtube.com", "tiktok.com", "twitter.com", "x.com", "reddit.com", "netflix.com", "twitch.tv", "snapchat.com", "discord.com"]

# --- PRIMARY GRADE KNOWLEDGE ENGINE ---
def primary_tutor_engine(query):
    query = query.lower().strip()
    
    # 1. Handle Basic Arithmetic (Math)
    # Matches patterns like "5 + 5" or "10 divided by 2"
    math_match = re.search(r'(\d+)\s*([\+\-\*\/]|plus|minus|times|divided by)\s*(\d+)', query)
    if math_match:
        num1 = float(math_match.group(1))
        op = math_match.group(2)
        num2 = float(math_match.group(3))
        
        if op in ['+', 'plus']: res = num1 + num2
        elif op in ['-', 'minus']: res = num1 - num2
        elif op in ['*', 'times']: res = num1 * num2
        elif op in ['/', 'divided by']: res = num1 / num2 if num2 != 0 else "Undefined (cannot divide by zero)"
        return f"🍎 **Math Result:** {num1} {op} {num2} = **{res}**"

    # 2. Basic Science/Geography Facts
    facts = {
        "color of the sky": "The sky usually looks **blue** during the day because of how sunlight interacts with the atmosphere!",
        "biggest planet": "The biggest planet in our solar system is **Jupiter**.",
        "capital of usa": "The capital of the United States is **Washington, D.C.**",
        "water freeze": "Water freezes at **32°F (0°C)**.",
        "how many legs does a spider have": "Spiders have **8 legs**, while insects have 6!",
        "who was the first president": "The first president of the United States was **George Washington**."
    }
    
    for key in facts:
        if key in query:
            return f"💡 **Did you know?** {facts[key]}"
            
    return None

# --- DATABASE LOGIC ---
def load_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    try:
        with open(DB_FILE, "r") as f:
            content = f.read()
            return json.loads(content) if content else {"users": {}}
    except: return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- AUTH SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🧭 MentorLoop EDU Compass")
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Access Compass"):
            db = load_db()
            if u in db["users"] and db["users"][u] == hash_pass(p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Invalid credentials.")
    with tab2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Create Local ID"):
            if nu and np:
                db = load_db()
                db["users"][nu] = hash_pass(np)
                save_db(db)
                st.success("Registered!")

# --- MAIN INTERFACE ---
else:
    st.sidebar.title("🧭 EDU Compass")
    st.sidebar.write(f"Active User: **{st.session_state.user}**")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("MentorLoop EDU Compass")
    user_input = st.text_input("🌐 Ask a question or enter a website URL", placeholder="e.g., '15 + 25' or 'Why is the sky blue?'")

    if user_input:
        query_lower = user_input.lower().strip()
        is_banned = any(platform in query_lower for platform in BANNED_PLATFORMS)

        if is_banned:
            st.error("🚫 **Access Denied.** Educational focus only.")
        else:
            # CHECK PRIMARY TUTOR ENGINE FIRST
            primary_answer = primary_tutor_engine(user_input)
            
            if primary_answer:
                st.success("🏫 **Primary Tutor Response:**")
                st.subheader(primary_answer)
                st.balloons() # Fun effect for younger students
            
            else:
                # DETECT IF URL OR COMPLEX QUESTION
                url_pattern = r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'
                is_website = re.search(url_pattern, query_lower) or query_lower.startswith("http")

                if is_website:
                    final_url = user_input if user_input.startswith("http") else "https://" + user_input
                    st.info(f"Navigating to: {final_url}")
                    st.components.v1.iframe(final_url, height=800, scrolling=True)
                else:
                    # AI RESEARCH MODE
                    encoded_query = urllib.parse.quote(user_input)
                    target_ai_url = f"{AI_LINK}?q={encoded_query}"
                    st.subheader(f"✨ AI Analysis: {user_input}")
                    st.components.v1.iframe(target_ai_url, height=800, scrolling=True)
