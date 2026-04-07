import streamlit as st
import hashlib
import json
import os
import re

# --- CONFIGURATION ---
st.set_page_config(page_title="MentorLoop EDU Compass", page_icon="🧭", layout="wide")
DB_FILE = "database.json"
AI_LINK = "https://chatbot-79kdx1gk0gm.streamlit.app/"

# --- DATABASE LOGIC ---
def load_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- THE COMPASS ENGINES ---
def process_query(q):
    q_clean = q.lower().strip()
    
    # 1. MATH ENGINE
    if re.match(r"^[0-9\+\-\*\/\(\)\s\.]+$", q_clean):
        try:
            res = eval(q_clean, {"__builtins__": None}, {})
            return f"🔢 **Calculation Result:** {res}", "Mathematics"
        except: pass

    # 2. DEFINITION ENGINE
    knowledge = {
        "science": "The systematic study of the physical and natural world.",
        "math": "The study of numbers, quantity, and space.",
        "extermination": "Biological: Total removal of pests. Historical: Systematic mass killing.",
        "physics": "The science of matter, energy, and motion.",
        "biology": "The study of living organisms.",
        "chemistry": "The science of substances and their reactions."
    }
    
    if q_clean in knowledge:
        return knowledge[q_clean], q_clean.capitalize()
    
    return f"MentorLoop EDU Compass has indexed '{q}' under general academic studies.", "General Inquiry"

# --- AUTH SYSTEM ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🧭 MentorLoop EDU Compass")
    st.markdown("### Secure Academic Gateway")
    
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
            else: st.error("Invalid credentials.")
    with tab2:
        nu = st.text_input("New Username", key="reg_u")
        np = st.text_input("New Password", type="password", key="reg_p")
        if st.button("Create Local ID"):
            if nu and np:
                db = load_db()
                db["users"][nu] = hash_pass(np)
                save_db(db)
                st.success("Registered! You can now login.")

# --- BROWSER INTERFACE ---
else:
    # Sidebar
    st.sidebar.title("🧭 EDU Compass")
    st.sidebar.write(f"Active User: **{st.session_state.user}**")
    
    st.sidebar.write("### AI INTEGRATION")
    # Verified direct link for AI Assistant
    st.sidebar.link_button("✨ Launch AI Assistant", AI_LINK, use_container_width=True)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Main Browser Interface
    st.title("MentorLoop EDU Compass")
    user_input = st.text_input("🌐 Enter Topic, Math, or URL (e.g. wikipedia.org, 12*12, or science)")

    if user_input:
        # --- SMART URL PARSER ---
        # Detects if input looks like a website (has .org, .com, .io, .net, etc.)
        url_pattern = r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'
        is_url = re.search(url_pattern, user_input) or user_input.startswith("http")

        if is_url:
            # Auto-format to include https:// if missing
            final_url = user_input if user_input.startswith("http") else "https://" + user_input
            
            st.success(f"Navigating to: {final_url}")
            
            # Action Buttons for URLs
            c1, c2 = st.columns(2)
            with c1:
                st.link_button(f"🚀 Open Website: {user_input}", final_url, use_container_width=True)
            with c2:
                # Direct AI analysis of the URL
                st.link_button("✨ Analyze with AI", f"{AI_LINK}?target={final_url}", use_container_width=True)
            
            st.info("Direct View (If the panel below is blank, the site has security blocking. Use the 'Open Website' button above.)")
            st.components.v1.iframe(final_url, height=700, scrolling=True)
        
        else:
            # --- TOPIC / MATH MODE ---
            result, category = process_query(user_input)
            
            st.markdown(f"""
                <div style="background-color: #fcfcfc; padding: 25px; border-radius: 12px; border: 1px solid #ddd; color: black; box-shadow: 2px 2px 10px rgba(0,0,0,0.05);">
                    <small style="color: grey;">Compass Indexing: {category}</small>
                    <h2 style="color: #1a73e8; margin-top: 5px;">{user_input.upper()}</h2>
                    <hr>
                    <p style="font-size: 20px; line-height: 1.5;">{result}</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            # Deep dive link
            st.link_button(f"🔍 Deep AI Analysis for {user_input}", f"{AI_LINK}?q={user_input}")
