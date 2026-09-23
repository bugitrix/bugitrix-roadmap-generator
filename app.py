import streamlit as st
import json
import base64
import os
import re
from datetime import datetime, timedelta
from math import ceil

# ===========================================================
# PAGE CONFIG
# ===========================================================
st.set_page_config(
    page_title="Bugitrix Roadmap Generator",
    page_icon="🛡️",
    layout="centered",
    initial_sidebar_state="expanded"
)

# ===========================================================
# CONSTANTS
# ===========================================================
CTA_LINK = "https://docs.google.com/forms/d/e/1FAIpQLSdjb-zRx_FTFaupAW2Q_6FF7Y49_CSPVveS6kkWui54GV-poA/viewform"
BRAND_SITE = "https://bugitrix.com"

FILE_MAP = {
    "web": "roadmaps/web_security.json",
    "network": "roadmaps/networking.json",
    "cloud": "roadmaps/cloud.json",
    "general": "roadmaps/general.json",
}

TRACK_LABELS = {
    "web": "🕸️ Web Security & Bug Bounty",
    "network": "🌐 Networking & Network Security",
    "cloud": "☁️ Cloud Security",
    "general": "🧭 General Foundations",
}

TYPE_ICONS = {"Learn": "📘", "Practice": "🧪", "Build": "🔨"}

DIFFICULTY_COLORS = {
    "Beginner": "#00E5B0",
    "Easy": "#4ADE80",
    "Medium": "#FBBF24",
    "Hard": "#F87171",
}

# Rough daily hours implied by each time-commitment answer
DAILY_HOURS_MAP = {
    "30 minutes": 0.5,
    "1–2 hours": 1.5,
    "3+ hours": 3.5,
}

# ===========================================================
# CSS LOADING
# ===========================================================
def load_css():
    css_path = "assets/style.css"
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ style.css not found — running with default Streamlit theme.")

load_css()

# ===========================================================
# DATA LOADING
# ===========================================================
@st.cache_data(show_spinner=False)
def load_roadmap(path_key):
    """Load a roadmap JSON file. Returns None if missing/invalid."""
    filepath = FILE_MAP.get(path_key, FILE_MAP["general"])
    if not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return None

# ===========================================================
# DECISION LOGIC — weighted scoring instead of flat if/elif
# ===========================================================
def decide_path(interest, goal, level):
    scores = {"web": 0.0, "network": 0.0, "cloud": 0.0, "general": 0.0}

    interest_weights = {
        "Web Security": {"web": 3},
        "Bug Bounty": {"web": 3, "general": 1},
        "Networking": {"network": 3},
        "Cloud": {"cloud": 3},
        "Not sure yet": {"general": 2, "web": 1, "network": 1, "cloud": 1},
    }
    for track, w in interest_weights.get(interest, {}).items():
        scores[track] += w

    goal_weights = {
        "First job": {"web": 1, "network": 1, "cloud": 1},
        "Freelance": {"web": 2},
        "Career switch": {"general": 1},
        "Just curious": {"general": 2},
    }
    for track, w in goal_weights.get(goal, {}).items():
        scores[track] += w

    # Someone already past "complete beginner" is more likely ready to specialize
    if level != "Complete beginner":
        for track in ("web", "network", "cloud"):
            scores[track] += 0.5

    return max(scores, key=scores.get)

def recommend_service(level, goal, time_available):
    if level == "Complete beginner":
        if time_available == "30 minutes":
            reason = (
                "You're just starting, and with limited daily time every session needs to count. "
                "A dedicated mentor keeps you on the shortest path instead of wasting hours guessing what's next."
            )
        else:
            reason = (
                "You're just starting. A dedicated mentor will build your path and keep you accountable week by week."
            )
        return ("1:1 Cybersecurity Mentorship", "₹1,999", reason)

    elif level == "Some labs / CTF":
        if goal == "Freelance":
            reason = (
                "You already have raw skill from labs and CTFs — this program packages it into a portfolio "
                "and pitch that actually lands freelance clients."
            )
        else:
            reason = (
                "You have skills but need job-readiness. This covers resume, LinkedIn, interviews, and portfolio."
            )
        return ("Cybersecurity Career Ready", "₹3,999", reason)

    elif level == "Intermediate":
        return (
            "8-Week Cybersecurity Career Program",
            "₹9,999",
            "A complete 8-week transformation with labs, projects, and weekly mentor check-ins.",
        )

    else:
        return (
            "1:1 Cybersecurity Clarity Session",
            "₹999",
            "Get clarity on your next step with a focused 1:1 session.",
        )

