"""
StudyFlow v4 — Smart Study Planner
Email login | OTP reset | Profile | Fixed Sidebar | Gemini AI Assistant
Run: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta

import auth
from knowledge_graph import StudyKnowledgeGraph
from study_planner import StudyPlanner, DIFFICULTY_COLOR, DIFFICULTY_ICON
from ai_assistant import (
    build_student_context, chat_with_ai,
    get_quick_prompts,
)

# ─────────────────────────────────────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="StudyFlow — Smart Study Planner",
    page_icon="📖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
#  GLOBAL CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Lora:wght@400;600;700&family=DM+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');


:root {
  --bg:       #F5F0E8; --bg2:    #EDE8DC; --surface: #FDFAF4;
  --border:   #DDD5C0; --border2:#C8BFA6;
  --txt:      #2C2416; --txt2:   #6B5E45; --txt3: #9C8E75;
  --accent:   #4F46E5; --accent2:#7C3AED;
  --red:      #DC2626; --green:  #16A34A; --gold: #D97706;
  --shadow:   0 2px 12px rgba(44,36,22,0.10);
  --shadow-lg:0 8px 32px rgba(44,36,22,0.15);
  --radius:   14px;
}

html,body,[class*="css"]{ font-family:'DM Sans',sans-serif; color:var(--txt); }

.stApp {
  background:var(--bg);
  background-image:
    radial-gradient(ellipse at 20% 20%,rgba(79,70,229,0.04) 0%,transparent 60%),
    radial-gradient(ellipse at 80% 80%,rgba(217,119,6,0.04) 0%,transparent 60%);
}

/* ── FIXED SIDEBAR ── */
[data-testid="collapsedControl"]          { display:none !important; }
section[data-testid="stSidebar"]>div:first-child>button { display:none !important; }
section[data-testid="stSidebar"] {
  background: linear-gradient(180deg,#2D2260 0%,#1E1650 60%,#150F3C 100%) !important;
  border-right:none !important;
  min-width:285px !important;
  max-width:285px !important;
  width:285px !important;
}
section[data-testid="stSidebar"] * { color:#E8E4F5 !important; }
section[data-testid="stSidebar"] hr { border-color:rgba(255,255,255,0.12) !important; }
section[data-testid="stSidebar"] .stButton>button {
  background:rgba(255,255,255,0.10) !important;
  border:1px solid rgba(255,255,255,0.18) !important;
  color:white !important; border-radius:8px !important; font-weight:600 !important;
}
section[data-testid="stSidebar"] .stButton>button:hover {
  background:rgba(255,255,255,0.20) !important;
}

#MainMenu,footer,header { visibility:hidden; }
::-webkit-scrollbar { width:6px; }
::-webkit-scrollbar-track { background:var(--bg2); }
::-webkit-scrollbar-thumb { background:var(--border2); border-radius:4px; }

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  gap:4px; background:var(--surface); padding:6px;
  border-radius:12px; border:1px solid var(--border); box-shadow:var(--shadow);
}
.stTabs [data-baseweb="tab"] {
  border-radius:8px; padding:8px 16px; color:var(--txt3);
  font-weight:600; font-size:0.83rem; font-family:'DM Sans',sans-serif;
}
.stTabs [aria-selected="true"] {
  background:linear-gradient(135deg,#4F46E5,#7C3AED) !important;
  color:white !important; border-bottom:none !important;
  box-shadow:0 4px 12px rgba(79,70,229,0.3) !important;
}

/* ── CARDS ── */
.sf-card {
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius); padding:22px 24px; margin:8px 0; box-shadow:var(--shadow);
}
.sf-metric {
  background:var(--surface); border:1px solid var(--border);
  border-radius:var(--radius); padding:20px 16px; text-align:center;
  transition:transform 0.2s,box-shadow 0.2s; position:relative; overflow:hidden;
}
.sf-metric:hover { transform:translateY(-2px); box-shadow:var(--shadow-lg); }
.sf-metric-num { font-family:'Lora',serif; font-size:2.1rem; font-weight:700; line-height:1; margin:4px 0; }
.sf-metric-lbl { font-size:0.72rem; color:var(--txt3); text-transform:uppercase; letter-spacing:0.08em; font-weight:600; margin-top:4px; }
.sf-section {
  font-family:'Lora',serif; font-size:1.2rem; font-weight:700;
  color:var(--txt); margin:20px 0 12px; padding-bottom:8px; border-bottom:2px solid var(--border);
}

/* ── TOPIC PILLS ── */
.topic-pill {
  border-radius:10px; padding:14px 18px; margin:8px 0;
  border:1px solid var(--border); background:var(--surface);
  position:relative; overflow:hidden; transition:box-shadow 0.2s;
}
.topic-pill:hover { box-shadow:var(--shadow-lg); }
.topic-pill::before {
  content:''; position:absolute; left:0; top:0; bottom:0;
  width:4px; border-radius:10px 0 0 10px;
}
.topic-pill.hard::before   { background:#DC2626; }
.topic-pill.medium::before { background:#D97706; }
.topic-pill.easy::before   { background:#16A34A; }
.topic-pill.completed { opacity:0.6; }
.topic-pill.completed::after {
  content:'✓ Done'; position:absolute; right:14px; top:50%;
  transform:translateY(-50%); color:#16A34A; font-weight:700; font-size:0.75rem;
  background:rgba(22,163,74,0.1); padding:2px 8px; border-radius:20px;
}

/* ── SESSION HEADERS ── */
.session-hdr { border-radius:10px; padding:12px 18px; font-weight:700; font-size:0.9rem; text-align:center; margin-bottom:12px; font-family:'Lora',serif; }
.morning-hdr { background:linear-gradient(135deg,#FEF3C7,#FDE68A); color:#92400E; border:1px solid #FCD34D; }
.evening-hdr { background:linear-gradient(135deg,#EDE9FE,#DDD6FE); color:#3730A3; border:1px solid #C4B5FD; }

/* ── DAY CARD ── */
.day-card { background:var(--surface); border:1px solid var(--border); border-radius:12px; padding:14px 12px; min-height:200px; }
.day-card.today { border-color:#4F46E5; box-shadow:0 0 0 2px rgba(79,70,229,0.15); }
.day-name  { font-family:'Lora',serif; font-weight:700; font-size:0.9rem; text-align:center; }
.day-date  { font-size:0.73rem; color:var(--txt3); text-align:center; margin-bottom:10px; }
.day-hours { font-size:0.7rem; color:#4F46E5; text-align:center; margin-bottom:6px; font-family:'JetBrains Mono',monospace; font-weight:600; }
.slot-hdr  { font-size:0.7rem; font-weight:700; margin:8px 0 4px; letter-spacing:0.03em; }
.slot-topic { font-size:0.71rem; color:var(--txt2); padding:3px 0 3px 8px; border-left:2px solid; margin:3px 0; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; }

/* ── BADGES ── */
.badge-weak { background:#FEE2E2; color:#DC2626; font-size:0.62rem; border-radius:4px; padding:2px 7px; font-weight:700; margin-left:5px; border:1px solid #FECACA; }
.badge-done { background:#DCFCE7; color:#16A34A; font-size:0.62rem; border-radius:4px; padding:2px 7px; font-weight:700; margin-left:5px; border:1px solid #BBF7D0; }
.res-tag { background:#EFF6FF; color:#1D4ED8; font-size:0.68rem; border-radius:5px; padding:2px 8px; margin:2px; display:inline-block; border:1px solid #BFDBFE; }

/* ── PROGRESS BAR ── */
.prog-bar-outer { background:var(--bg2); border-radius:20px; height:10px; overflow:hidden; margin:6px 0; border:1px solid var(--border); }
.prog-bar-inner  { height:100%; border-radius:20px; transition:width 0.5s ease; }

/* ── TIP CARDS ── */
.tip-card { border-radius:10px; padding:14px 16px; margin:6px 0; border-left:4px solid; font-size:0.88rem; }
.tip-info    { background:#EFF6FF; border-color:#3B82F6; color:#1E40AF; }
.tip-warn    { background:#FFFBEB; border-color:#F59E0B; color:#92400E; }
.tip-success { background:#F0FDF4; border-color:#22C55E; color:#15803D; }
.tip-danger  { background:#FFF1F2; border-color:#F43F5E; color:#9F1239; }

/* ── CYPHER BLOCK ── */
.cypher-block {
  background:#1E1B4B; border:1px solid #312E81; border-radius:10px; padding:18px;
  font-family:'JetBrains Mono',monospace; font-size:0.8rem; color:#A5B4FC;
  white-space:pre-wrap; line-height:1.7;
}

/* ── APP TITLE ── */
.app-title { font-family:'Lora',serif; font-size:2.2rem; font-weight:700; color:var(--txt); letter-spacing:-0.02em; }
.app-title span { background:linear-gradient(135deg,#4F46E5,#7C3AED); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.app-subtitle { color:var(--txt3); font-size:0.85rem; margin-top:5px; }

/* ── SIDEBAR ── */
.sb-brand { padding:16px 0 10px; text-align:center; }
.sb-brand-title { font-family:'Lora',serif; font-size:1.25rem; font-weight:700; }
.sb-brand-sub { font-size:0.68rem; color:rgba(255,255,255,0.42) !important; letter-spacing:0.08em; text-transform:uppercase; margin-top:2px; }
.sb-user-card { background:rgba(255,255,255,0.07); border:1px solid rgba(255,255,255,0.12); border-radius:12px; padding:14px 12px; text-align:center; margin:8px 0; }
.sb-avatar { width:54px; height:54px; border-radius:50%; background:linear-gradient(135deg,#6366F1,#8B5CF6); display:flex; align-items:center; justify-content:center; font-size:1.5rem; margin:0 auto 8px; box-shadow:0 4px 12px rgba(99,102,241,0.4); }

/* ── INPUTS ── */
.stTextInput input,.stNumberInput input {
  background:var(--surface) !important; color:var(--txt) !important;
  border:1px solid var(--border) !important; border-radius:8px !important;
}
.stButton>button {
  background:linear-gradient(135deg,#4F46E5,#7C3AED) !important;
  color:white !important; border:none !important; border-radius:8px !important;
  font-weight:600 !important; transition:all 0.2s !important;
  box-shadow:0 2px 8px rgba(79,70,229,0.25) !important;
}
.stButton>button:hover { transform:translateY(-1px) !important; box-shadow:0 6px 16px rgba(79,70,229,0.35) !important; }
.stDataFrame { border-radius:12px !important; overflow:hidden !important; border:1px solid var(--border) !important; }
.streamlit-expanderHeader { background:var(--surface) !important; border:1px solid var(--border) !important; border-radius:8px !important; font-weight:600 !important; }
div[data-baseweb="select"]>div { background:var(--surface) !important; border-color:var(--border) !important; border-radius:8px !important; }
hr { border-color:var(--border) !important; }
.goal-card { background:linear-gradient(135deg,#EDE9FE,#F5F3FF); border:1px solid #C4B5FD; border-radius:12px; padding:18px; margin:10px 0; }

/* ── AUTH ── */
.auth-logo { font-family:'Lora',serif; font-size:2rem; font-weight:700; text-align:center; margin-bottom:2px; }
.auth-logo span { background:linear-gradient(135deg,#4F46E5,#7C3AED); -webkit-background-clip:text; -webkit-text-fill-color:transparent; background-clip:text; }
.auth-sub { color:var(--txt3); font-size:0.8rem; text-align:center; margin-bottom:24px; letter-spacing:0.04em; }

/* ── OTP BOX ── */
.otp-box { background:linear-gradient(135deg,#F0FDF4,#DCFCE7); border:2px solid #22C55E; border-radius:14px; padding:20px 24px; text-align:center; margin:12px 0; }
.otp-code { font-family:'JetBrains Mono',monospace; font-size:2.8rem; font-weight:700; color:#15803D; letter-spacing:0.3em; }

/* ── PROFILE ── */
.profile-banner { background:linear-gradient(135deg,#2D2260,#1E1650); border-radius:16px; padding:32px; margin-bottom:24px; text-align:center; }

/* ── AI CHAT ── */
.chat-bubble-user {
  background:linear-gradient(135deg,#4F46E5,#7C3AED);
  color:white; border-radius:18px 18px 4px 18px;
  padding:12px 16px; margin:8px 0 8px 60px;
  font-size:0.9rem; line-height:1.6; box-shadow:0 2px 8px rgba(79,70,229,0.2);
}
.chat-bubble-ai {
  background:var(--surface); border:1px solid var(--border);
  color:var(--txt); border-radius:18px 18px 18px 4px;
  padding:12px 16px; margin:8px 60px 8px 0;
  font-size:0.9rem; line-height:1.6; box-shadow:var(--shadow);
}
.chat-label-user { text-align:right; font-size:0.72rem; color:var(--txt3); margin-bottom:3px; font-weight:600; }
.chat-label-ai   { text-align:left;  font-size:0.72rem; color:var(--txt3); margin-bottom:3px; font-weight:600; }
.quick-prompt-btn { display:inline-block; background:var(--surface); border:1px solid var(--border); border-radius:20px; padding:6px 14px; margin:4px; font-size:0.8rem; color:var(--accent); cursor:pointer; transition:all 0.2s; }
.quick-prompt-btn:hover { background:#EDE9FE; border-color:#4F46E5; }
.api-key-box { background:#EDE9FE; border:1px solid #C4B5FD; border-radius:12px; padding:16px; margin:12px 0; }

/* ── EMPTY STATE ── */
.empty-state { text-align:center; padding:60px 20px; color:var(--txt3); }
.empty-state .es-icon  { font-size:3.5rem; margin-bottom:16px; }
.empty-state .es-title { font-family:'Lora',serif; font-size:1.4rem; font-weight:700; color:var(--txt2); margin-bottom:8px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
#  SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────────────────
_defaults = {
    "logged_in":    False,
    "email":        "",
    "username":     "",
    "display_name": "",
    "page":         "main",   # "main" | "profile"
    "fp_step":      0,
    "fp_email":     "",
    "fp_otp":       "",
    "fp_ts":        None,
    "chat_history": [],       # AI chat history
    # gemini key hardcoded in ai_assistant.py — no session key needed
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ─────────────────────────────────────────────────────────────────────────────
#  SMALL HELPERS
# ─────────────────────────────────────────────────────────────────────────────
def progress_bar(pct, color="#4F46E5"):
    return f'<div class="prog-bar-outer"><div class="prog-bar-inner" style="width:{pct}%;background:{color}"></div></div>'

def tip_card(msg, kind="info"):
    return f'<div class="tip-card tip-{kind}">{msg}</div>'

def topic_pill_html(topic, weak_areas, completed):
    name  = topic.get("name","");    diff  = topic.get("difficulty","Easy")
    subj  = topic.get("subject",""); hours = topic.get("estimated_hours",1)
    res   = topic.get("resources",[])
    is_wk = name in weak_areas;      is_done = name in completed
    clr   = DIFFICULTY_COLOR.get(diff,"#16A34A")
    icon  = DIFFICULTY_ICON.get(diff,"🟢")
    cls   = diff.lower() + (" completed" if is_done else "")
    wb = '<span class="badge-weak">⚠ WEAK</span>' if is_wk  else ""
    db = '<span class="badge-done">✓ DONE</span>'  if is_done else ""
    rt = "".join(f'<span class="res-tag">📎 {r}</span>' for r in res)
    return f"""<div class="topic-pill {cls}">
      <div style="display:flex;justify-content:space-between;align-items:flex-start">
        <span style="color:{'#6B7280' if is_done else '#1A1310'};font-weight:600;font-size:0.92rem">{icon} {name} {wb}{db}</span>
        <span style="color:{clr};font-family:'JetBrains Mono',monospace;font-size:0.78rem;white-space:nowrap;margin-left:10px;background:rgba(0,0,0,0.04);padding:2px 8px;border-radius:20px">⏱ {hours}h</span>
      </div>
      <div style="color:#9C8E75;font-size:0.78rem;margin-top:5px">
        <span style="background:#F3F4F6;color:#374151;padding:1px 6px;border-radius:4px;font-size:0.7rem">{subj}</span>
        &nbsp;<span style="color:{clr};font-weight:600">{diff}</span>
      </div>
      <div style="margin-top:8px">{rt}</div></div>"""

def show_empty_state():
    st.markdown("""<div class="empty-state">
      <div class="es-icon">📚</div>
      <div class="es-title">Welcome to StudyFlow!</div>
      <div style="color:#9C8E75;font-size:0.88rem">
        No subjects yet.<br>Go to <strong>⚙️ Manage → 📗 Subjects</strong> to get started.
      </div></div>""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  FORGOT PASSWORD FLOW
