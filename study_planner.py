"""
Smart Study Planner — Scheduling Engine (v3)
Priority-based scheduling with completion tracking and goal awareness.
"""

from __future__ import annotations
from typing import List, Dict, TYPE_CHECKING
from datetime import datetime, timedelta

if TYPE_CHECKING:
    from knowledge_graph import StudyKnowledgeGraph

DIFFICULTY_PRIORITY: Dict[str, int] = {"Hard": 1, "Medium": 2, "Easy": 3}
DIFFICULTY_COLOR:    Dict[str, str] = {
    "Hard":   "#E74C3C",
    "Medium": "#F39C12",
    "Easy":   "#27AE60",
}
DIFFICULTY_ICON: Dict[str, str] = {
    "Hard":   "🔴",
    "Medium": "🟡",
    "Easy":   "🟢",
}
DIFFICULTY_BG: Dict[str, str] = {
    "Hard":   "rgba(231,76,60,0.1)",
    "Medium": "rgba(243,156,18,0.1)",
    "Easy":   "rgba(39,174,96,0.1)",
}


class StudyPlanner:
    def __init__(self, kg: "StudyKnowledgeGraph"):
        self.kg = kg

    # ------------------------------------------------------------------ #
    #  PRIORITY SCORING                                                    #
    # ------------------------------------------------------------------ #

    def _score(
        self, topic: Dict, weak_areas: List[str], completed: List[str]
    ) -> float:
        base   = DIFFICULTY_PRIORITY.get(topic.get("difficulty", "Easy"), 3)
        weak_b = -0.5 if topic.get("name") in weak_areas else 0
        done_b =  5.0 if topic.get("name") in completed  else 0
        return base + weak_b + done_b

    def _sorted_topics(self, student_name: str):
        all_topics = self.kg.get_all_topics_for_student(student_name)
        weak_areas = self.kg.get_weak_areas(student_name)
        completed  = self.kg.get_completed_topics(student_name)
        ranked = sorted(
            all_topics,
            key=lambda t: self._score(t, weak_areas, completed),
        )
        return ranked, weak_areas, completed

    # ------------------------------------------------------------------ #
    #  TODAY'S PLAN                                                        #
    # ------------------------------------------------------------------ #

    def get_today_plan(self, student_name: str) -> Dict:
        ranked, weak_areas, completed = self._sorted_topics(student_name)
        info    = self.kg.get_student_info(student_name)
        avail_h = info.get("available_hours", 4)

        pending = [t for t in ranked if t["name"] not in completed]
        morning = [t for t in pending if t.get("time_slot") == "Morning"][:3]
        evening = [t for t in pending if t.get("time_slot") == "Evening"][:3]

        total_h = sum(t.get("estimated_hours", 1) for t in morning + evening)

        tips = []
        hard_t = [x for x in morning + evening if x.get("difficulty") == "Hard"]
        if hard_t:
            tips.append(
                f"🔴 Start with **{hard_t[0]['name']}** — brain is sharpest in the morning!"
            )
        if weak_areas:
            tips.append(
                f"⚠️ Spend extra 20 min reviewing: **{', '.join(weak_areas[:2])}**"
            )
        tips.append(
            f"⏱️ {total_h:.1f} hrs planned. Take 10-min breaks every 45 mins."
        )
        if total_h > avail_h:
            tips.append(
                f"⚡ Today's plan ({total_h:.1f}h) exceeds your daily limit ({avail_h}h). Consider reducing!"
            )

        return {
            "date":        datetime.now().strftime("%A, %d %B %Y"),
            "morning":     morning,
            "evening":     evening,
            "weak_areas":  weak_areas,
            "completed":   completed,
            "total_hours": total_h,
            "avail_hours": avail_h,
            "tips":        tips,
        }

    # ------------------------------------------------------------------ #
    #  7-DAY PLAN                                                          #
    # ------------------------------------------------------------------ #

    def generate_weekly_plan(self, student_name: str) -> List[Dict]:
        ranked, weak_areas, completed = self._sorted_topics(student_name)
        pending = [t for t in ranked if t["name"] not in completed]
        n = max(len(pending), 1)

        weekly = []
        for day_offset in range(7):
            date_obj = datetime.now() + timedelta(days=day_offset)
            start = (day_offset * 3) % n
            pool  = pending[start:] + pending[:start]

            morning = [t for t in pool if t.get("time_slot") == "Morning"][:2]
            evening = [t for t in pool if t.get("time_slot") == "Evening"][:2]

            if not morning and pool:
                morning = pool[:1]
            if not evening and len(pool) > 1:
                evening = pool[1:2]

            total_h = sum(t.get("estimated_hours", 1) for t in morning + evening)

            weekly.append(
                {
                    "day":         date_obj.strftime("%A"),
                    "date":        date_obj.strftime("%d %b"),
                    "morning":     morning,
                    "evening":     evening,
                    "weak_areas":  weak_areas,
                    "completed":   completed,
                    "total_hours": total_h,
                }
            )

        return weekly

    # ------------------------------------------------------------------ #
    #  STATS & PROGRESS                                                    #
    # ------------------------------------------------------------------ #

    def get_progress_stats(self, student_name: str) -> Dict:
        all_topics = self.kg.get_all_topics_for_student(student_name)
        weak_areas = self.kg.get_weak_areas(student_name)
        completed  = self.kg.get_completed_topics(student_name)
        subjects   = self.kg.get_student_subjects(student_name)

        diff_counts   = {"Hard": 0, "Medium": 0, "Easy": 0}
        total_hours   = 0.0
        pending_hours = 0.0

        for t in all_topics:
            diff = t.get("difficulty", "Easy")
            diff_counts[diff] = diff_counts.get(diff, 0) + 1
            h = t.get("estimated_hours", 1)
            total_hours += h
            if t["name"] not in completed:
                pending_hours += h

        completion_pct = (
            len(completed) / len(all_topics) * 100 if all_topics else 0
        )

        return {
            "total_topics":            len(all_topics),
            "completed_count":         len(completed),
            "pending_count":           len(all_topics) - len(completed),
            "completion_pct":          round(completion_pct, 1),
            "weak_areas_count":        len(weak_areas),
            "weak_areas":              weak_areas,
            "difficulty_distribution": diff_counts,
            "total_study_hours":       total_hours,
            "pending_hours":           pending_hours,
            "logged_hours":            self.kg.get_total_logged_hours(student_name),
            "subjects_count":          len(subjects),
            "subjects":                subjects,
        }

    # ------------------------------------------------------------------ #
    #  CYPHER REFERENCE QUERIES                                            #
    # ------------------------------------------------------------------ #

    def neo4j_study_plan_query(self, student_name: str) -> str:
        return (
            f'// Get prioritised study plan for "{student_name}"\n'
            f'MATCH (s:Student {{name: "{student_name}"}})\n'
            f'      -[:STUDIES]->(sub:Subject)\n'
            f'      -[:HAS]->(t:Topic)\n'
            f'OPTIONAL MATCH (s)-[:WEAK_IN]->(t)\n'
            f'OPTIONAL MATCH (s)-[:COMPLETED]->(t)\n'
            f'WITH t,\n'
            f'     CASE t.difficulty WHEN "Hard" THEN 1\n'
            f'                       WHEN "Medium" THEN 2\n'
            f'                       ELSE 3 END AS diffScore,\n'
            f'     (s)-[:WEAK_IN]->(t)   AS isWeak,\n'
            f'     (s)-[:COMPLETED]->(t) AS isDone\n'
            f'RETURN t.name, t.difficulty, t.time_slot, isWeak, isDone\n'
            f'ORDER BY isDone, diffScore, isWeak DESC;'
        )

    def neo4j_weak_areas_query(self, student_name: str) -> str:
        return (
            f'// Weak topics for "{student_name}"\n'
            f'MATCH (s:Student {{name: "{student_name}"}})\n'
            f'      -[:WEAK_IN]->(t:Topic)\n'
            f'RETURN t.name AS weak_topic, t.difficulty;'
        )

    def neo4j_progress_query(self, student_name: str) -> str:
        return (
            f'// Completion progress for "{student_name}"\n'
            f'MATCH (s:Student {{name: "{student_name}"}})\n'
            f'      -[:STUDIES]->(sub:Subject)\n'
            f'      -[:HAS]->(t:Topic)\n'
            f'OPTIONAL MATCH (s)-[:COMPLETED]->(t)\n'
            f'RETURN sub.name AS subject,\n'
            f'       count(t) AS total,\n'
            f'       count((s)-[:COMPLETED]->(t)) AS done;'
        )