# ===========================================================
# TIME ESTIMATION LOGIC
# ===========================================================
def parse_hours(time_str):
    """Extract an average hour estimate from strings like '5–6 hrs' or 'Ongoing'."""
    numbers = re.findall(r"\d+\.?\d*", time_str)
    if not numbers:
        return 0.0
    numbers = [float(n) for n in numbers]
    return sum(numbers) / len(numbers)

def estimate_timeline(roadmap, time_available):
    total_hours = 0.0
    ongoing_items = 0
    for phase in roadmap["phases"]:
        for item in phase["items"]:
            if "ongoing" in item["time"].lower():
                ongoing_items += 1
            else:
                total_hours += parse_hours(item["time"])

    daily_hours = DAILY_HOURS_MAP.get(time_available, 1.5)
    total_days = ceil(total_hours / daily_hours) if daily_hours > 0 else 0
    weeks = ceil(total_days / 7) if total_days else 0
    target_date = datetime.now() + timedelta(days=total_days)

    return {
        "total_hours": round(total_hours, 1),
        "ongoing_items": ongoing_items,
        "weeks": weeks,
        "target_date": target_date.strftime("%d %B %Y"),
    }

# ===========================================================
# EXPORT GENERATION
# ===========================================================
def generate_roadmap_text(roadmap, answers, timeline):
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
    lines.append(f"Duration        : {roadmap['duration']}")
    lines.append(f"Level           : {roadmap['level']}")
    lines.append(f"Outcome         : {roadmap['outcome']}")
    lines.append(f"Est. Total Time : ~{timeline['total_hours']} hrs (+{timeline['ongoing_items']} ongoing tasks)")
    lines.append(f"Est. Finish By  : {timeline['target_date']} (~{timeline['weeks']} weeks at your pace)")
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

def generate_roadmap_markdown(roadmap, answers, timeline, completed_keys):
    lines = []
    lines.append(f"# {roadmap['path_name']}")
    lines.append(f"*{roadmap['tagline']}*")
    lines.append("")
    lines.append(f"> Generated by [Bugitrix Roadmap Generator]({BRAND_SITE}) on {datetime.now().strftime('%d %B %Y')}")
    lines.append("")
    lines.append("## Your Profile")
    lines.append(f"- **Background:** {answers['background']}")
    lines.append(f"- **Daily time:** {answers['time']}")
    lines.append(f"- **Interest:** {answers['interest']}")
    lines.append(f"- **Goal:** {answers['goal']}")
    lines.append(f"- **Level:** {answers['level']}")
    lines.append("")
    lines.append("## Path Overview")
    lines.append(f"- **Duration:** {roadmap['duration']}")
    lines.append(f"- **Level:** {roadmap['level']}")
    lines.append(f"- **Outcome:** {roadmap['outcome']}")
    lines.append(f"- **Estimated time:** ~{timeline['total_hours']} hrs, finish by ~{timeline['target_date']}")
    lines.append("")

    for p_idx, phase in enumerate(roadmap["phases"]):
        lines.append(f"## {phase['title']}")
        lines.append(f"*{phase['subtitle']}*")
        lines.append("")
        for i_idx, item in enumerate(phase["items"]):
            key = f"{p_idx}-{i_idx}"
            box = "x" if key in completed_keys else " "
            lines.append(f"- [{box}] **{item['title']}** — {item['detail']}")
            lines.append(f"  - {item['type']} · {item['difficulty']} · {item['time']} · [{item['resource_label']}]({item['resource']})")
        lines.append("")

    lines.append("---")
    lines.append(f"**Want to accelerate?** [Book a session with Bugitrix]({CTA_LINK})")
    lines.append("")
    lines.append(f"Built by [Bugitrix]({BRAND_SITE}) — mentor-first cyber security education.")
    return "\n".join(lines)