# ─────────────────────────────────────────────────────────────────────────────
def show_forgot_password():
    st.markdown("### 🔓 Reset Password")

    # Step 1 — enter email
    if st.session_state.fp_step == 1:
        st.markdown("Enter your registered email to receive a verification code.")
        with st.form("fp_email_form"):
            fp_e = st.text_input("Email Address", placeholder="you@example.com")
            if st.form_submit_button("📧 Send Verification Code", use_container_width=True):
                fp_e = fp_e.strip().lower()
                if not auth.email_exists(fp_e):
                    st.error("❌ No account found with this email.")
                else:
                    otp = auth.generate_otp()
                    st.session_state.fp_email = fp_e
                    st.session_state.fp_otp   = otp
                    st.session_state.fp_ts    = datetime.now()
                    st.session_state.fp_step  = 2
                    st.rerun()

    # Step 2 — enter OTP + new password
    elif st.session_state.fp_step == 2:
        otp     = st.session_state.fp_otp
        ts      = st.session_state.fp_ts
        fp_e    = st.session_state.fp_email
        elapsed = (datetime.now() - ts).seconds if ts else 999

        st.markdown(f"""
        <div class="otp-box">
          <div style="font-size:0.82rem;color:#166534;margin-bottom:8px">
            📧 <strong>Verification Code</strong> sent to <code>{fp_e}</code>
            <br><span style="font-size:0.75rem;opacity:0.7">(Simulated — shown here for demo)</span>
          </div>
          <div class="otp-code">{otp}</div>
          <div style="font-size:0.72rem;color:#15803D;margin-top:8px">
            ⏱ Expires in {max(0,600-elapsed)//60}m {max(0,600-elapsed)%60}s
          </div>
        </div>""", unsafe_allow_html=True)

        if elapsed > 600:
            st.error("⏰ Code expired. Please start again.")
            st.session_state.fp_step = 1
            st.rerun()

        with st.form("fp_reset_form"):
            entered = st.text_input("Enter Verification Code", placeholder="6-digit code", max_chars=6)
            np1 = st.text_input("New Password",     type="password", placeholder="Min. 6 chars")
            np2 = st.text_input("Confirm Password", type="password", placeholder="Repeat")
            if st.form_submit_button("🔑 Reset Password", use_container_width=True):
                if entered.strip() != otp:
                    st.error("❌ Incorrect code.")
                elif np1 != np2:
                    st.error("❌ Passwords do not match.")
                else:
                    ok, msg = auth.reset_password(fp_e, np1)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.session_state.fp_step  = 0
                        st.session_state.fp_email = ""
                        st.session_state.fp_otp   = ""
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")


