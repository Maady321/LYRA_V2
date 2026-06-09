import sqlite3
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
from config.settings import settings
from MJ_AI_Assistant.security.guardian import guardian_kernel

class UserModelTwin:
    def __init__(self, db_path: Path = settings.DB_PATH):
        self.db_path = db_path
        self._initialize_default_profile()

    def _initialize_default_profile(self):
        """
        Seeds baseline preference attributes inside the profile.
        """
        guardian_kernel.authorize_execution(agent_name="twin_engine", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db_path) as conn:
            profile_defaults = [
                ("preferred_name", "Friend", 1.0),
                ("learning_mode", "EXPLORATIVE", 0.5),
                ("habit_morning_active", "false", 0.3)
            ]
            for key, val, conf in profile_defaults:
                conn.execute(
                    "INSERT OR IGNORE INTO user_profile (key, value, confidence) VALUES (?, ?, ?)",
                    (key, val, conf)
                )
            conn.commit()

    def analyze_query_for_twin(self, prompt: str) -> None:
        """
        Scans queries for technology keywords, projects, and learning behaviors,
        updating the user digital twin state.
        """
        # Dictionary of skill mapping keywords
        skills_keywords = {
            "python": "Python Development",
            "javascript": "JavaScript Development",
            "typescript": "TypeScript Development",
            "react": "React.js Framework",
            "docker": "Docker Containerization",
            "sqlite": "SQLite Database Management",
            "fastapi": "FastAPI Web Architecture",
            "machine learning": "Machine Learning",
            "devops": "DevOps Engineering"
        }
        
        normalized_prompt = prompt.lower()
        detected_skills = []
        for kw, skill_name in skills_keywords.items():
            if kw in normalized_prompt:
                detected_skills.append(skill_name)
                
        # Update user skills
        if detected_skills:
            guardian_kernel.authorize_execution(agent_name="twin_engine", action="db_access", target="sqlite3")
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                for skill in detected_skills:
                    row = conn.execute("SELECT * FROM user_skills WHERE skill_name = ?", (skill,)).fetchone()
                    if row:
                        freq = row["frequency_used"] + 1
                        # Logarithmic growth in confidence score up to 1.0
                        new_conf = min(1.0, row["confidence_score"] + 0.05)
                        
                        # Dynamically advance skill level based on frequency
                        level = "NOVICE"
                        if freq > 15:
                            level = "EXPERT"
                        elif freq > 5:
                            level = "INTERMEDIATE"
                            
                        conn.execute(
                            """UPDATE user_skills 
                               SET frequency_used = ?, confidence_score = ?, skill_level = ?, last_detected = CURRENT_TIMESTAMP 
                               WHERE skill_name = ?""",
                            (freq, new_conf, level, skill)
                        )
                    else:
                        conn.execute(
                            """INSERT INTO user_skills (skill_name, skill_level, confidence_score, frequency_used) 
                               VALUES (?, ?, ?, ?)""",
                            (skill, "NOVICE", 0.40, 1)
                        )
                conn.commit()

    def add_project(self, name: str, description: str = "", tech_stack: List[str] = None) -> str:
        """
        Registers an active ongoing project directly within the user model digital twin.
        """
        project_id = f"project_{int(datetime.utcnow().timestamp())}"
        tech_str = ",".join(tech_stack) if tech_stack else ""
        
        guardian_kernel.authorize_execution(agent_name="twin_engine", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """INSERT INTO user_projects (project_id, name, description, associated_tech) 
                   VALUES (?, ?, ?, ?)""",
                (project_id, name, description, tech_str)
            )
            conn.commit()
        return project_id

    def serialize_digital_twin(self) -> Dict[str, Any]:
        """
        Compiles the entire profile state, observed skills, and project list for visual rendering.
        """
        guardian_kernel.authorize_execution(agent_name="twin_engine", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            skills = [dict(r) for r in conn.execute("SELECT * FROM user_skills ORDER BY confidence_score DESC").fetchall()]
            projects = [dict(r) for r in conn.execute("SELECT * FROM user_projects WHERE status = 'ACTIVE'").fetchall()]
            profile = [dict(r) for r in conn.execute("SELECT * FROM user_profile").fetchall()]
            
        return {
            "status": "success",
            "profile": {p["key"]: {"value": p["value"], "confidence": p["confidence"]} for p in profile},
            "skills": skills,
            "projects": projects
        }
