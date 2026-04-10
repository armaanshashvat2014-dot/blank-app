import streamlit as st
import hashlib
import json
import os
import re
import urllib.parse

# --- CONFIGURATION ---
st.set_page_config(page_title="MentorLoop EDU Compass", page_icon="🧭", layout="wide")

# This is your AI Assistant URL
AI_LINK = "https://chatbot-79kdx1gk0gm.streamlit.app/" 
DB_FILE = "database.json"

# --- RESTRICTION SETTINGS ---
# List of non-educational platforms to block
BANNED_PLATFORMS = [
    "facebook.com", "instagram.com", "youtube.com", "tiktok.com", 
    "twitter.com", "x.com", "reddit.com", "netflix.com", 
    "twitch.tv", "snapchat.com", "discord.com"
]

# --- DATABASE LOGIC ---
def load_db():
    if not os.path.exists(DB_FILE): 
        return {"users": {}}
    try:
        with open(DB_FILE, "r") as f: 
            content = f.read()
            return json.loads(content) if content else {"users": {}}
    except Exception: 
        return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f: 
        json.dump(data, f, indent=4)

def hash_pass(p): 
    return hashlib.sha256(str.encode(p)).hexdigest()

# --- AUTH SYSTEM ---
if 'logged_in' not in st.session_state: 
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🧭 MentorLoop EDU Compass")
    st.markdown("### Secure Academic Gateway")
    st.info("Log in to access the AI Research Compass and Educational Browser.")
    
    tab1, tab2 = st.tabs(["Login", "Register"])
    with tab1:
        u = st.text_input("Username", key="login_u")
        p = st.text_input("Password", type="password", key="login_p")
        if st.button("Access Compass"):
            db = load_db()
            if u in db["users"] and db["users"][u] == hash_pass(p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: 
                st.error("Invalid credentials.")
    with tab2:
        nu = st.text_input("New Username", key="reg_u")
        np = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Create Local ID"):
            if nu and np:
                db = load_db()
                db["users"][nu] = hash_pass(np)
                save_db(db)
                st.success("Registered! You can now login.")

# --- MAIN BROWSER & AI INTERFACE ---
else:
    # Sidebar Navigation
    st.sidebar.title("🧭 EDU Compass")
    st.sidebar.write(f"Active User: **{st.session_state.user}**")
    st.sidebar.divider()
    st.sidebar.success("✅ AI Cluster Connected")
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("MentorLoop EDU Compass")
    st.markdown("##### Research Topic, Math, or Website")
    
    user_input = st.text_input("🌐 Enter a question (for AI summary) or a website URL (e.g. 'wikipedia.org' or 'physics concepts')", placeholder="What would you like to explore today?")

    if user_input:
        # 1. CLEANING & LOGIC PREP
        query_lower = user_input.lower().strip()
        
        # 2. CHECK FOR BANNED PLATFORMS
        is_banned = any(platform in query_lower for platform in BANNED_PLATFORMS)
        
        if is_banned:
            st.error("🚫 **Access Denied.** MentorLoop EDU Compass has restricted this platform to maintain an educational focus. Please try a different resource or ask the AI.")
        
        else:
            # 3. DETECT IF INPUT IS A URL OR A QUESTION
            url_pattern = r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'
            is_website = re.search(url_pattern, query_lower) or query_lower.startswith("http")

            if is_website:
                # --- WEBSITE MODE ---
                final_url = user_input if user_input.startswith("http") else "https://" + user_input
                st.caption(f"Navigating to External Resource...")
                
                # Action bar for URLs
                c1, c2 = st.columns([1, 5])
                with c1:
                    st.link_button("🚀 Open Tab", final_url)
                with c2:
                    st.info(f"Viewing: {final_url}")
                
                # Embedded Browser
                st.components.v1.iframe(final_url, height=800, scrolling=True)

            else:
                # --- AI SUMMARY MODE (Your AI App) ---
                # We encode the user question and pass it to your AI app via URL parameter
                encoded_query = urllib.parse.quote(user_input)
                
                # This constructs the link to your specific AI tool with the question attached
                # Assumes your AI app is set up to read st.query_params
                target_ai_url = f"{AI_LINK}?q={encoded_query}"
                
                st.subheader(f"✨ AI Summary: {user_input}")
                st.markdown(f"Fetching integrated analysis from your **Consultant AI**...")

                # Embed your AI app directly so the user sees the answer immediately
                st.components.v1.iframe(target_ai_url, height=900, scrolling=True)
                
                # Back-up option if the iframe is blocked
                st.link_button("💬 Open AI in Full Screen", target_ai_url)

# --- CSS STYLING (Optional for a cleaner look) ---
st.markdown("""
    <style>
    .stTextInput > div > div > input {
        background-color: #f0f2f6;
    }
    </style>
    """, unsafe_allow_html=True)
