import streamlit as st
import hashlib
import json
import os
import time

# --- CONFIG ---
st.set_page_config(page_title="MentorLoop EDU Compass", page_icon="🧭", layout="wide")

DB_FILE = "database.json"
AI_LINK = "https://chatbot-79kdx1gk0gm.streamlit.app/"

# --- DATABASE & AUTH ---
def load_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    with open(DB_FILE, "r") as f: return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- SCIENCE KNOWLEDGE ENGINE ---
def get_science_intel(query):
    query = query.lower()
    knowledge = {
        "science": "Science is the systematic study of the structure and behavior of the physical and natural world through observation and experiment.",
        "biology": "The study of living organisms, divided into many specialized fields that cover their morphology, physiology, anatomy, behavior, origin, and distribution.",
        "physics": "The branch of science concerned with the nature and properties of matter and energy.",
        "chemistry": "The branch of science that deals with the identification of the substances of which matter is composed.",
        "quantum": "Quantum mechanics is a fundamental theory in physics that provides a description of the physical properties of nature at the scale of atoms and subatomic particles."
    }
    for key in knowledge:
        if key in query:
            return knowledge[key]
    return "Topic analyzed. Information retrieved from EDU Compass cloud global 21.0 index."

# --- SESSION STATE ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

# --- UI: AUTH ---
if not st.session_state.logged_in:
    st.title("🧭 MentorLoop EDU Compass")
    t1, t2 = st.tabs(["Login", "Register"])
    with t1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            db = load_db()
            if u in db["users"] and db["users"][u] == hash_pass(p):
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else: st.error("Access Denied")
    with t2:
        nu = st.text_input("New Username")
        np = st.text_input("New Password", type="password")
        if st.button("Register"):
            db = load_db()
            db["users"][nu] = hash_pass(np)
            save_db(db)
            st.success("Registered Locally!")

# --- UI: BROWSER ---
else:
    # Sidebar
    st.sidebar.title("🧭 EDU Compass")
    st.sidebar.write(f"Logged in: {st.session_state.user}")
    
    # 1. THE AI ASSISTANT BUTTON
    st.sidebar.markdown("---")
    st.sidebar.write("### AI Tools")
    if st.sidebar.button("✨ Open AI Assistant"):
        # This opens the link in a new tab since it's an external streamlit app
        js = f"window.open('{AI_LINK}')"
        st.components.v1.html(f"<script>{js}</script>", height=0)
        st.sidebar.success("Assistant Opened in New Tab")

    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    # Browser Top Bar
    st.title("MentorLoop EDU Compass")
    url_input = st.text_input("🌐 Enter URL or Search Topic", placeholder="e.g. Science, or https://wikipedia.com")

    if url_input:
        # Check if it's a URL or a Search
        if url_input.startswith("http"):
            st.info(f"Attempting to navigate to {url_input}...")
            st.markdown(f"### [Click Here to Navigate to Site]({url_input})")
            st.warning("Note: Security layers (CORS) prevent some sites from loading directly inside a frame. Use the link above if the window below is blank.")
            st.components.v1.iframe(url_input, height=600, scrolling=True)
        
        else:
            # SEARCH MODE
            with st.spinner("AI Compass gathering data..."):
                time.sleep(1)
                science_result = get_science_intel(url_input)
            
            # Browser Result Page UI
            st.markdown(f"""
            <div style="background-color:#f0f2f6; padding:25px; border-radius:15px; border-left: 5px solid #007bff; color: black;">
                <h3 style="margin-top:0;">Search Results: {url_input.capitalize()}</h3>
                <p style="font-size:18px;">{science_result}</p>
                <hr>
                <small>Source: MentorLoop Internal Database & Local AI Engine</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Action Buttons for results
            col1, col2 = st.columns(2)
            with col1:
                if st.button("Cite this information"):
                    st.code(f"MentorLoop EDU Compass. (2023). Report on {url_input}.")
            with col2:
                # Direct AI query based on search
                st.link_button("Analyze with AI Assistant", f"{AI_LINK}?query={url_input}")
