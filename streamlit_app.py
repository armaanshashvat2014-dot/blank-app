import streamlit as st
import hashlib
import json
import os
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="MentorLoop EDU Compass", page_icon="🧭", layout="wide")

DB_FILE = "database.json"

# --- DATABASE LOGIC ---
def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": {}}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

def hash_pass(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

# --- SESSION STATE ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""

# --- UI: LOGIN & REGISTRATION ---
def show_auth():
    st.title("🧭 MentorLoop EDU Compass")
    st.markdown("### *Navigate the Future of Education*")
    
    tab1, tab2 = st.tabs(["Login", "Register Account"])
    
    with tab1:
        u = st.text_input("Username", key="l_user")
        p = st.text_input("Password", type="password", key="l_pass")
        if st.button("Access Compass"):
            db = load_db()
            if u in db["users"] and db["users"][u] == hash_pass(p):
                st.session_state.logged_in = True
                st.session_state.user_name = u
                st.success("Access Granted. Initializing Compass...")
                time.sleep(1)
                st.rerun()
            else:
                st.error("Invalid credentials.")

    with tab2:
        new_u = st.text_input("Create Username", key="r_user")
        new_p = st.text_input("Create Password", type="password", key="r_pass")
        if st.button("Register Locally"):
            db = load_db()
            if new_u in db["users"]:
                st.warning("Username already exists.")
            elif new_u == "" or new_p == "":
                st.error("Fields cannot be empty.")
            else:
                db["users"][new_u] = hash_pass(new_p)
                save_db(db)
                st.success("Account created locally! You can now login.")

# --- UI: THE BROWSER ---
def show_browser():
    # Sidebar Header
    st.sidebar.title("🧭 MentorLoop")
    st.sidebar.write(f"User: **{st.session_state.user_name}**")
    if st.sidebar.button("Shutdown Browser"):
        st.session_state.logged_in = False
        st.rerun()

    # Browser Top Bar
    st.title("MentorLoop EDU Compass")
    
    query = st.text_input("🌐 Search or enter URL", placeholder="Explain Quantum Physics simply...")

    if query:
        st.markdown(f"### 🔍 Searching: *{query}*")
        
        # Simulated AI Processing
        with st.status("AI Agent is browsing the web...", expanded=True) as status:
            st.write("Checking Educational Databases...")
            time.sleep(1)
            st.write("Synthesizing Results...")
            time.sleep(1)
            status.update(label="Search Complete!", state="complete", expanded=False)

        # Main Layout: 2 Columns
        col_main, col_ai = st.columns([3, 2])
        
        with col_main:
            st.markdown(f"""
            <div style="background-color:#ffffff; padding:20px; border-radius:10px; border: 1px solid #ddd; color: black;">
                <h2 style="color:#1E88E5;">Results for: {query}</h2>
                <hr>
                <p><b>MentorLoop AI Summary:</b> Based on current educational standards, <i>{query}</i> 
                is being analyzed for academic accuracy. The EDU Compass has identified 
                multiple verified sources for your inquiry.</p>
                <ul>
                    <li>Verified Educational Source: 1</li>
                    <li>Verified Educational Source: 2</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.write("")
            st.warning("⚠️ This view is powered by the MentorLoop Compass AI Engine.")

        with col_ai:
            st.markdown("### ✨ Linked AI Assistant")
            # INTEGRATING YOUR SPECIFIC AI LINK HERE
            st.components.v1.iframe("https://chatbot-79kdx1gk0gm.streamlit.app/", height=600, scrolling=True)

# --- ROUTING ---
if not st.session_state.logged_in:
    show_auth()
else:
    show_browser()
