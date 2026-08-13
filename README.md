# 📚 Smart Study Planner

An AI-powered study companion built with Streamlit that helps students plan their study time, track progress visually, and get contextual guidance from a built-in AI assistant.

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-web%20app-FF4B4B)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Overview

Smart Study Planner helps students move from "I should study more" to an actual plan. It generates a personalized study timetable, visualizes progress over time, and offers AI-guided suggestions to keep students on track — all through a simple Streamlit interface.

## Features

- ✅ **Personalized timetables** generated based on user input (subjects, available time, goals)
- ✅ **Progress tracking** with visual charts so students can see how they're doing
- ✅ **AI study assistant** that offers contextual guidance, not just a static schedule
- ✅ **User authentication** so each student's plan and progress are saved individually
- ✅ **Knowledge-graph-based structuring** of topics and study materials

## Tech Stack

| Category | Technologies |
|---|---|
| **Language** | Python |
| **Web framework** | Streamlit |
| **AI / Assistant** | LLM-based guidance (`ai_assistant.py`) |
| **Data structuring** | Custom knowledge graph (`knowledge_graph.py`) |
| **Auth** | Custom authentication module (`auth.py`) |

## Repository Structure
Smart-Study-Planner/
├── app.py # Main Streamlit application entry point
├── auth.py # User authentication and session handling
├── ai_assistant.py # AI assistant logic for contextual study guidance
├── knowledge_graph.py # Knowledge-graph structuring of topics/materials
├── study_planner.py # Core timetable generation and planning logic
└── requirements.txt # Python dependencies

## How It Works

1. **Authentication** (`auth.py`) — users log in so their plans and progress persist across sessions.
2. **Planning** (`study_planner.py`) — generates a personalized timetable based on the user's subjects, available time, and goals.
3. **Knowledge structuring** (`knowledge_graph.py`) — organizes topics and materials so the planner and assistant understand relationships between them, not just a flat list.
4. **AI guidance** (`ai_assistant.py`) — provides contextual suggestions and answers as the student studies.
5. **Interface** (`app.py`) — ties everything together in a Streamlit web UI, including progress visualizations.

## Getting Started

### Prerequisites

- Python 3.8+
- `pip`

### Installation

```bash
git clone https://github.com/Shahid-0039/Smart-Study-Planner.git
cd Smart-Study-Planner

python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints in your terminal (typically `http://localhost:8501`).

> If `ai_assistant.py` calls an external LLM API, add a note here about any required API key / environment variable setup so others can run it.

## Roadmap

- [ ] Add screenshots or a short demo GIF showing the timetable and progress views
- [ ] Document any required API keys/environment variables for the AI assistant
- [ ] Add example study data so reviewers can try it without creating an account from scratch
- [ ] Add a `Dockerfile` for one-command setup

## Author

Maintained by **[Shahid-0039](https://github.com/Shahid-0039)**

