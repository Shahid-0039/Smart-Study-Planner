"""
StudyFlow v4 — AI Assistant
Gemini API se powered personal study assistant.
Student ka apna data context mein diya jata hai.
"""

import google.generativeai as genai
from typing import List, Dict, Optional


# ─────────────────────────────────────────────────────────────────────────────
#  SETUP
# ─────────────────────────────────────────────────────────────────────────────
def _get_api_key() -> str:
    try:
        import streamlit as st
        return st.secrets.get("GEMINI_API_KEY", "")
    except Exception:
        return ""


def init_gemini(api_key: str = ""):
    key = api_key or _get_api_key()
    genai.configure(api_key=key)


def get_model():
    return genai.GenerativeModel(
        model_name="gemini-1.5-flash-latest",
        generation_config={
            "temperature":       0.7,
            "top_p":             0.9,
            "max_output_tokens": 1024,
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
#  STUDENT CONTEXT BUILDER
# ─────────────────────────────────────────────────────────────────────────────
def build_student_context(
    display_name:  str,
    username:      str,
    subjects:      List[str],
    all_topics:    List[Dict],
    weak_areas:    List[str],
    completed:     List[str],
    sessions:      List[Dict],
    goal:          Optional[Dict],
    hours_per_day: int,
    university:    str = "",
    department:    str = "",
    semester:      str = "",
) -> str:
    subjects_info = ""
    for sub in subjects:
        sub_topics = [t for t in all_topics if t.get("subject") == sub]
        if sub_topics:
            topics_list = []
            for t in sub_topics:
                status = "✓ Completed" if t["name"] in completed else ("⚠ Weak" if t["name"] in weak_areas else "Pending")
                topics_list.append(
                    f"  - {t['name']} ({t.get('difficulty','Easy')}, "
                    f"{t.get('estimated_hours',1)}h, {t.get('time_slot','Morning')}) [{status}]"
                )
            subjects_info += f"\n📗 {sub}:\n" + "\n".join(topics_list)

    total_logged  = sum(s.get("hours", 0) for s in sessions)
    session_count = len(sessions)
    recent_topics = list({s["topic"] for s in sessions[-5:]}) if sessions else []

    goal_info = "No goal set yet."
    if goal:
        goal_info = (
            f"Exam: {goal.get('exam_name','')}, "
            f"Target Date: {goal.get('target_date','')}, "
            f"Weekly Hours: {goal.get('weekly_hours',0)}h"
        )

    total_topics    = len(all_topics)
    completed_count = len(completed)
    weak_count      = len(weak_areas)
    pending_count   = total_topics - completed_count
    completion_pct  = round(completed_count / total_topics * 100, 1) if total_topics else 0

    context = f"""
You are StudyFlow AI — a personal academic study assistant for the following student.
Always be helpful, encouraging, and personalized. Use the student's actual data in your answers.
Respond in the same language the student uses (Urdu or English or mix).
Keep answers clear, practical, and motivating. Use emojis where appropriate.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STUDENT PROFILE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Name         : {display_name}
Username     : @{username}
University   : {university or 'Not specified'}
Department   : {department or 'Not specified'}
Semester     : {semester or 'Not specified'}
Study Hours  : {hours_per_day} hours/day

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STUDY OVERVIEW
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Subjects     : {len(subjects)} → {', '.join(subjects) if subjects else 'None added yet'}
Total Topics : {total_topics}
Completed    : {completed_count} ({completion_pct}%)
Pending      : {pending_count}
Weak Areas   : {weak_count} → {', '.join(weak_areas) if weak_areas else 'None'}
Goal         : {goal_info}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SUBJECTS & TOPICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{subjects_info if subjects_info else 'No topics added yet.'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SESSION HISTORY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Total Sessions    : {session_count}
Total Hours Logged: {total_logged:.1f}h
Recently Studied  : {', '.join(recent_topics) if recent_topics else 'No sessions yet'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YOUR ROLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Help {display_name} understand their topics
- Give study tips for weak areas: {', '.join(weak_areas) if weak_areas else 'none'}
- Suggest what to study next based on their schedule
- Motivate them based on their progress ({completion_pct}% done)
- Answer academic questions related to their subjects
- Help them plan their study time ({hours_per_day}h/day)
- If they ask in Urdu, reply in Urdu. If English, reply in English.
""".strip()

    return context


# ─────────────────────────────────────────────────────────────────────────────
#  CHAT FUNCTION
# ─────────────────────────────────────────────────────────────────────────────
def chat_with_ai(
    user_message:    str,
    chat_history:    List[Dict],
    student_context: str,
    api_key:         str = "",
) -> str:
    try:
        init_gemini(api_key)
        model = get_model()

        history_with_context = [
            {"role": "user",  "parts": [student_context]},
            {"role": "model", "parts": [
                "Understood! I'm StudyFlow AI, ready to help this student "
                "with their personalized study plan and academic questions."
            ]},
        ] + chat_history

        chat     = model.start_chat(history=history_with_context)
        response = chat.send_message(user_message)
        return response.text

    except Exception as e:
        err = str(e)
        if "API_KEY" in err.upper() or "api key" in err.lower():
            return "❌ **Invalid API Key.** Please check your Gemini API key in the AI Assistant settings."
        elif "quota" in err.lower() or "429" in err:
            return "⚠️ **Rate limit reached.** Please wait a moment and try again."
        elif "network" in err.lower() or "connection" in err.lower():
            return "🌐 **Connection error.** Please check your internet connection."
        else:
            return f"❌ **Error:** {err}"


# ─────────────────────────────────────────────────────────────────────────────
#  QUICK SUGGESTION PROMPTS
# ─────────────────────────────────────────────────────────────────────────────
def get_quick_prompts(
    weak_areas: List[str],
    subjects:   List[str],
    pending:    List[str],
) -> List[str]:
    prompts = []

    if weak_areas:
        prompts.append(f"📖 Explain {weak_areas[0]} in simple words")
        if len(weak_areas) > 1:
            prompts.append(f"📝 Give me practice tips for {weak_areas[1]}")

    if subjects:
        prompts.append(f"📅 Make a study plan for {subjects[0]}")

    if pending:
        prompts.append(f"🚀 How should I start studying {pending[0]}?")

    prompts += [
        "💪 Motivate me to study today",
        "⏰ How can I manage my study time better?",
        "🧠 What is the best technique to memorize topics?",
        "📊 Analyze my progress and give me feedback",
    ]

    return prompts[:6]


# ─────────────────────────────────────────────────────────────────────────────
#  API KEY VALIDATOR
# ─────────────────────────────────────────────────────────────────────────────
def validate_api_key(api_key: str = "") -> tuple[bool, str]:
    try:
        init_gemini(api_key)
        model    = get_model()
        response = model.generate_content("Say OK")
        if response.text:
            return True, "✅ API key is valid!"
        return False, "❌ No response from Gemini."
    except Exception as e:
        err = str(e)
        if "API_KEY" in err.upper() or "invalid" in err.lower():
            return False, "❌ Invalid API key. Please check and try again."
        return False, f"❌ Error: {err}"