# ─────────────────────────────────────────────────────────────────────────────
#  AUTH PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_auth_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    _, c, _ = st.columns([1, 1.5, 1])
    with c:
        st.markdown(
            '<div class="auth-logo">📖 <span>StudyFlow</span></div>'
            '<div class="auth-sub">SMART STUDY PLANNER &nbsp;·&nbsp; KNOWLEDGE GRAPH ENGINE</div>',
            unsafe_allow_html=True)

        # ── Forgot password mode ───────────────────────────────────────────
        if st.session_state.fp_step > 0:
            show_forgot_password()
            st.markdown("<br>")
            if st.button("← Back to Login", key="back_login"):
                st.session_state.fp_step = 0
                st.rerun()
            return

        # ── Tabs ───────────────────────────────────────────────────────────
        login_tab, signup_tab = st.tabs(["🔑  Login", "✨  Sign Up"])

        with login_tab:
            st.markdown("")
            with st.form("login_form"):
                l_email = st.text_input("Email Address", placeholder="you@example.com")
                l_pass  = st.text_input("Password",      type="password", placeholder="••••••••")
                st.markdown("")
                if st.form_submit_button("🔑  Log In", use_container_width=True):
                    ok, msg, user = auth.authenticate(l_email, l_pass)
                    if ok:
                        st.session_state.logged_in    = True
                        st.session_state.email        = l_email.strip().lower()
                        st.session_state.username     = user["username"]
                        st.session_state.display_name = user["display_name"]
                        st.session_state.chat_history = []
                        for k in ["kg","planner","kg_for"]:
                            st.session_state.pop(k, None)
                        st.success(f"✅ Welcome back, {user['display_name']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {msg}")
            st.markdown("")
            if st.button("🔓 Forgot Password?", key="fp_btn", use_container_width=True):
                st.session_state.fp_step = 1
                st.rerun()

        with signup_tab:
            st.markdown("")
            with st.form("signup_form", clear_on_submit=True):
                s_name  = st.text_input("Full Name",         placeholder="Ali Raza")
                s_email = st.text_input("Email Address",     placeholder="ali@example.com")
                s_user  = st.text_input("Username",          placeholder="ali_raza",
                                        help="3-30 chars: letters, numbers, _ or -")
                sc1, sc2 = st.columns(2)
                s_pass  = sc1.text_input("Password",         type="password", placeholder="Min. 6 chars")
                s_pass2 = sc2.text_input("Confirm Password", type="password", placeholder="Repeat")
                s_hrs   = st.slider("Study hours / day", 1, 14, 4)
                st.markdown("")
                if st.form_submit_button("✨  Create Account", use_container_width=True):
                    ok, msg = auth.register(s_email, s_pass, s_pass2, s_name, s_user, s_hrs)
                    if ok:
                        st.success(f"✅ {msg}")
                        st.info("💡 Switch to Login tab and sign in.")
                    else:
                        st.error(f"❌ {msg}")

        st.markdown('<div style="text-align:center;font-size:0.75rem;color:#C8BFA6;margin-top:20px"></div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  GATE
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state.logged_in:
    show_auth_page()
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
#  LOAD KG
# ─────────────────────────────────────────────────────────────────────────────
email        = st.session_state.email
username     = st.session_state.username
display_name = st.session_state.display_name

if "kg" not in st.session_state or st.session_state.get("kg_for") != email:
    ui = auth.get_user(email) or {}
    st.session_state.kg      = StudyKnowledgeGraph.load(ui.get("username", username), ui.get("hours_per_day", 4))
    st.session_state.planner = StudyPlanner(st.session_state.kg)
    st.session_state.kg_for  = email
    username = st.session_state.kg.username
    st.session_state.username = username

kg: StudyKnowledgeGraph = st.session_state.kg
planner: StudyPlanner   = st.session_state.planner
has_subjects            = len(kg.subjects) > 0


# ─────────────────────────────────────────────────────────────────────────────
#  PROFILE PAGE
# ─────────────────────────────────────────────────────────────────────────────
def show_profile_page():
    ui  = auth.get_user(email) or {}
    pic = ui.get("profile_pic")

    # Banner
    pic_html = (auth.b64_img_tag(pic, 90, "display:block;margin:0 auto 12px;")
                if pic else '<div class="sb-avatar" style="width:90px;height:90px;font-size:2.5rem;margin:0 auto 12px;">🎓</div>')
    st.markdown(f"""
    <div class="profile-banner">
      {pic_html}
      <div style="font-family:'Lora',serif;font-size:1.5rem;font-weight:700;color:white">{ui.get('display_name','')}</div>
      <div style="font-size:0.8rem;color:rgba(255,255,255,0.5);margin-top:4px">@{ui.get('username','')} &nbsp;·&nbsp; {ui.get('email','')}</div>
      <div style="font-size:0.75rem;color:rgba(255,255,255,0.35);margin-top:4px">Member since {ui.get('joined','')}</div>
    </div>""", unsafe_allow_html=True)

    if st.button("← Back to Dashboard", key="back_dash"):
        st.session_state.page = "main"
        st.rerun()

    st.divider()
    st.markdown("### ✏️ Edit Profile")

    pic_col, info_col = st.columns([1, 2])

    with pic_col:
        st.markdown("**Profile Picture**")
        uploaded = st.file_uploader("Upload photo (PNG/JPG)", type=["png","jpg","jpeg"],
                                    key="pic_upload", label_visibility="collapsed")
        if uploaded:
            b64 = auth.image_to_b64(uploaded)
            if b64:
                st.markdown(auth.b64_img_tag(b64, 120, "display:block;margin:0 auto;"), unsafe_allow_html=True)
                if st.button("💾 Save Photo"):
                    auth.update_profile(email, {"profile_pic": b64})
                    st.success("✅ Photo saved!")
                    st.rerun()
            else:
                st.error("Could not process image. Make sure Pillow is installed.")
        elif pic:
            st.markdown(auth.b64_img_tag(pic, 120, "display:block;margin:0 auto;"), unsafe_allow_html=True)
            if st.button("🗑️ Remove Photo"):
                auth.update_profile(email, {"profile_pic": None})
                st.rerun()
        else:
            st.markdown('<div style="width:120px;height:120px;border-radius:50%;background:linear-gradient(135deg,#6366F1,#8B5CF6);display:flex;align-items:center;justify-content:center;font-size:3rem;margin:0 auto;">🎓</div>', unsafe_allow_html=True)
            st.markdown('<div style="text-align:center;font-size:0.75rem;color:#9C8E75;margin-top:8px">No photo yet</div>', unsafe_allow_html=True)

    with info_col:
        with st.form("profile_form"):
            pf1, pf2 = st.columns(2)
            new_dn   = pf1.text_input("Full Name",    value=ui.get("display_name",""))
            new_un   = pf2.text_input("Username",     value=ui.get("username",""),
                                      help="3-30 chars: letters, numbers, _ or -")
            pf3, pf4 = st.columns(2)
            new_ph   = pf3.text_input("Phone",        value=ui.get("phone",""),       placeholder="+92 300 1234567")
            new_uni  = pf4.text_input("University",   value=ui.get("university",""),  placeholder="FAST NUCES")
            pf5, pf6 = st.columns(2)
            new_dept = pf5.text_input("Department",   value=ui.get("department",""),  placeholder="Computer Science")
            new_sem  = pf6.text_input("Semester",     value=ui.get("semester",""),    placeholder="Semester 5")
            new_bio  = st.text_area("Bio / Study Goals", value=ui.get("bio",""),
                                    height=100, placeholder="Tell us about your study goals...")
            new_hrs  = st.slider("Study hours / day", 1, 14, int(ui.get("hours_per_day", 4)))
            st.markdown("<br>")
            if st.form_submit_button("💾 Save Profile", use_container_width=True):
                ok, msg = auth.update_profile(email, {
                    "display_name": new_dn, "username":     new_un,
                    "phone":        new_ph, "university":   new_uni,
                    "department":   new_dept, "semester":   new_sem,
                    "bio":          new_bio, "hours_per_day": new_hrs,
                })
                if ok:
                    st.session_state.display_name = new_dn.strip() or display_name
                    st.session_state.username     = new_un.strip().lower() or username
                    kg.update_available_hours(kg.username, new_hrs)
                    kg.save()
                    for k in ["kg","planner","kg_for"]:
                        st.session_state.pop(k, None)
                    st.success(f"✅ {msg}")
                    st.rerun()
                else:
                    st.error(f"❌ {msg}")

    st.divider()
    st.markdown("### 🔒 Change Password")
    with st.form("pw_form"):
        cp1, cp2, cp3 = st.columns(3)
        old_pw = cp1.text_input("Current Password", type="password")
        new_pw = cp2.text_input("New Password",     type="password", placeholder="Min. 6 chars")
        cnf_pw = cp3.text_input("Confirm New",      type="password")
        if st.form_submit_button("🔒 Update Password", use_container_width=True):
            ok_a, _, _ = auth.authenticate(email, old_pw)
            if not ok_a:
                st.error("❌ Current password is incorrect.")
            elif new_pw != cnf_pw:
                st.error("❌ Passwords do not match.")
            else:
                ok, msg = auth.reset_password(email, new_pw)
                st.success(f"✅ {msg}") if ok else st.error(f"❌ {msg}")


# ─────────────────────────────────────────────────────────────────────────────
#  SIDEBAR (fixed, no collapse)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        '<div class="sb-brand">'
        '<div class="sb-brand-title">📖 StudyFlow</div>'
        '<div class="sb-brand-sub">Smart Study Planner</div>'
        '</div>', unsafe_allow_html=True)
    st.divider()

    ui    = auth.get_user(email) or {}
    stats = planner.get_progress_stats(username)
    goal  = kg.get_goal(username)
    pct   = stats["completion_pct"]
    pic   = ui.get("profile_pic")

    avatar_html = (auth.b64_img_tag(pic, 54) if pic
                   else '<div class="sb-avatar">🎓</div>')

    st.markdown(f"""
    <div class="sb-user-card">
      {avatar_html}
      <div style="font-family:'Lora',serif;font-size:1rem;font-weight:700;color:white;margin-top:6px">{display_name}</div>
      <div style="font-size:0.7rem;color:rgba(255,255,255,0.42)">@{username}</div>
      {f'<div style="font-size:0.72rem;color:rgba(255,255,255,0.42);margin-top:2px">{ui.get("university","")}</div>' if ui.get("university") else ''}
      {f'<div style="font-size:0.7rem;color:rgba(255,255,255,0.35)">{ui.get("department","")}{" · " + ui.get("semester","") if ui.get("semester") else ""}</div>' if ui.get("department") else ''}
      <div style="font-size:0.72rem;color:rgba(255,255,255,0.42);margin-top:4px">⏰ {ui.get('hours_per_day',4)}h/day &nbsp;·&nbsp; 📚 {stats['subjects_count']} subjects</div>
      <div style="margin-top:10px">
        <div style="font-size:0.68rem;color:rgba(255,255,255,0.42);margin-bottom:4px">Progress {pct}%</div>
        <div style="background:rgba(255,255,255,0.10);border-radius:20px;height:6px;overflow:hidden">
          <div style="width:{pct}%;background:linear-gradient(90deg,#6366F1,#8B5CF6);height:100%;border-radius:20px"></div>
        </div>
      </div>
    </div>""", unsafe_allow_html=True)

    if st.button("👤 My Profile", key="profile_btn", use_container_width=True):
        st.session_state.page = "profile"
        st.rerun()

    if goal:
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.06);border:1px solid rgba(255,255,255,0.10);border-radius:10px;padding:10px;margin:6px 0;text-align:center">
          <div style="font-size:0.62rem;color:rgba(255,255,255,0.38);text-transform:uppercase;letter-spacing:0.08em">🎯 Goal</div>
          <div style="font-size:0.88rem;font-weight:700;color:white;margin-top:3px">{goal['exam_name']}</div>
          <div style="font-size:0.7rem;color:rgba(255,255,255,0.42)">{goal['target_date']} · {goal['weekly_hours']}h/wk</div>
        </div>""", unsafe_allow_html=True)

    weak = stats["weak_areas"]
    if weak:
        st.markdown('<div style="font-size:0.72rem;color:rgba(255,255,255,0.38);text-transform:uppercase;letter-spacing:0.08em;margin:10px 0 5px">⚠️ Weak Areas</div>', unsafe_allow_html=True)
        for w in weak:
            st.markdown(f'<div style="border-left:3px solid #F87171;padding:3px 8px;margin:2px 0;font-size:0.78rem;color:rgba(255,255,255,0.72);background:rgba(248,113,113,0.07);border-radius:0 5px 5px 0">{w}</div>', unsafe_allow_html=True)

    if stats["subjects"]:
        st.divider()
        st.markdown('<div style="font-size:0.72rem;color:rgba(255,255,255,0.38);text-transform:uppercase;letter-spacing:0.08em;margin-bottom:6px">📗 Subjects</div>', unsafe_allow_html=True)
        for s in stats["subjects"]:
            st.markdown(f'<div style="color:rgba(165,180,252,0.8);font-size:0.8rem;padding:2px 0">▸ {s}</div>', unsafe_allow_html=True)

    st.divider()
    if st.button("🚪 Log Out", key="logout_btn", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.session_state.logged_in = False
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  ROUTE TO PROFILE PAGE
# ─────────────────────────────────────────────────────────────────────────────
if st.session_state.page == "profile":
    show_profile_page()
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN HEADER
# ─────────────────────────────────────────────────────────────────────────────
stats_h = planner.get_progress_stats(username)
c1, c2  = st.columns([3, 1])
with c1:
    st.markdown(
        f'<div class="app-title">📖 <span>StudyFlow</span></div>'
        f'<div class="app-subtitle">Knowledge Graph Planner &nbsp;·&nbsp; '
        f'{datetime.now().strftime("%A, %d %B %Y")} &nbsp;·&nbsp; 👤 <strong>{display_name}</strong></div>',
        unsafe_allow_html=True)
with c2:
    st.markdown(
        f'<div style="text-align:right;padding-top:10px">'
        f'<div style="font-size:2rem;font-family:\'Lora\',serif;font-weight:700;color:#4F46E5">{stats_h["completion_pct"]}%</div>'
        f'<div style="font-size:0.72rem;color:#9C8E75;text-transform:uppercase;letter-spacing:0.08em">Overall Progress</div>'
        f'{progress_bar(stats_h["completion_pct"])}</div>',
        unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  TABS
# ─────────────────────────────────────────────────────────────────────────────
tab1,tab2,tab3,tab4,tab5,tab6,tab7 = st.tabs([
    "🏠 Dashboard", "📅 Today's Plan", "🗓️ Weekly Plan",
    "✅ Progress", "🕸️ Knowledge Graph", "🤖 AI Assistant", "⚙️ Manage",
])


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 1 — DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════
with tab1:
    if not has_subjects:
        show_empty_state()
    else:
        stats = planner.get_progress_stats(username)
        diff  = stats["difficulty_distribution"]
        goal  = kg.get_goal(username)

        m1,m2,m3,m4,m5 = st.columns(5)
        for col,(num,lbl,icon,clr) in zip([m1,m2,m3,m4,m5],[
            (str(stats["subjects_count"]),     "Subjects",      "📚","#4F46E5"),
            (str(stats["total_topics"]),        "Topics",        "📝","#0EA5E9"),
            (str(stats["completed_count"]),     "Completed",     "✅","#16A34A"),
            (str(stats["weak_areas_count"]),    "Weak Areas",    "⚠️","#DC2626"),
            (f"{stats['pending_hours']:.0f}h",  "Hrs Remaining", "⏳","#D97706"),
        ]):
            col.markdown(f'<div class="sf-metric"><div style="position:absolute;top:0;left:0;right:0;height:3px;background:{clr};border-radius:14px 14px 0 0"></div><div style="font-size:1.4rem;margin-bottom:4px">{icon}</div><div class="sf-metric-num" style="color:{clr}">{num}</div><div class="sf-metric-lbl">{lbl}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>")
        ch1,ch2,ch3 = st.columns([2,2,1])
        with ch1:
            fig = go.Figure(go.Pie(labels=list(diff.keys()),values=list(diff.values()),hole=0.55,
                                   marker_colors=["#DC2626","#D97706","#16A34A"],textfont_size=13))
            fig.update_layout(title=dict(text="Difficulty Distribution",font=dict(color="#2C2416",size=14,family="Lora")),
                              paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#6B5E45",height=280,
                              legend=dict(font=dict(color="#6B5E45",size=11),bgcolor="rgba(0,0,0,0)"),margin=dict(t=40,b=10,l=10,r=10))
            st.plotly_chart(fig, use_container_width=True)
        with ch2:
            subs=stats["subjects"]; tc=[len(kg.get_subject_topics(s)) for s in subs]
            dc=[sum(1 for t in kg.get_subject_topics(s) if t["name"] in kg.get_completed_topics(username)) for s in subs]
            fig2=go.Figure()
            fig2.add_trace(go.Bar(name="Total",x=subs,y=tc,marker_color="#C7D2FE",marker_line_width=0))
            fig2.add_trace(go.Bar(name="Completed",x=subs,y=dc,marker_color="#4F46E5",marker_line_width=0))
            fig2.update_layout(barmode="overlay",title=dict(text="Topics per Subject",font=dict(color="#2C2416",size=14,family="Lora")),
                               paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#6B5E45",height=280,
                               xaxis=dict(gridcolor="#DDD5C0",color="#6B5E45"),yaxis=dict(gridcolor="#DDD5C0",color="#6B5E45"),
                               legend=dict(font=dict(color="#6B5E45"),bgcolor="rgba(0,0,0,0)"),margin=dict(t=40,b=10,l=10,r=10))
            st.plotly_chart(fig2, use_container_width=True)
        with ch3:
            lh=stats["logged_hours"]; gh=goal["weekly_hours"] if goal else 20
            pg=min(lh/gh*100,100) if gh else 0
            st.markdown(f'<div class="sf-card" style="text-align:center;padding:20px"><div style="font-size:0.72rem;color:#9C8E75;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:8px">⏱ Logged</div><div style="font-family:\'Lora\',serif;font-size:2.2rem;font-weight:700;color:#4F46E5">{lh:.1f}h</div><div style="font-size:0.78rem;color:#9C8E75">of {gh}h goal</div>{progress_bar(pg,"#16A34A")}<div style="font-size:0.72rem;color:#16A34A;margin-top:4px">{pg:.0f}% done</div><div style="margin-top:14px;border-top:1px solid #DDD5C0;padding-top:10px"><div style="font-size:0.72rem;color:#9C8E75;margin-bottom:4px">Sessions</div><div style="font-family:\'Lora\',serif;font-size:1.6rem;font-weight:700;color:#D97706">{len(kg.get_sessions_for_student(username))}</div></div></div>', unsafe_allow_html=True)

        weak = stats["weak_areas"]
        if weak:
            st.markdown('<div class="sf-section">⚠️ Areas Needing Focus</div>', unsafe_allow_html=True)
            cols=st.columns(min(len(weak),4)); all_t=kg.get_all_topics_for_student(username)
            for i,w in enumerate(weak):
                td=next((t for t in all_t if t["name"]==w),{}); clr=DIFFICULTY_COLOR.get(td.get("difficulty","Easy"),"#888")
                with cols[i%len(cols)]:
                    st.markdown(f'<div style="background:#FFF7ED;border:1px solid {clr}40;border-top:3px solid {clr};border-radius:12px;padding:16px;text-align:center;margin:4px 0"><div style="font-size:1.4rem">⚠️</div><div style="font-weight:700;color:#1A1310;margin-top:6px;font-size:0.9rem">{w}</div><div style="color:{clr};font-size:0.78rem;font-weight:600">{td.get("difficulty","")}</div><div style="color:#9C8E75;font-size:0.75rem">{td.get("subject","")}</div></div>', unsafe_allow_html=True)

        if goal:
            st.markdown('<div class="sf-section">🎯 Study Goal</div>', unsafe_allow_html=True)
            try: dl=(datetime.strptime(goal["target_date"],"%Y-%m-%d")-datetime.now()).days
            except: dl="?"
            g1,g2,g3,g4=st.columns(4)
            for col,lbl,val,clr in [(g1,"🏆 Exam",goal["exam_name"],"#4F46E5"),(g2,"📅 Target",goal["target_date"],"#2C2416"),(g3,"📆 Days Left",str(dl),"#DC2626"),(g4,"⏱ Weekly",f"{goal['weekly_hours']}h","#16A34A")]:
                col.markdown(f'<div class="sf-card" style="text-align:center"><div style="font-size:0.7rem;color:#9C8E75;text-transform:uppercase;letter-spacing:0.08em">{lbl}</div><div style="font-family:\'Lora\',serif;font-size:1.1rem;font-weight:700;color:{clr};margin-top:6px">{val}</div></div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 2 — TODAY'S PLAN
# ══════════════════════════════════════════════════════════════════════════════
with tab2:
    if not has_subjects: show_empty_state()
    else:
        plan=planner.get_today_plan(username); weak_a=plan["weak_areas"]; completed=plan["completed"]
        ch1,ch2,ch3=st.columns([3,1,1])
        ch1.markdown(f'<div style="font-family:\'Lora\',serif;font-size:1.5rem;font-weight:700;color:#2C2416">📅 Today\'s Plan</div><div style="color:#9C8E75;font-size:0.85rem">{plan["date"]}</div>', unsafe_allow_html=True)
        ch2.markdown(f'<div class="sf-metric" style="border-top:3px solid #4F46E5"><div class="sf-metric-num" style="color:#4F46E5">{plan["total_hours"]:.1f}h</div><div class="sf-metric-lbl">Planned</div></div>', unsafe_allow_html=True)
        ch3.markdown(f'<div class="sf-metric" style="border-top:3px solid #DC2626"><div class="sf-metric-num" style="color:#DC2626">{len(weak_a)}</div><div class="sf-metric-lbl">Weak Areas</div></div>', unsafe_allow_html=True)

        avail=kg.get_student_info(username).get("available_hours",4)
        if plan["total_hours"]>avail:
            st.markdown(tip_card(f"⚡ Plan ({plan['total_hours']:.1f}h) exceeds your daily limit ({avail}h). Prioritise Hard topics!","warn"), unsafe_allow_html=True)

        st.markdown("<br>")
        cm,ce=st.columns(2)
        with cm:
            st.markdown('<div class="session-hdr morning-hdr">🌅 Morning Session</div>', unsafe_allow_html=True)
            if plan["morning"]:
                for t in plan["morning"]: st.markdown(topic_pill_html(t,weak_a,completed), unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#9C8E75;padding:20px;text-align:center;background:#F9F6EF;border-radius:10px;border:1px dashed #DDD5C0">No morning topics</div>', unsafe_allow_html=True)
        with ce:
            st.markdown('<div class="session-hdr evening-hdr">🌙 Evening Session</div>', unsafe_allow_html=True)
            if plan["evening"]:
                for t in plan["evening"]: st.markdown(topic_pill_html(t,weak_a,completed), unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#9C8E75;padding:20px;text-align:center;background:#F9F6EF;border-radius:10px;border:1px dashed #DDD5C0">No evening topics</div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-section">💡 Smart Tips</div>', unsafe_allow_html=True)
        for tip in plan["tips"]:
            kind = "danger" if "🔴" in tip else ("warn" if "⚠" in tip or "⚡" in tip else "info")
            st.markdown(tip_card(tip, kind), unsafe_allow_html=True)

        st.markdown('<div class="sf-section">📝 Log Study Session</div>', unsafe_allow_html=True)
        all_tn=list(kg.topics.keys())
        if all_tn:
            lc1,lc2,lc3,lc4=st.columns([2,1,1,1])
            lt=lc1.selectbox("Topic",all_tn,key="log_topic")
            lh=lc2.number_input("Hours",0.25,8.0,1.0,0.25,key="log_hours")
            lm=lc3.selectbox("Mood",["😄 Great","😊 Good","😐 Okay","😓 Tired","😩 Difficult"],key="log_mood")
            lc4.markdown("<br>")
            if lc4.button("📝 Log"):
                kg.log_session(username,lt,lh,lm.split()[0]); kg.save()
                st.success(f"✅ Logged {lh}h for {lt}!"); st.rerun()
        sess=kg.get_sessions_for_student(username)
        if sess:
            st.markdown("**Recent Sessions:**")
            st.dataframe(pd.DataFrame(sess[-5:][::-1])[["date","timestamp","topic","hours","mood"]], use_container_width=True, hide_index=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 3 — WEEKLY PLAN
# ══════════════════════════════════════════════════════════════════════════════
with tab3:
    if not has_subjects: show_empty_state()
    else:
        weekly=planner.generate_weekly_plan(username); ww=kg.get_weak_areas(username); dw=kg.get_completed_topics(username)
        th=sum(d["total_hours"] for d in weekly)
        st.markdown('<div style="font-family:\'Lora\',serif;font-size:1.5rem;font-weight:700;color:#2C2416">🗓️ 7-Day Schedule</div>', unsafe_allow_html=True)
        s1,s2,s3=st.columns(3)
        s1.metric("📊 Weekly Total",f"{th:.1f} hrs"); s2.metric("📅 Daily Avg",f"{th/7:.1f} hrs"); s3.metric("📚 Subjects",len(stats_h["subjects"]))
        st.markdown("<br>")
        dc=st.columns(7)
        for i,day in enumerate(weekly):
            with dc[i]:
                is_today=(i==0); cc="day-card today" if is_today else "day-card"; nc="#4F46E5" if is_today else "#2C2416"
                def si(topics):
                    parts=[]
                    for t in topics:
                        clr=DIFFICULTY_COLOR.get(t.get("difficulty","Easy"),"#888"); pfx="⚠ " if t["name"] in ww else ("✓ " if t["name"] in dw else "")
                        parts.append(f'<div class="slot-topic" style="border-color:{clr}">{pfx}{t["name"]}</div>')
                    return "".join(parts) or '<div style="color:#C8BFA6;font-size:0.7rem">—</div>'
                st.markdown(f'<div class="{cc}"><div class="day-name" style="color:{nc}">{day["day"]}</div><div class="day-date">{day["date"]}</div><div class="day-hours">⏱ {day["total_hours"]:.1f}h</div><div style="border-top:1px solid #DDD5C0;padding-top:8px"><div class="slot-hdr" style="color:#92400E">🌅 Morning</div>{si(day["morning"])}<div class="slot-hdr" style="color:#3730A3;margin-top:6px">🌙 Evening</div>{si(day["evening"])}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-section">📋 Full Schedule</div>', unsafe_allow_html=True)
        rows=[]
        for day in weekly:
            for sn,topics in [("🌅 Morning",day["morning"]),("🌙 Evening",day["evening"])]:
                for t in topics:
                    rows.append({"Day":day["day"],"Date":day["date"],"Session":sn,"Topic":("⚠️ " if t["name"] in ww else "")+t["name"],"Subject":t.get("subject",""),"Difficulty":DIFFICULTY_ICON.get(t.get("difficulty","Easy"),"")+t.get("difficulty","Easy"),"Hours":t.get("estimated_hours",1)})
        if rows:
            df=pd.DataFrame(rows); st.dataframe(df,use_container_width=True,hide_index=True)
            st.download_button("📥 Download CSV",df.to_csv(index=False),file_name=f"plan_{username}_{datetime.now().strftime('%Y%m%d')}.csv",mime="text/csv")


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 4 — PROGRESS
# ══════════════════════════════════════════════════════════════════════════════
with tab4:
    if not has_subjects: show_empty_state()
    else:
        stats=planner.get_progress_stats(username); comp=kg.get_completed_topics(username); all_t=kg.get_all_topics_for_student(username)
        st.markdown('<div style="font-family:\'Lora\',serif;font-size:1.5rem;font-weight:700;color:#2C2416">✅ Progress Tracker</div>', unsafe_allow_html=True)
        pc1,pc2,pc3=st.columns(3)
        pc1.markdown(f'<div class="sf-card" style="text-align:center"><div style="font-size:0.72rem;color:#9C8E75;text-transform:uppercase;letter-spacing:0.08em">Completion</div><div style="font-family:\'Lora\',serif;font-size:3rem;font-weight:700;color:#4F46E5;line-height:1;margin:10px 0">{stats["completion_pct"]}%</div>{progress_bar(stats["completion_pct"])}<div style="font-size:0.8rem;color:#6B5E45;margin-top:8px">{stats["completed_count"]} of {stats["total_topics"]} topics</div></div>', unsafe_allow_html=True)
        pc2.markdown(f'<div class="sf-card" style="text-align:center"><div style="font-size:0.72rem;color:#9C8E75;text-transform:uppercase;letter-spacing:0.08em">Hours Logged</div><div style="font-family:\'Lora\',serif;font-size:3rem;font-weight:700;color:#16A34A;line-height:1;margin:10px 0">{stats["logged_hours"]:.1f}h</div><div style="font-size:0.8rem;color:#6B5E45">{len(kg.get_sessions_for_student(username))} sessions</div></div>', unsafe_allow_html=True)
        pc3.markdown(f'<div class="sf-card" style="text-align:center"><div style="font-size:0.72rem;color:#9C8E75;text-transform:uppercase;letter-spacing:0.08em">Pending</div><div style="font-family:\'Lora\',serif;font-size:3rem;font-weight:700;color:#DC2626;line-height:1;margin:10px 0">{stats["pending_hours"]:.0f}h</div><div style="font-size:0.8rem;color:#6B5E45">{stats["pending_count"]} topics left</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-section">📚 By Subject</div>', unsafe_allow_html=True)
        for sub in stats["subjects"]:
            st_list=kg.get_subject_topics(sub); done=[t for t in st_list if t["name"] in comp]; sp=(len(done)/len(st_list)*100) if st_list else 0
            clr="#16A34A" if sp==100 else ("#D97706" if sp>50 else "#4F46E5")
            st.markdown(f'<div class="sf-card" style="padding:16px 20px;margin:8px 0"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px"><div style="font-weight:700;color:#2C2416">📗 {sub}</div><div style="font-family:\'JetBrains Mono\',monospace;font-size:0.85rem;color:{clr};font-weight:700">{len(done)}/{len(st_list)} ({sp:.0f}%)</div></div>{progress_bar(sp,clr)}</div>', unsafe_allow_html=True)

        st.markdown('<div class="sf-section">🔘 Mark Completion</div>', unsafe_allow_html=True)
        mc1,mc2=st.columns(2)
        with mc1:
            pending=[t["name"] for t in all_t if t["name"] not in comp]
            if pending:
                mk=st.selectbox("Mark as Completed",pending,key="mark_done")
                if st.button("✅ Mark Completed"):
                    kg.mark_completed(username,mk); kg.save(); st.success(f"✅ '{mk}' done!"); st.rerun()
            else: st.success("🎉 All topics completed!")
        with mc2:
            if comp:
                um=st.selectbox("Unmark",comp,key="unmark_done")
                if st.button("↩️ Unmark"):
                    kg.unmark_completed(username,um); kg.save(); st.warning(f"↩️ '{um}' unmarked."); st.rerun()

        sess=kg.get_sessions_for_student(username)
        if sess:
            st.markdown('<div class="sf-section">📈 Session History</div>', unsafe_allow_html=True)
            fig=px.bar(pd.DataFrame(sess),x="date",y="hours",color="topic",title="Hours per Day",color_discrete_sequence=px.colors.qualitative.Set2)
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="rgba(0,0,0,0)",font_color="#6B5E45",height=280,margin=dict(t=40,b=10,l=10,r=10),title=dict(font=dict(color="#2C2416",size=14,family="Lora")),xaxis=dict(gridcolor="#DDD5C0",color="#6B5E45",title=""),yaxis=dict(gridcolor="#DDD5C0",color="#6B5E45",title="Hours"),legend=dict(font=dict(color="#6B5E45"),bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 5 — KNOWLEDGE GRAPH
# ══════════════════════════════════════════════════════════════════════════════
with tab5:
    st.markdown('<div style="font-family:\'Lora\',serif;font-size:1.5rem;font-weight:700;color:#2C2416">🕸️ Knowledge Graph</div>', unsafe_allow_html=True)
    if not has_subjects: show_empty_state()
    else:
        vc1,vc2=st.columns([4,1])
        with vc2:
            show_all=st.checkbox("Show full graph",value=False)
            st.markdown('<div class="sf-section" style="font-size:0.85rem">Legend</div>', unsafe_allow_html=True)
            for lbl,clr in [("🔵 Student","#4F46E5"),("🟣 Subject","#7C3AED"),("🔴 Hard","#DC2626"),("🟡 Medium","#D97706"),("🟢 Easy","#16A34A"),("⬜ Done","#9CA3AF")]:
                st.markdown(f'<div style="font-size:0.82rem;color:{clr};padding:2px 0">{lbl}</div>', unsafe_allow_html=True)
            st.markdown("---"); gs=kg.get_graph_stats()
            st.metric("Nodes",gs["nodes"]); st.metric("Edges",gs["edges"])
        with vc1:
            gd=kg.get_graph_for_visualization(student_name=None if show_all else username)
            cset=set(kg.get_completed_topics(username))
            rc={"STUDIES":"#4F46E5","HAS":"#DDD5C0","WEAK_IN":"#DC2626","COMPLETED":"#16A34A"}
            traces=[]
            for e in gd["edges"]:
                traces.append(go.Scatter(x=[e["x0"],e["x1"],None],y=[e["y0"],e["y1"],None],mode="lines",line=dict(width=1.5,color=rc.get(e["relation"],"#DDD5C0")),hoverinfo="none",showlegend=False))
            for nt,cfg in {"Student":dict(color="#4F46E5",size=24,symbol="circle"),"Subject":dict(color="#7C3AED",size=18,symbol="diamond")}.items():
                nodes=[n for n in gd["nodes"] if n["type"]==nt]
                if nodes:
                    traces.append(go.Scatter(x=[n["x"] for n in nodes],y=[n["y"] for n in nodes],mode="markers+text",marker=dict(size=cfg["size"],color=cfg["color"],symbol=cfg["symbol"],line=dict(width=2,color="white")),text=[n["name"] for n in nodes],textposition="top center",textfont=dict(color="#2C2416",size=11),hoverinfo="text",name=nt))
            for diff,clr in DIFFICULTY_COLOR.items():
                ns=[n for n in gd["nodes"] if n["type"]=="Topic" and n.get("difficulty")==diff]
                if ns:
                    traces.append(go.Scatter(x=[n["x"] for n in ns],y=[n["y"] for n in ns],mode="markers+text",marker=dict(size=[8 if n["name"] in cset else 11 for n in ns],color=[clr if n["name"] not in cset else "#9CA3AF" for n in ns],line=dict(width=1,color="white"),symbol=["circle-open" if n["name"] in cset else "circle" for n in ns]),text=[n["name"] for n in ns],textposition="top center",textfont=dict(color="#6B5E45",size=8),hoverinfo="text",name=f"Topic–{diff}"))
            if traces:
                fig=go.Figure(data=traces,layout=go.Layout(showlegend=True,hovermode="closest",paper_bgcolor="rgba(0,0,0,0)",plot_bgcolor="#FDFAF4",height=520,margin=dict(l=10,r=10,t=10,b=10),legend=dict(font=dict(color="#6B5E45",size=11),bgcolor="rgba(253,250,244,0.9)",bordercolor="#DDD5C0",borderwidth=1),xaxis=dict(showgrid=False,zeroline=False,showticklabels=False),yaxis=dict(showgrid=False,zeroline=False,showticklabels=False)))
                st.plotly_chart(fig, use_container_width=True)
            else: st.info("Add topics to see the graph.")
        with st.expander("📝 Neo4j Cypher Queries"):
            for title,q in [("Study Plan",planner.neo4j_study_plan_query(username)),("Weak Areas",planner.neo4j_weak_areas_query(username)),("Progress",planner.neo4j_progress_query(username))]:
                st.markdown(f"##### {title}"); st.markdown(f'<div class="cypher-block">{q}</div>', unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 6 — AI ASSISTANT
# ══════════════════════════════════════════════════════════════════════════════
with tab6:
    st.markdown('<div style="font-family:\'Lora\',serif;font-size:1.5rem;font-weight:700;color:#2C2416">🤖 AI Study Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div style="color:#9C8E75;font-size:0.85rem;margin-bottom:16px">Powered by Gemini 2.0 Flash — Knows your subjects, topics, weak areas & progress</div>', unsafe_allow_html=True)

    # ── Build student context ──────────────────────────────────────────────
    ui_data     = auth.get_user(email) or {}
    all_topics  = kg.get_all_topics_for_student(username)
    weak_areas  = kg.get_weak_areas(username)
    completed   = kg.get_completed_topics(username)
    sessions    = kg.get_sessions_for_student(username)
    goal        = kg.get_goal(username)
    subjects    = kg.get_student_subjects(username)
    pending     = [t["name"] for t in all_topics if t["name"] not in completed]

    student_ctx = build_student_context(
        display_name  = display_name,
        username      = username,
        subjects      = subjects,
        all_topics    = all_topics,
        weak_areas    = weak_areas,
        completed     = completed,
        sessions      = sessions,
        goal          = goal,
        hours_per_day = ui_data.get("hours_per_day", 4),
        university    = ui_data.get("university", ""),
        department    = ui_data.get("department", ""),
        semester      = ui_data.get("semester", ""),
    )

    # ── Quick prompt buttons ───────────────────────────────────────────────
    quick_prompts = get_quick_prompts(weak_areas, subjects, pending)

    st.markdown("**💡 Quick Questions:**")
    qp_cols = st.columns(3)
    for i, prompt in enumerate(quick_prompts):
        with qp_cols[i % 3]:
            if st.button(prompt, key=f"qp_{i}", use_container_width=True):
                st.session_state.chat_history.append(
                    {"role":"user","parts":[prompt]}
                )
                with st.spinner("🤖 Thinking..."):
                    reply = chat_with_ai(
                        prompt,
                        st.session_state.chat_history[:-1],
                        student_ctx,
                    )
                st.session_state.chat_history.append(
                    {"role":"model","parts":[reply]}
                )
                st.rerun()

    st.divider()

    # ── Chat history display ───────────────────────────────────────────────
    if st.session_state.chat_history:
        st.markdown("**💬 Conversation:**")
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.chat_history:
                role = msg["role"]
                text = msg["parts"][0] if isinstance(msg["parts"], list) else msg["parts"]
                if role == "user":
                    st.markdown(f'<div class="chat-label-user">You 👤</div><div class="chat-bubble-user">{text}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="chat-label-ai">🤖 StudyFlow AI</div><div class="chat-bubble-ai">{text}</div>', unsafe_allow_html=True)

        st.markdown("<br>")
        if st.button("🗑️ Clear Chat", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    else:
        st.markdown("""
        <div style="text-align:center;padding:40px 20px;color:#9C8E75">
          <div style="font-size:2.5rem;margin-bottom:12px">💬</div>
          <div style="font-size:0.9rem">Ask me anything about your studies!<br>Use the quick questions above or type below.</div>
        </div>""", unsafe_allow_html=True)

    # ── Chat input ─────────────────────────────────────────────────────────
    st.markdown("---")
    user_input = st.chat_input("Ask your AI study assistant...", key="ai_chat_input")
    if user_input and user_input.strip():
        st.session_state.chat_history.append(
            {"role":"user","parts":[user_input.strip()]}
        )
        with st.spinner("🤖 Thinking..."):
            reply = chat_with_ai(
                user_input.strip(),
                st.session_state.chat_history[:-1],
                student_ctx,
            )
        st.session_state.chat_history.append(
            {"role":"model","parts":[reply]}
        )
        st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  TAB 7 — MANAGE
# ══════════════════════════════════════════════════════════════════════════════
with tab7:
    st.markdown('<div style="font-family:\'Lora\',serif;font-size:1.5rem;font-weight:700;color:#2C2416">⚙️ Manage Study Data</div>', unsafe_allow_html=True)
    mt1,mt2,mt3,mt4,mt5 = st.tabs(["📗 Subjects","📚 Topics","⚠️ Weak Areas","🎯 Goals","📋 All Data"])

    # ── SUBJECTS ──────────────────────────────────────────────────────────────
    with mt1:
        sc1,sc2=st.columns(2)
        with sc1:
            st.markdown("#### ➕ Add Subject")
            ns=st.text_input("Subject Name",placeholder="e.g. Mathematics",key="new_subj")
            if st.button("➕ Add Subject"):
                n=ns.strip()
                if not n: st.error("Enter a name.")
                elif n in kg.subjects: st.warning(f"'{n}' already exists.")
                else:
                    kg.add_subject(n); kg.student_studies_subject(username,n); kg.save()
                    st.success(f"✅ '{n}' added!"); st.rerun()
        with sc2:
            st.markdown("#### 🗑️ Delete Subject")
            sl=list(kg.subjects.keys())
            if sl:
                ds=st.selectbox("Select",sl,key="del_subj"); tc=len(kg.get_subject_topics(ds))
                st.markdown(f'<div style="font-size:0.82rem;color:#DC2626;margin:6px 0">⚠️ Will also delete {tc} topic(s).</div>', unsafe_allow_html=True)
                cf=st.checkbox(f"Confirm delete '{ds}'",key="cf_ds")
                if st.button("🗑️ Delete",key="del_s"):
                    if cf: kg.remove_subject(ds); kg.save(); st.success(f"✅ Deleted."); st.rerun()
                    else:  st.warning("Tick confirm first.")
            else: st.info("No subjects yet.")
        if kg.subjects:
            st.markdown("#### 📋 Your Subjects")
            for sub in kg.subjects:
                cnt=len(kg.get_subject_topics(sub))
                st.markdown(f'<div style="background:#EDE9FE;border-left:4px solid #4F46E5;padding:10px 16px;border-radius:0 8px 8px 0;margin:4px 0"><span style="font-weight:700;color:#2C2416">📗 {sub}</span><span style="float:right;color:#4F46E5;font-size:0.82rem;font-weight:600">{cnt} topic(s)</span></div>', unsafe_allow_html=True)

    # ── TOPICS ────────────────────────────────────────────────────────────────
    with mt2:
        if not has_subjects: st.info("💡 Add a subject first.")
        else:
            tc1,tc2=st.columns(2)
            with tc1:
                st.markdown("#### ➕ Add Topic")
                tn=st.text_input("Topic Name",key="nt_name")
                ts=st.selectbox("Subject",list(kg.subjects.keys()),key="nt_subj")
                td=st.select_slider("Difficulty",["Easy","Medium","Hard"],key="nt_diff")
                tsl=st.radio("Time Slot",["Morning","Evening"],horizontal=True,key="nt_slot")
                th_=st.number_input("Est. Hours",0.5,8.0,1.5,0.5,key="nt_hrs")
                tr=st.multiselect("Resources",["YouTube","Textbook","Khan Academy","GeeksforGeeks","LeetCode","Online Course","Research Papers","freeCodeCamp","Documentation","Coursera","Udemy"],key="nt_res")
                if st.button("➕ Add Topic"):
                    n=tn.strip()
                    if not n: st.error("Enter topic name.")
                    elif n in kg.topics: st.warning("Already exists.")
                    else:
                        kg.add_topic(n,td,tsl,tr,th_,ts); kg.subject_has_topic(ts,n); kg.save()
                        st.success(f"✅ '{n}' added to {ts}!"); st.rerun()
            with tc2:
                st.markdown("#### 📝 Topic Notes")
                atn=list(kg.topics.keys())
                if atn:
                    nt=st.selectbox("Topic",atn,key="note_sel"); en=kg.get_topic_note(nt)
                    ntx=st.text_area("Notes",value=en,height=120,key="note_tx")
                    if st.button("💾 Save Note"):
                        kg.save_topic_note(nt,ntx); kg.save(); st.success("✅ Saved!")
                st.markdown("#### 🗑️ Delete Topic")
                if atn:
                    dt=st.selectbox("Topic to delete",atn,key="del_t")
                    if st.button("🗑️ Delete Topic"):
                        kg.remove_topic(dt); kg.save(); st.success(f"✅ '{dt}' removed."); st.rerun()

    # ── WEAK AREAS ────────────────────────────────────────────────────────────
    with mt3:
        if not has_subjects: st.info("💡 Add subjects and topics first.")
        else:
            cw=kg.get_weak_areas(username); wc1,wc2=st.columns(2)
            with wc1:
                st.markdown("#### ⚠️ Mark Weak Area")
                um=[t for t in kg.topics if t not in cw]
                if um:
                    nwk=st.selectbox("Topic",um,key="wk_sel")
                    if st.button("⚠️ Mark Weak"):
                        kg.mark_weak_area(username,nwk); kg.save(); st.success(f"'{nwk}' marked!"); st.rerun()
                else: st.info("All topics are marked as weak.")
            with wc2:
                st.markdown("#### ✅ Remove Weak Flag")
                if cw:
                    rw=st.selectbox("Remove",cw,key="rm_wk")
                    if st.button("✅ Remove Flag"):
                        kg.unmark_weak_area(username,rw); kg.save(); st.success(f"'{rw}' removed!"); st.rerun()
            if cw:
                st.markdown("**Current Weak Areas:**"); all_t=kg.get_all_topics_for_student(username)
                for w in cw:
                    td=next((t for t in all_t if t["name"]==w),{}); clr=DIFFICULTY_COLOR.get(td.get("difficulty","Easy"),"#888")
                    st.markdown(f'<div style="border-left:3px solid {clr};padding:6px 12px;margin:4px 0;font-size:0.88rem;color:#2C2416;background:#FFF7ED;border-radius:0 8px 8px 0">{w} <span style="color:{clr};font-size:0.75rem;font-weight:600">{td.get("difficulty","")}</span></div>', unsafe_allow_html=True)

    # ── GOALS ─────────────────────────────────────────────────────────────────
    with mt4:
        st.markdown("#### 🎯 Set Study Goal")
        eg=kg.get_goal(username); gc1,gc2=st.columns(2)
        with gc1:
            ge=st.text_input("Exam / Goal Name",value=eg["exam_name"] if eg else "",key="goal_exam")
            gh=st.slider("Weekly Hours Target",5,60,int(eg["weekly_hours"]) if eg else 15,key="goal_hrs")
        with gc2:
            gd_=st.date_input("Target Date",key="goal_date")
            if st.button("🎯 Set Goal"):
                kg.set_goal(username,gh,str(gd_),ge); kg.save()
                st.success(f"✅ Goal set: {ge} by {gd_} ({gh}h/week)"); st.rerun()
        if eg:
            st.markdown(f'<div class="goal-card"><div style="font-size:0.72rem;color:#5B21B6;text-transform:uppercase;letter-spacing:0.08em;margin-bottom:10px">Current Goal</div><div style="font-family:\'Lora\',serif;font-size:1.3rem;font-weight:700;color:#2C2416">{eg["exam_name"]}</div><div style="color:#6B5E45;font-size:0.85rem;margin-top:6px">📅 <strong>{eg["target_date"]}</strong> &nbsp;·&nbsp; ⏱ <strong>{eg["weekly_hours"]}h/week</strong></div></div>', unsafe_allow_html=True)

    # ── ALL DATA ──────────────────────────────────────────────────────────────
    with mt5:
        st.markdown("#### 📋 All Topics")
        rows=[]
        for sub in kg.subjects:
            for t in kg.get_subject_topics(sub):
                rows.append({"Subject":sub,"Topic":t["name"],"Difficulty":DIFFICULTY_ICON.get(t.get("difficulty","Easy"),"")+t.get("difficulty","Easy"),"Slot":t.get("time_slot",""),"Hours":t.get("estimated_hours",1),"Resources":", ".join(t.get("resources",[]))})
        if rows:
            df=pd.DataFrame(rows); st.dataframe(df,use_container_width=True,hide_index=True)
            st.download_button("📥 Export CSV",df.to_csv(index=False),file_name=f"topics_{username}.csv",mime="text/csv")
        else: st.info("No topics yet.")
