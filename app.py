import streamlit as st
import json
import base64
from datetime import datetime

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
# CONSTANTS
# ---------------------------------------------------------
CTA_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSdjb-zRx_FTFaupAW2Q_6FF7Y49_CSPVveS6kkWui54GV-poA/viewform"

TYPE_ICONS = {
    "Learn": "📘",
    "Practice": "🧪",
    "Build": "🔨"
}

DIFFICULTY_COLORS = {
    "Beginner": "#00E5B0",
    "Easy": "#4ADE80",
    "Medium": "#FBBF24",
    "Hard": "#F87171"
}

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
# DECISION LOGIC
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
# PDF GENERATION (simple, text-based report)
# ---------------------------------------------------------
def generate_roadmap_text(roadmap, answers):
    lines = []
    lines.append("=" * 60)
    lines.append("BUGITRIX — PERSONALIZED CYBER SECURITY ROADMAP")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"Generated: {datetime.now().strftime('%d %B %Y')}")
    lines.append("")
    lines.append("YOUR PROFILE")
    lines.append("-" * 60)
    lines.append(f"Background     : {answers['background']}")
    lines.append(f"Daily Time     : {answers['time']}")
    lines.append(f"Interest       : {answers['interest']}")
    lines.append(f"Goal           : {answers['goal']}")
    lines.append(f"Current Level  : {answers['level']}")
    lines.append("")
    lines.append("=" * 60)
    lines.append(f"PATH: {roadmap['path_name']}")
    lines.append("=" * 60)
    lines.append(f"{roadmap['tagline']}")
    lines.append("")
    lines.append(f"Duration : {roadmap['duration']}")
    lines.append(f"Level    : {roadmap['level']}")
    lines.append(f"Outcome  : {roadmap['outcome']}")
    lines.append("")
    lines.append("-" * 60)

    for phase in roadmap["phases"]:
        lines.append("")
        lines.append(phase["title"])
        lines.append(phase["subtitle"])
        lines.append("")
        for item in phase["items"]:
            lines.append(f"  [ ] {item['title']}")
            lines.append(f"      {item['detail']}")
            lines.append(f"      Type: {item['type']}  |  Difficulty: {item['difficulty']}  |  Time: {item['time']}")
            lines.append(f"      Resource: {item['resource']}")
            lines.append("")
        lines.append("-" * 60)

    lines.append("")
    lines.append("=" * 60)
    lines.append("RECOMMENDED NEXT STEP WITH BUGITRIX")
    lines.append("=" * 60)
    lines.append("")
    lines.append("Ready to accelerate? Book a session with Bugitrix:")
    lines.append(CTA_LINK)
    lines.append("")
    lines.append("Built by Bugitrix — bugitrix.com")
    lines.append("Mentor-first cyber security education.")
    return "\n".join(lines)

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
if "roadmap" not in st.session_state:
    st.session_state.roadmap = None
if "answers" not in st.session_state:
    st.session_state.answers = None
if "completed" not in st.session_state:
    st.session_state.completed = set()

# ---------------------------------------------------------
# HEADER — COMPACT LOGO + BRAND
# ---------------------------------------------------------
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    st.image("logo.png", width=110)

st.markdown(
    "<h1 style='text-align:center; margin-top:0.2rem;'>Bugitrix Roadmap Generator</h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='text-align:center; color:#B0B0B0; font-size:1.05rem; margin-top:-0.5rem;'>"
    "From confused beginner to career-ready — one roadmap at a time."
    "</p>",
    unsafe_allow_html=True
)

st.markdown(
    """
    <div style='text-align:center; margin: 1.2rem 0 1.8rem 0;'>
        <span class='pill'>🆓 100% Free</span>
        <span class='pill'>⚡ Instant Result</span>
        <span class='pill'>🎯 Personalized</span>
    </div>
    """,
    unsafe_allow_html=True
)

st.markdown("---")

# ---------------------------------------------------------
# QUESTIONS FORM
# ---------------------------------------------------------
if st.session_state.roadmap is None:

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

    if st.button("🚀 Generate My Roadmap", use_container_width=True):
        st.session_state.answers = {
            "background": background,
            "time": time_available,
            "interest": interest,
            "goal": goal,
            "level": level
        }
        path_key = decide_path(interest, level)
        st.session_state.roadmap = load_roadmap(path_key)
        st.session_state.completed = set()
        st.rerun()

