import unittest
import os
import sys
import tempfile
import sqlite3
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from user_model.twin_engine import UserModelTwin
from config.settings import settings

class TestUserModelTwin(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        settings.DB_PATH = Path(self.db_path)
        
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema_sql)
            conn.commit()
            
        self.twin = UserModelTwin(Path(self.db_path))

    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_skill_detection(self):
        """
        Confirms skill keywords are correctly scanned, leveled, and tracked in the SQLite store.
        """
        # Trigger first observation
        self.twin.analyze_query_for_twin("I am writing python scripts for react apps")
        
        state = self.twin.serialize_digital_twin()
        skills = state["skills"]
        
        # Verify detected skills
        skill_names = [s["skill_name"] for s in skills]
        self.assertIn("Python Development", skill_names)
        self.assertIn("React.js Framework", skill_names)
        
        python_skill = next(s for s in skills if s["skill_name"] == "Python Development")
        self.assertEqual(python_skill["frequency_used"], 1)
        self.assertEqual(python_skill["skill_level"], "NOVICE")

    def test_incremental_skill_leveling(self):
        """
        Confirms repeated skill observations dynamically level up the digital twin profile.
        """
        # Simulate multiple python observations
        for _ in range(6):
            self.twin.analyze_query_for_twin("Need help with python code")
            
        state = self.twin.serialize_digital_twin()
        python_skill = next(s for s in state["skills"] if s["skill_name"] == "Python Development")
        
        self.assertEqual(python_skill["frequency_used"], 6)
        self.assertEqual(python_skill["skill_level"], "INTERMEDIATE")
        self.assertTrue(python_skill["confidence_score"] > 0.40)

    def test_project_registration(self):
        """
        Confirms active projects are cataloged accurately under user_projects.
        """
        proj_id = self.twin.add_project("AIOS Core Upgrade", "Building a next-gen security layer", ["python", "sqlite"])
        self.assertTrue(proj_id.startswith("project_"))
        
        state = self.twin.serialize_digital_twin()
        projects = state["projects"]
        
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]["name"], "AIOS Core Upgrade")
        self.assertEqual(projects[0]["associated_tech"], "python,sqlite")

if __name__ == "__main__":
    unittest.main()
