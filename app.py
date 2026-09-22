import streamlit as st
import json

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Bugitrix Roadmap Generator",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# LOAD CUSTOM CSS
# ---------------------------------------------------------
def load_css():
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ---------------------------------------------------------
# CTA LINK
# ---------------------------------------------------------
CTA_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSdjb-zRx_FTFaupAW2Q_6FF7Y49_CSPVveS6kkWui54GV-poA/viewform"

# ---------------------------------------------------------
# LOAD ROADMAP DATA
# ---------------------------------------------------------
def load_roadmap(path_key):
    file_map = {
        "web": "roadmaps/web_security.json",
        "network": "roadmaps/networking.json",
        "cloud": "roadmaps/cloud.json",
        "general": "roadmaps/general.json"
    }
    filepath = file_map.get(path_key, "roadmaps/general.json")
    with open(filepath, "r") as f:
        return json.load(f)

# ---------------------------------------------------------
# DECIDE ROADMAP
# ---------------------------------------------------------
def decide_path(interest, level):
    if interest in ["Web Security", "Bug Bounty"]:
        return "web"
    elif interest == "Networking":
        return "network"
    elif interest == "Cloud":
        return "cloud"
    else:
        return "general"

# ---------------------------------------------------------
# RECOMMEND SERVICE
# ---------------------------------------------------------
def recommend_service(level, goal):
    if level == "Complete beginner":
        return (
            "1:1 Cybersecurity Mentorship",
            "₹1,999",
            "You're just starting. A dedicated mentor will build your path and keep you accountable week by week."
        )
    elif level == "Some labs / CTF":
        return (
            "Cybersecurity Career Ready",
            "₹3,999",
            "You have skills but need job-readiness. This covers resume, LinkedIn, interviews, and portfolio."
        )
    elif level == "Intermediate":
        return (
            "8-Week Cybersecurity Career Program",
            "₹9,999",
            "A complete 8-week transformation with labs, projects, and weekly mentor check-ins."
        )
    else:
        return (
            "1:1 Cybersecurity Clarity Session",
            "₹999",
            "Get clarity on your next step with a focused 1:1 session."
        )

# ---------------------------------------------------------
# HEADER (with logo)
# ---------------------------------------------------------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("logo.png", use_container_width=True)

st.markdown(
    "<h1 style='text-align:center;'>Bugitrix Roadmap Generator</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:#B0B0B0; font-size:1.1rem;'>"
    "From confused beginner to career-ready — one roadmap at a time."
    "</p>",
    unsafe_allow_html=True
)
st.markdown("---")

# ---------------------------------------------------------
# QUESTIONS
# ---------------------------------------------------------
st.markdown("#### Answer 5 quick questions. Get your personalized roadmap instantly.")

background = st.selectbox(
    "1. What's your background?",
    ["No tech background", "IT student", "Working professional", "Some coding experience"]
)

time_available = st.selectbox(
    "2. How much time can you give daily?",
    ["30 minutes", "1–2 hours", "3+ hours"]
)

interest = st.selectbox(
    "3. What excites you most?",
    ["Web Security", "Networking", "Cloud", "Bug Bounty", "Not sure yet"]
)

goal = st.selectbox(
    "4. What's your goal?",
    ["First job", "Freelance", "Career switch", "Just curious"]
)

level = st.selectbox(
    "5. What's your current level?",
    ["Complete beginner", "Some labs / CTF", "Intermediate"]
)

st.markdown("")

# ---------------------------------------------------------
# GENERATE BUTTON
# ---------------------------------------------------------
if st.button("🚀 Generate My Roadmap", use_container_width=True):

    path_key = decide_path(interest, level)
    roadmap = load_roadmap(path_key)

    st.markdown("---")
    st.markdown(f"## 🗺️ Your Roadmap: {roadmap['path_name']}")
    st.markdown(f"*{roadmap['description']}*")
    st.markdown("")

    for phase in roadmap["phases"]:
        st.markdown(f"### {phase['title']}")
        for item in phase["items"]:
            st.markdown(f"- [ ] {item}")
        st.markdown("")

    st.markdown("---")

    # Recommended service
    service_name, price, reason = recommend_service(level, goal)
    st.markdown("## 🎯 Recommended Next Step")
    st.markdown(f"### **{service_name} — {price}**")
    st.markdown(reason)
    st.markdown("")

    st.markdown(
        f"""
        <a href="{CTA_LINK}" target="_blank">
            <button style="
                background-color:#00E5B0;
                color:#0A0A0A;
                padding:14px 28px;
                border:none;
                border-radius:8px;
                font-size:16px;
                font-weight:600;
                cursor:pointer;
                width:100%;
            ">
                👉 Book This Service with Bugitrix
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")
    st.markdown(
        f"*Want to explore all Bugitrix services? [Click here]({CTA_LINK})*"
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.markdown(
    "<div class='footer-text'>"
    "Built with 🛡️ by <b>Bugitrix</b> — Mentor-first cyber security education.<br>"
    "<a href='https://bugitrix.com' target='_blank'>bugitrix.com</a>"
    "</div>",
    unsafe_allow_html=True
)