# ---------------------------------------------------------
# ROADMAP DISPLAY
# ---------------------------------------------------------
else:
    roadmap = st.session_state.roadmap
    answers = st.session_state.answers

    # Progress calculation
    total_items = sum(len(p["items"]) for p in roadmap["phases"])
    done_items = len(st.session_state.completed)
    progress = done_items / total_items if total_items else 0

    # Hero card
    st.markdown(
        f"""
        <div class='hero-card'>
            <div class='hero-tag'>YOUR PERSONALIZED PATH</div>
            <h2 style='margin:0.2rem 0 0.4rem 0;'>{roadmap['path_name']}</h2>
            <p style='color:#B0B0B0; margin:0 0 1rem 0;'>{roadmap['tagline']}</p>
            <p style='color:#D0D0D0; font-size:0.95rem;'>{roadmap['description']}</p>
            <div class='meta-row'>
                <span class='meta-badge'>⏱ {roadmap['duration']}</span>
                <span class='meta-badge'>📊 {roadmap['level']}</span>
                <span class='meta-badge'>🎯 {roadmap['outcome']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Progress bar
    st.markdown(
        f"""
        <div style='margin: 1.5rem 0 0.5rem 0;'>
            <div style='display:flex; justify-content:space-between; color:#B0B0B0; font-size:0.9rem;'>
                <span>Your Progress</span>
                <span>{done_items} / {total_items} completed</span>
            </div>
            <div class='progress-track'>
                <div class='progress-fill' style='width:{progress*100:.1f}%;'></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    # Phases
    for phase_idx, phase in enumerate(roadmap["phases"]):
        st.markdown(
            f"""
            <div class='phase-header'>
                <h3 style='margin:0;'>{phase['title']}</h3>
                <p style='color:#888; margin:0.2rem 0 0 0; font-size:0.9rem;'>{phase['subtitle']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        for item_idx, item in enumerate(phase["items"]):
            key = f"{phase_idx}-{item_idx}"
            checked = key in st.session_state.completed

            col_check, col_body = st.columns([0.08, 0.92])

            with col_check:
                if st.checkbox("", key=f"chk_{key}", value=checked, label_visibility="collapsed"):
                    st.session_state.completed.add(key)
                else:
                    st.session_state.completed.discard(key)

            with col_body:
                type_icon = TYPE_ICONS.get(item["type"], "📌")
                diff_color = DIFFICULTY_COLORS.get(item["difficulty"], "#B0B0B0")
                strike = "text-decoration:line-through; opacity:0.55;" if checked else ""

                st.markdown(
                    f"""
                    <div class='item-card' style='{strike}'>
                        <div class='item-title'>{type_icon} {item['title']}</div>
                        <div class='item-detail'>{item['detail']}</div>
                        <div class='item-meta'>
                            <span class='badge' style='border-color:{diff_color}; color:{diff_color};'>{item['difficulty']}</span>
                            <span class='badge'>⏱ {item['time']}</span>
                            <span class='badge'>{item['type']}</span>
                        </div>
                        <a class='resource-link' href='{item['resource']}' target='_blank'>🔗 {item['resource_label']}</a>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("")

    st.markdown("---")

    # Recommended service
    service_name, price, reason = recommend_service(answers["level"], answers["goal"])

    st.markdown(
        f"""
        <div class='cta-card'>
            <div class='hero-tag'>🎯 RECOMMENDED NEXT STEP</div>
            <h2 style='margin:0.3rem 0;'>{service_name}</h2>
            <div class='price-tag'>{price}</div>
            <p style='color:#D0D0D0; margin-top:0.8rem;'>{reason}</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        f"""
        <a href="{CTA_LINK}" target="_blank" class='main-cta'>
            👉 Book This Service with Bugitrix
        </a>
        """,
        unsafe_allow_html=True
    )

    st.markdown("")

    # Download + Reset
    colA, colB = st.columns(2)
    with colA:
        roadmap_text = generate_roadmap_text(roadmap, answers)
        b64 = base64.b64encode(roadmap_text.encode()).decode()
        filename = f"Bugitrix_Roadmap_{roadmap['path_name'].replace(' ', '_')}.txt"
        st.markdown(
            f"""
            <a href="data:text/plain;base64,{b64}" download="{filename}" class='secondary-cta'>
                ⬇️ Download Roadmap
            </a>
            """,
            unsafe_allow_html=True
        )
    with colB:
        if st.button("🔄 Start Over", use_container_width=True):
            st.session_state.roadmap = None
            st.session_state.answers = None
            st.session_state.completed = set()
            st.rerun()

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
