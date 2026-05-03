"""
StudyFlow v4 — AI Assistant
Gemini API se powered personal study assistant.
Student ka apna data context mein diya jata hai.
"""

import google.generativeai as genai
from typing import List, Dict, Optional
import streamlit as st

# ─────────────────────────────────────────────────────────────────────────────
#  API KEY — Streamlit Secrets se lo
# ─────────────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")


# ─────────────────────────────────────────────────────────────────────────────
#  SETUP
# ─────────────────────────────────────────────────────────────────────────────
def init_gemini(api_key: str = GEMINI_API_KEY):
    """Gemini API ko initialize karo."""
    genai.configure(api_key=api_key)


def get_model():
    """Gemini 1.5 Flash model return karo."""
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
    # Topics by subject
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

    # Sessions summary
    total_logged  = sum(s.get("hours", 0) for s in sessions)
    session_count = len(sessions)
    recent_topics = list({s["topic"] for s in sessions[-5:]}) if sessions else []

    # Goal info
    goal_info = "No goal set yet."
    if goal:
        goal_info = (
            f"Exam: {goal.get('exam_name','')}, "
            f"Target Date: {goal.get('target_date','')}, "
            f"Weekly Hours: {goal.get('weekly_hours',0)}h"
        )

    # Stats
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
Goal         : {goal_inf
