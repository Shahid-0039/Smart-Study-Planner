"""
StudyFlow v4 — Knowledge Graph
• NetworkX in-memory graph
• JSON-based persistence (organized, human-readable)
• Per-user single-student model
"""

import json
import os
import networkx as nx
from typing import List, Dict, Optional
from datetime import datetime

DATA_DIR = "studyflow_data"
KG_DIR   = os.path.join(DATA_DIR, "kg")


def _kp(username: str) -> str:
    """Return the JSON file path for a user's knowledge graph."""
    os.makedirs(KG_DIR, exist_ok=True)
    return os.path.join(KG_DIR, f"{username}_kg.json")


class StudyKnowledgeGraph:
    """
    One instance = one logged-in student.
    Graph nodes : Student | Subject | Topic
    Graph edges : STUDIES | HAS | WEAK_IN | COMPLETED
    """

    def __init__(self, username: str, hours_per_day: int = 4):
        self.graph    = nx.MultiDiGraph()
        self.students: Dict[str, str] = {}
        self.subjects: Dict[str, str] = {}
        self.topics:   Dict[str, str] = {}
        self.sessions: List[Dict]     = []
        self.goals:    Dict           = {}
        self.username  = username
        self._add_student(username, hours_per_day)

    # ─────────────────────────────────────────────────────────────────────────
    #  PRIVATE
    # ─────────────────────────────────────────────────────────────────────────
    def _add_student(self, name: str, hrs: int):
        nid = f"student_{name}"
        self.graph.add_node(
            nid, type="Student", name=name,
            available_hours=hrs,
            joined=datetime.now().strftime("%Y-%m-%d"),
        )
        self.students[name] = nid

    def _completed_with_dates(self) -> List[Dict]:
        if self.username not in self.students:
            return []
        out = []
        for _, t, d in self.graph.out_edges(self.students[self.username], data=True):
            if d.get("relation") == "COMPLETED":
                out.append({
                    "name": self.graph.nodes[t]["name"],
                    "date": d.get("date", datetime.now().strftime("%Y-%m-%d")),
                })
        return out

    def _mark_completed_on(self, sn: str, tn: str, date: str):
        if sn in self.students and tn in self.topics:
            already = any(
                d.get("relation") == "COMPLETED" and v == self.topics[tn]
                for _, v, d in self.graph.out_edges(self.students[sn], data=True)
            )
            if not already:
                self.graph.add_edge(
                    self.students[sn], self.topics[tn],
                    relation="COMPLETED", date=date,
                )

    # ─────────────────────────────────────────────────────────────────────────
    #  SAVE  (JSON — organized & human-readable)
    # ─────────────────────────────────────────────────────────────────────────
    def save(self):
        topics_data = {}
        for name, nid in self.topics.items():
            nd = self.graph.nodes.get(nid, {})
            topics_data[name] = {
                "difficulty":      nd.get("difficulty",      "Easy"),
                "time_slot":       nd.get("time_slot",       "Morning"),
                "resources":       nd.get("resources",       []),
                "estimated_hours": nd.get("estimated_hours", 1.0),
                "subject":         nd.get("subject",         ""),
                "notes":           nd.get("notes",           ""),
            }

        data = {
            "meta": {
                "version":    "4",
                "username":   self.username,
                "saved_at":   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            },
            "subjects":          list(self.subjects.keys()),
            "student_subjects":  self.get_student_subjects(self.username),
            "topics":            topics_data,
            "weak_areas":        self.get_weak_areas(self.username),
            "completed":         self._completed_with_dates(),
            "sessions":          self.sessions,
            "goals":             self.goals,
        }

        with open(_kp(self.username), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    # ─────────────────────────────────────────────────────────────────────────
    #  LOAD
    # ─────────────────────────────────────────────────────────────────────────
    @classmethod
    def load(cls, username: str, hours_per_day: int = 4) -> "StudyKnowledgeGraph":
        path = _kp(username)
        if not os.path.exists(path):
            return cls(username, hours_per_day)

        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        kg = cls(username, hours_per_day)

        # subjects
        for s in data.get("subjects", []):
            kg.add_subject(s)

        # topics
        for tn, td in data.get("topics", {}).items():
            kg.add_topic(
                tn,
                td.get("difficulty",      "Easy"),
                td.get("time_slot",       "Morning"),
                td.get("resources",       []),
                td.get("estimated_hours", 1.0),
                td.get("subject",         ""),
            )
            if td.get("notes"):
                kg.save_topic_note(tn, td["notes"])

        # student → subject edges
        for s in data.get("student_subjects", []):
            kg.student_studies_subject(username, s)

        # subject → topic edges
        for tn, td in data.get("topics", {}).items():
            if td.get("subject"):
                kg.subject_has_topic(td["subject"], tn)

        # weak areas
        for tn in data.get("weak_areas", []):
            if tn in kg.topics:
                kg.mark_weak_area(username, tn)

        # completed
        for item in data.get("completed", []):
            tn = item["name"] if isinstance(item, dict) else item
            dt = (item.get("date", datetime.now().strftime("%Y-%m-%d"))
                  if isinstance(item, dict)
                  else datetime.now().strftime("%Y-%m-%d"))
            if tn in kg.topics:
                kg._mark_completed_on(username, tn, dt)

        kg.sessions = data.get("sessions", [])
        kg.goals    = data.get("goals",    {})
        return kg

    # ─────────────────────────────────────────────────────────────────────────
    #  NODES — ADD / REMOVE
    # ─────────────────────────────────────────────────────────────────────────
    def add_student(self, name: str, hours: int = 4) -> str:
        if name not in self.students:
            self._add_student(name, hours)
        return self.students[name]

    def add_subject(self, name: str) -> str:
        nid = f"subject_{name}"
        self.graph.add_node(nid, type="Subject", name=name)
        self.subjects[name] = nid
        return nid

    def remove_subject(self, name: str):
        if name not in self.subjects:
            return
        for t in [td["name"] for td in self.get_subject_topics(name)]:
            self.remove_topic(t)
        self.graph.remove_node(self.subjects[name])
        del self.subjects[name]

    def add_topic(
        self,
        name: str,
        difficulty: str,
        time_slot: str,
        resources: List[str],
        estimated_hours: float = 1.0,
        subject: str = "",
    ) -> str:
        nid = f"topic_{name}"
        self.graph.add_node(
            nid, type="Topic", name=name,
            difficulty=difficulty, time_slot=time_slot,
            resources=resources, estimated_hours=estimated_hours,
            subject=subject, notes="",
        )
        self.topics[name] = nid
        return nid

    def remove_topic(self, name: str):
        if name not in self.topics:
            return
        self.graph.remove_node(self.topics[name])
        del self.topics[name]

    def update_available_hours(self, student_name: str, hours: int):
        if student_name in self.students:
            self.graph.nodes[self.students[student_name]]["available_hours"] = hours

    # ─────────────────────────────────────────────────────────────────────────
    #  EDGES
    # ─────────────────────────────────────────────────────────────────────────
    def student_studies_subject(self, sn: str, sub: str):
        if sn in self.students and sub in self.subjects:
            self.graph.add_edge(
                self.students[sn], self.subjects[sub], relation="STUDIES"
            )

    def subject_has_topic(self, sub: str, tn: str):
        if sub in self.subjects and tn in self.topics:
            self.graph.add_edge(
                self.subjects[sub], self.topics[tn], relation="HAS"
            )

    def mark_weak_area(self, sn: str, tn: str):
        if sn in self.students and tn in self.topics:
            already = any(
                d.get("relation") == "WEAK_IN" and v == self.topics[tn]
                for _, v, d in self.graph.out_edges(self.students[sn], data=True)
            )
            if not already:
                self.graph.add_edge(
                    self.students[sn], self.topics[tn], relation="WEAK_IN"
                )

    def unmark_weak_area(self, sn: str, tn: str):
        if sn in self.students and tn in self.topics:
            to_rm = [
                (u, v, k)
                for u, v, k, d in self.graph.edges(
                    self.students[sn], data=True, keys=True
                )
                if d.get("relation") == "WEAK_IN" and v == self.topics.get(tn)
            ]
            for u, v, k in to_rm:
                self.graph.remove_edge(u, v, k)

    def mark_completed(self, sn: str, tn: str):
        self._mark_completed_on(sn, tn, datetime.now().strftime("%Y-%m-%d"))

    def unmark_completed(self, sn: str, tn: str):
        if sn in self.students and tn in self.topics:
            to_rm = [
                (u, v, k)
                for u, v, k, d in self.graph.edges(
                    self.students[sn], data=True, keys=True
                )
                if d.get("relation") == "COMPLETED" and v == self.topics.get(tn)
            ]
            for u, v, k in to_rm:
                self.graph.remove_edge(u, v, k)

    # ─────────────────────────────────────────────────────────────────────────
    #  NOTES
    # ─────────────────────────────────────────────────────────────────────────
    def save_topic_note(self, tn: str, note: str):
        if tn in self.topics:
            self.graph.nodes[self.topics[tn]]["notes"] = note

    def get_topic_note(self, tn: str) -> str:
        if tn in self.topics:
            return self.graph.nodes[self.topics[tn]].get("notes", "")
        return ""

    # ─────────────────────────────────────────────────────────────────────────
    #  SESSIONS
    # ─────────────────────────────────────────────────────────────────────────
    def log_session(self, sn: str, tn: str, hours: float, mood: str = "😊"):
        self.sessions.append({
            "student":   sn,
            "topic":     tn,
            "hours":     hours,
            "mood":      mood,
            "date":      datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().strftime("%H:%M"),
        })

    def get_sessions_for_student(self, sn: str) -> List[Dict]:
        return [s for s in self.sessions if s["student"] == sn]

    def get_total_logged_hours(self, sn: str) -> float:
        return sum(s["hours"] for s in self.get_sessions_for_student(sn))

    # ─────────────────────────────────────────────────────────────────────────
    #  GOALS
    # ─────────────────────────────────────────────────────────────────────────
    def set_goal(self, sn: str, weekly_hours: float, target_date: str, exam_name: str = ""):
        self.goals = {
            "weekly_hours": weekly_hours,
            "target_date":  target_date,
            "exam_name":    exam_name,
            "set_on":       datetime.now().strftime("%Y-%m-%d"),
        }

    def get_goal(self, sn: str) -> Optional[Dict]:
        return self.goals if self.goals else None

    # ─────────────────────────────────────────────────────────────────────────
    #  QUERIES
    # ─────────────────────────────────────────────────────────────────────────
    def get_student_list(self) -> List[str]:
        return list(self.students.keys())

    def get_student_info(self, sn: str) -> Dict:
        if sn not in self.students:
            return {}
        return dict(self.graph.nodes[self.students[sn]])

    def get_student_subjects(self, sn: str) -> List[str]:
        if sn not in self.students:
            return []
        return [
            self.graph.nodes[t]["name"]
            for _, t, d in self.graph.out_edges(self.students[sn], data=True)
            if d.get("relation") == "STUDIES"
            and self.graph.nodes[t].get("type") == "Subject"
        ]

    def get_subject_topics(self, sub: str) -> List[Dict]:
        if sub not in self.subjects:
            return []
        return [
            dict(self.graph.nodes[t])
            for _, t, d in self.graph.out_edges(self.subjects[sub], data=True)
            if d.get("relation") == "HAS"
        ]

    def get_weak_areas(self, sn: str) -> List[str]:
        if sn not in self.students:
            return []
        return [
            self.graph.nodes[t]["name"]
            for _, t, d in self.graph.out_edges(self.students[sn], data=True)
            if d.get("relation") == "WEAK_IN"
        ]

    def get_completed_topics(self, sn: str) -> List[str]:
        if sn not in self.students:
            return []
        return [
            self.graph.nodes[t]["name"]
            for _, t, d in self.graph.out_edges(self.students[sn], data=True)
            if d.get("relation") == "COMPLETED"
        ]

    def get_all_topics_for_student(self, sn: str) -> List[Dict]:
        out = []
        for sub in self.get_student_subjects(sn):
            for t in self.get_subject_topics(sub):
                td = dict(t)
                td["subject"] = sub
                out.append(td)
        return out

    # ─────────────────────────────────────────────────────────────────────────
    #  GRAPH STATS & VISUALIZATION
    # ─────────────────────────────────────────────────────────────────────────
    def get_graph_stats(self) -> Dict:
        return {
            "nodes":    self.graph.number_of_nodes(),
            "edges":    self.graph.number_of_edges(),
            "subjects": len(self.subjects),
            "topics":   len(self.topics),
        }

    def get_graph_for_visualization(self, student_name: Optional[str] = None) -> Dict:
        if student_name:
            relevant: set = set()
            sn = self.students.get(student_name)
            if sn:
                relevant.add(sn)
                for sub in self.get_student_subjects(student_name):
                    sn2 = self.subjects.get(sub)
                    if sn2:
                        relevant.add(sn2)
                        for top in self.get_subject_topics(sub):
                            tn = self.topics.get(top["name"])
                            if tn:
                                relevant.add(tn)
            subg = self.graph.subgraph(relevant)
        else:
            subg = self.graph

        if subg.number_of_nodes() == 0:
            return {"nodes": [], "edges": []}

        pos  = nx.spring_layout(subg, k=2.5, iterations=60, seed=42)
        comp = set(self.get_completed_topics(student_name)) if student_name else set()
        weak = set(self.get_weak_areas(student_name))       if student_name else set()

        nodes_data = []
        for node, d in subg.nodes(data=True):
            x, y = pos[node]
            name = d.get("name", node)
            nodes_data.append({
                "id":         node,
                "x":          float(x),
                "y":          float(y),
                "type":       d.get("type",       ""),
                "name":       name,
                "difficulty": d.get("difficulty", ""),
                "completed":  name in comp,
                "weak":       name in weak,
            })

        edges_data = []
        for src, tgt, d in subg.edges(data=True):
            if src in pos and tgt in pos:
                edges_data.append({
                    "relation": d.get("relation", ""),
                    "x0": float(pos[src][0]),
                    "y0": float(pos[src][1]),
                    "x1": float(pos[tgt][0]),
                    "y1": float(pos[tgt][1]),
                })

        return {"nodes": nodes_data, "edges": edges_data}