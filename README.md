# 📖 StudyFlow — Smart Study Planner v3

A beautiful, fully-featured **multi-user** academic study planner powered by a Knowledge Graph (NetworkX).
Every student signs up with their own account — data is private and persistent across sessions.

---

## 🚀 Quick Start (2 commands)

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open: **http://localhost:8501**

---

## 📁 Project Structure

| File | Description |
|------|-------------|
| `app.py` | Full Streamlit UI — Auth gate + 6 tabs, warm academic theme |
| `auth.py` | Signup / Login — SHA-256 hashed passwords, JSON storage |
| `knowledge_graph.py` | NetworkX Knowledge Graph — per-user, pickle-persisted |
| `study_planner.py` | Priority scheduling engine |
| `requirements.txt` | Python dependencies |
| `studyflow_data/` | Auto-created folder: `users.json` + per-user `*.pkl` files |

---

## ✨ What's New in v3

### 🔐 Multi-User Auth
- **Sign Up** with display name, username, password (min 6 chars), hours/day
- **Login** — each student sees only their own data
- **Logout** from the sidebar at any time
- Passwords hashed with SHA-256; stored in `studyflow_data/users.json`

### 💾 Persistent Data
- Each user's Knowledge Graph is saved to `studyflow_data/<username>_kg.pkl`
- Data survives app restarts — no more losing progress on refresh
- Auto-saves after every change (add topic, mark complete, log session, etc.)

### 📗 Subject Management
- Students add their **own subjects** (not shared with others)
- New sub-tab in Manage: **📗 Subjects** — add or delete subjects
- Deleting a subject also removes all its topics

### 🗑️ Topic Deletion
- New option in Manage → Topics to **delete** a topic

### ⚙️ Account Settings
- Change display name and study hours/day from the sidebar

---

## 6 Tabs (same as before)

1. **🏠 Dashboard** — Metric cards, difficulty pie chart, subject bar chart, goal tracker
2. **📅 Today's Plan** — Morning/Evening sessions, smart tips, session logging, mood tracker
3. **🗓️ Weekly Plan** — 7-day grid, detailed downloadable table (CSV export)
4. **✅ Progress** — Completion tracker per subject, session history chart, mark/unmark
5. **🕸️ Knowledge Graph** — Interactive Plotly visualization with Neo4j Cypher queries
6. **⚙️ Manage** — Subjects, Topics, Weak Areas, Goal Setting, All Data export

---

## 🆕 Getting Started (New Account)

1. Open the app → **Sign Up** tab
2. Fill in your name, username, password, daily hours
3. Switch to **Login** tab and log in
4. Go to **⚙️ Manage → 📗 Subjects** — add your subjects (e.g. Mathematics, Physics)
5. Go to **⚙️ Manage → 📚 Topics** — add topics for each subject
6. Go to **⚙️ Manage → 🎯 Goal Setting** — set your exam goal
7. Done! Your dashboard is ready 🎉

---

## 🗄️ Data Storage

```
studyflow_data/
├── users.json          ← All usernames + hashed passwords
├── ali_kg.pkl          ← Ali's complete knowledge graph
├── sara_kg.pkl         ← Sara's complete knowledge graph
└── ahmed_kg.pkl        ← Ahmed's complete knowledge graph
```

Each `.pkl` file is completely private to that user.

---

## 🛠️ Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| Port already in use | Run `streamlit run app.py --server.port 8502` |
| Forgot password | Delete the user entry from `studyflow_data/users.json` (and their `.pkl` file) and re-register |
| Slow graph layout | Reduce `iterations` in `spring_layout` call in `knowledge_graph.py` |

---

## 📝 Notes

- Data is persisted to disk on every action — no data loss on refresh.
- The app is mobile-friendly via Streamlit's responsive layout.
- Sidebar is collapsible via the native `>` arrow on the left edge.
- Tested on Python 3.9+.
