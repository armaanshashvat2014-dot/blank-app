import streamlit as st
import hashlib
import json
import os
import re
import time

# --- CONFIGURATION ---
st.set_page_config(page_title="MentorLoop EDU Compass", page_icon="🧭", layout="wide")
DB_FILE = "database.json"
AI_LINK = "https://chatbot-79kdx1gk0gm.streamlit.app/"

# --- RESTRICTION SETTINGS ---
BANNED_PLATFORMS = ["facebook.com", "instagram.com", "youtube.com", "tiktok.com", "twitter.com", "x.com", "reddit.com"]

# --- DATABASE LOGIC ---
def load_db():
    if not os.path.exists(DB_FILE): return {"users": {}}
    try:
        with open(DB_FILE, "r") as f: return json.load(f)
    except: return {"users": {}}

def save_db(data):
    with open(DB_FILE, "w") as f: json.dump(data, f, indent=4)

def hash_pass(p): return hashlib.sha256(str.encode(p)).hexdigest()

# --- THE COMPASS ENGINES (INTEGRATED AI) ---
def get_ai_response(query):
    """
    Simulates fetching an answer from the linked AI engine.
    In a production app, you would use requests.post(API_URL) here.
    """
    query = query.lower().strip()
    
    # Simulate processing delay for 'AI-feel'
    with st.spinner('🤖 Consultant AI is generating response...'):
        time.sleep(1.2) 
    
    # 1. MATH LOGIC
    if re.match(r"^[0-9\+\-\*\/\(\)\s\.]+$", query):
        try:
            res = eval(query, {"__builtins__": None}, {})
            return f"### 🔢 Calculation Result\nAfter processing your mathematical expression, the result is: **{res}**.", "Mathematics"
        except:
            return "I attempted to calculate that, but the syntax seems incorrect. Please check your numbers.", "Error"

    # 2. ENHANCED KNOWLEDGE ENGINE (SIMULATING AI RETRIEVAL)
    # This acts as the "Internal AI" answer
    knowledge_base = {
        "science": "Science is the systematic enterprise that builds and organizes knowledge in the form of testable explanations and predictions about the universe.",
        "photosynthesis": "Photosynthesis is the process used by plants and other organisms to convert light energy into chemical energy (sugar).",
        "gravity": "Gravity is a fundamental interaction which causes mutual attraction between all things with mass or energy.",
        "coding": "Coding, or programming, is the process of creating instructions for computers to follow using specific languages like Python or C++."
    }

    if query in knowledge_base:
        return f"### 🧠 AI Knowledge Index\n{knowledge_base[query]}", query.capitalize()
    
    # 3. FALLBACK AI (General Logic)
    return (f"### 🌐 AI Analysis\nI have analyzed your query regarding **'{query}'**. \n\n"
            f"Based on academic records, this topic falls under **General Research**. To provide a more detailed "
            "dissertation, please connect to the high-performance AI cluster using the link in the sidebar."), "General Inquiry"

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
    st.sidebar.title("🧭 EDU Compass")
    st.sidebar.write(f"Active User: **{st.session_state.user}**")
    st.sidebar.divider()
    st.sidebar.write("### AI CLUSTER STATUS")
    st.sidebar.success("● Connected to MentorLoop AI")
    st.sidebar.link_button("✨ Advanced AI Dashboard", AI_LINK, use_container_width=True)
    
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    st.title("MentorLoop EDU Compass")
    user_input = st.text_input("🌐 Enter Topic, Math, or Website URL")

    if user_input:
        # Check if input is a URL
        url_pattern = r'[a-zA-Z0-9-]+\.[a-zA-Z]{2,}'
        is_url = re.search(url_pattern, user_input) or user_input.startswith("http")

        if is_url:
            # BLOCKLIST CHECK
            is_banned = any(platform in user_input.lower() for platform in BANNED_PLATFORMS)
            if is_banned:
                st.error("🚫 **Access Denied.** Social Media/Entertainment is blocked for productivity.")
            else:
                final_url = user_input if user_input.startswith("http") else "https://" + user_input
                st.info(f"Navigating to External Resource...")
                st.components.v1.iframe(final_url, height=600, scrolling=True)
        else:
            # --- AI ANSWER SECTION ---
            ai_result, category = get_ai_response(user_input)
            
            st.markdown(f"""
                <div style="background-color: #ffffff; padding: 30px; border-radius: 15px; border-left: 8px solid #1a73e8; color: #333; box-shadow: 0px 4px 12px rgba(0,0,0,0.1);">
                    <p style="color: #666; font-size: 12px; margin-bottom: 0;">SOURCE: AI COMPASS ENGINE | CATEGORY: {category}</p>
                    <div style="font-family: 'Segoe UI', sans-serif;">
                        {ai_result}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # Action buttons for the answer
            st.write("")
            col1, col2 = st.columns([1, 4])
            with col1:
                # Deep link to your other app for further chat
                st.link_button("💬 Chat about this", f"{AI_LINK}?q={user_input}")