def make_download_link(content, filename, label, mime="text/plain"):
    b64 = base64.b64encode(content.encode()).decode()
    return f"""<a href="data:{mime};base64,{b64}" download="{filename}" class='secondary-cta'>{label}</a>"""

# ===========================================================
# SESSION STATE
# ===========================================================
defaults = {
    "roadmap": None,
    "roadmap_key": None,
    "answers": None,
    "completed": set(),
    "browse_mode": False,
    "celebrated": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

def reset_all():
    st.session_state.roadmap = None
    st.session_state.roadmap_key = None
    st.session_state.answers = None
    st.session_state.completed = set()
    st.session_state.browse_mode = False
    st.session_state.celebrated = False
    st.query_params.clear()

def load_track_direct(track_key):
    """Load a roadmap directly (sidebar browse mode), skipping the quiz."""
    roadmap = load_roadmap(track_key)
    if roadmap is None:
        st.session_state["_load_error"] = track_key
        return
    st.session_state.roadmap = roadmap
    st.session_state.roadmap_key = track_key
    st.session_state.browse_mode = True
    st.session_state.answers = {
        "background": "—",
        "time": "1–2 hours",
        "interest": TRACK_LABELS.get(track_key, track_key),
        "goal": "Exploring",
        "level": "Complete beginner",
    }
    st.session_state.completed = set()
    st.session_state.celebrated = False
    st.query_params["track"] = track_key

# ---- auto-load from shareable link (?track=cloud etc.) ----
qp_track = st.query_params.get("track")
if qp_track and st.session_state.roadmap is None and qp_track in FILE_MAP:
    load_track_direct(qp_track)

# ===========================================================
# SIDEBAR — always-visible brand + CTA
# ===========================================================
with st.sidebar:
    if os.path.exists("logo.png"):
        st.image("logo.png", width=90)
    else:
        st.markdown("### 🛡️ BUGITRIX")

    st.markdown("**Mentor-first cyber security education.**")
    st.markdown(
        f"""
        <a href="{CTA_LINK}" target="_blank" class='sidebar-cta'>📅 Book a Free Call</a>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")

    if st.session_state.roadmap is not None:
        roadmap = st.session_state.roadmap
        total = sum(len(p["items"]) for p in roadmap["phases"])
        done = len(st.session_state.completed)
        pct = (done / total * 100) if total else 0
        st.markdown(f"**Current path:**\n\n{roadmap['path_name']}")
        st.progress(pct / 100 if total else 0, text=f"{done}/{total} tasks · {pct:.0f}%")
        if st.button("🔄 Restart Quiz", use_container_width=True):
            reset_all()
            st.rerun()

    st.markdown("---")
    st.markdown("**🔍 Browse roadmaps directly**")
    st.caption("Skip the quiz and preview any path.")
    for key, label in TRACK_LABELS.items():
        if st.button(label, key=f"browse_{key}", use_container_width=True):
            load_track_direct(key)
            st.rerun()

    st.markdown("---")
    st.caption("🆓 100% Free · ⚡ Instant · 🎯 Personalized")
    st.caption(f"[bugitrix.com]({BRAND_SITE})")

# ===========================================================
# HEADER
# ===========================================================
if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.image("logo.png", width=110)
else:
    st.markdown("<h1 style='text-align:center;'>🛡️ Bugitrix</h1>", unsafe_allow_html=True)

st.markdown(
    "<h1 style='text-align:center; margin-top:0.2rem;'>Bugitrix Roadmap Generator</h1>",
    unsafe_allow_html=True,
)
st.markdown(
    "<p style='text-align:center; color:#B0B0B0; font-size:1.05rem; margin-top:-0.5rem;'>"
    "From confused beginner to career-ready — one roadmap at a time."
    "</p>",
    unsafe_allow_html=True,
)
st.markdown(
    """
    <div style='text-align:center; margin: 1.2rem 0 1.8rem 0;'>
        <span class='pill'>🆓 100% Free</span>
        <span class='pill'>⚡ Instant Result</span>
        <span class='pill'>🎯 Personalized</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# ===========================================================
# LOAD ERROR HANDLING
# ===========================================================
if st.session_state.get("_load_error"):
    missing_key = st.session_state.pop("_load_error")
    st.error(
        f"⚠️ Couldn't find the roadmap file for **{TRACK_LABELS.get(missing_key, missing_key)}** "
        f"(expected at `{FILE_MAP.get(missing_key)}`). Please check the file exists and is valid JSON."
    )

# ===========================================================
# QUIZ FORM
# ===========================================================
if st.session_state.roadmap is None:

    st.markdown("#### Answer 5 quick questions. Get your personalized roadmap instantly.")

    background = st.selectbox(
        "1. What's your background?",
        ["No tech background", "IT student", "Working professional", "Some coding experience"],
    )
    time_available = st.selectbox(
        "2. How much time can you give daily?",
        ["30 minutes", "1–2 hours", "3+ hours"],
    )
    interest = st.selectbox(
        "3. What excites you most?",
        ["Web Security", "Networking", "Cloud", "Bug Bounty", "Not sure yet"],
    )
    goal = st.selectbox(
        "4. What's your goal?",
        ["First job", "Freelance", "Career switch", "Just curious"],
    )
    level = st.selectbox(
        "5. What's your current level?",
        ["Complete beginner", "Some labs / CTF", "Intermediate"],
    )

    st.markdown("")

    if st.button("🚀 Generate My Roadmap", use_container_width=True):
        path_key = decide_path(interest, goal, level)
        roadmap = load_roadmap(path_key)
        if roadmap is None:
            st.error(
                f"⚠️ We couldn't load the roadmap for this path (`{FILE_MAP.get(path_key)}`). "
                "Please make sure the file exists in the `roadmaps/` folder."
            )
        else:
            st.session_state.answers = {
                "background": background,
                "time": time_available,
                "interest": interest,
                "goal": goal,
                "level": level,
            }
            st.session_state.roadmap = roadmap
            st.session_state.roadmap_key = path_key
            st.session_state.browse_mode = False
            st.session_state.completed = set()
            st.session_state.celebrated = False
            st.query_params["track"] = path_key
            st.rerun()

# ===========================================================
# ROADMAP DISPLAY
# ===========================================================
else:
    roadmap = st.session_state.roadmap
    answers = st.session_state.answers
    timeline = estimate_timeline(roadmap, answers["time"])

    total_items = sum(len(p["items"]) for p in roadmap["phases"])
    done_items = len(st.session_state.completed)
    progress = done_items / total_items if total_items else 0

    if st.session_state.browse_mode:
        st.info("👀 **Preview mode** — you're browsing this roadmap directly. Take the quiz for a personalized recommendation.")

    # ---- Hero card ----
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
            <div class='meta-row'>
                <span class='meta-badge'>🕒 ~{timeline['total_hours']} hrs total</span>
                <span class='meta-badge'>📅 Finish by ~{timeline['target_date']}</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # ---- Overall progress ----
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
        unsafe_allow_html=True,
    )

    if progress >= 1.0 and total_items > 0 and not st.session_state.celebrated:
        st.balloons()
        st.session_state.celebrated = True

    st.markdown("")

    # ---- Search & filter ----
    with st.expander("🔍 Search & Filter Roadmap", expanded=False):
        search_query = st.text_input("Search by keyword", placeholder="e.g. IAM, XSS, certification...")
        all_difficulties = sorted(
            {item["difficulty"] for phase in roadmap["phases"] for item in phase["items"]},
            key=lambda d: list(DIFFICULTY_COLORS.keys()).index(d) if d in DIFFICULTY_COLORS else 99,
        )
        selected_difficulties = st.multiselect(
            "Filter by difficulty", options=all_difficulties, default=all_difficulties
        )
        all_types = sorted({item["type"] for phase in roadmap["phases"] for item in phase["items"]})
        selected_types = st.multiselect("Filter by type", options=all_types, default=all_types)

    search_query = search_query.strip().lower()

    # ---- Phases ----
    for phase_idx, phase in enumerate(roadmap["phases"]):
        phase_total = len(phase["items"])
        phase_done = sum(
            1 for i in range(phase_total) if f"{phase_idx}-{i}" in st.session_state.completed
        )
        phase_pct = (phase_done / phase_total * 100) if phase_total else 0

        st.markdown(
            f"""
            <div class='phase-header'>
                <h3 style='margin:0;'>{phase['title']}</h3>
                <p style='color:#888; margin:0.2rem 0 0.5rem 0; font-size:0.9rem;'>{phase['subtitle']}</p>
                <div class='phase-progress-track'>
                    <div class='phase-progress-fill' style='width:{phase_pct:.1f}%;'></div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        visible_count = 0
        for item_idx, item in enumerate(phase["items"]):
            if item["difficulty"] not in selected_difficulties:
                continue
            if item["type"] not in selected_types:
                continue
            if search_query and search_query not in item["title"].lower() and search_query not in item["detail"].lower():
                continue

            visible_count += 1
            key = f"{phase_idx}-{item_idx}"
            checked = key in st.session_state.completed

            col_check, col_body = st.columns([0.08, 0.92])
            with col_check:
                new_val = st.checkbox("", key=f"chk_{key}", value=checked, label_visibility="collapsed")
                if new_val:
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
                    unsafe_allow_html=True,
                )

        if visible_count == 0:
            st.markdown(
                "<div class='empty-state'>No items match your current filters in this phase.</div>",
                unsafe_allow_html=True,
            )

        st.markdown("")

    st.markdown("---")

    # ---- Recommended service ----
    service_name, price, reason = recommend_service(answers["level"], answers["goal"], answers["time"])
    st.markdown(
        f"""
        <div class='cta-card'>
            <div class='hero-tag'>🎯 RECOMMENDED NEXT STEP</div>
            <h2 style='margin:0.3rem 0;'>{service_name}</h2>
            <div class='price-tag'>{price}</div>
            <p style='color:#D0D0D0; margin-top:0.8rem;'>{reason}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<a href="{CTA_LINK}" target="_blank" class='main-cta'>👉 Book This Service with Bugitrix</a>""",
        unsafe_allow_html=True,
    )

    st.markdown("")

    # ---- Downloads + reset ----
    colA, colB, colC = st.columns(3)
    with colA:
        roadmap_text = generate_roadmap_text(roadmap, answers, timeline)
        filename_txt = f"Bugitrix_Roadmap_{roadmap['path_name'].replace(' ', '_')}.txt"
        st.markdown(make_download_link(roadmap_text, filename_txt, "⬇️ Download .txt"), unsafe_allow_html=True)
    with colB:
        roadmap_md = generate_roadmap_markdown(roadmap, answers, timeline, st.session_state.completed)
        filename_md = f"Bugitrix_Roadmap_{roadmap['path_name'].replace(' ', '_')}.md"
        st.markdown(make_download_link(roadmap_md, filename_md, "⬇️ Download .md"), unsafe_allow_html=True)
    with colC:
        if st.button("🔄 Start Over", use_container_width=True):
            reset_all()
            st.rerun()

    st.markdown("")
    st.caption(
        f"🔗 Bookmark this exact roadmap by copying the URL from your browser — it now includes `?track={st.session_state.roadmap_key}`."
    )
    st.markdown(f"*Want to explore all Bugitrix services? [Click here]({CTA_LINK})*")

# ===========================================================
# FOOTER
# ===========================================================
st.markdown("---")
st.markdown(
    "<div class='footer-text'>"
    "Built with 🛡️ by <b>Bugitrix</b> — Mentor-first cyber security education.<br>"
    f"<a href='{BRAND_SITE}' target='_blank'>bugitrix.com</a>"
    "</div>",
    unsafe_allow_html=True,
)
