import unittest
import os
import sys
import tempfile
import sqlite3
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.oracle import OracleRouter
from config.settings import settings

class MockOllamaClient:
    def __init__(self, running_models: list):
        self.models = running_models

    def list_local_models(self) -> list:
        return self.models

class TestOracleRouter(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        settings.DB_PATH = Path(self.db_path)
        
        self.mock_client = MockOllamaClient(["qwen2.5-coder:7b", "llama3:latest"])
        self.oracle = OracleRouter(Path(self.db_path), self.mock_client)

    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_coding_task_routing(self):
        """
        Confirms CODING tasks are mapped to the high-performance qwen-coder.
        """
        selected_model = self.oracle.route_task("CODING", "Write a python server")
        self.assertEqual(selected_model, "qwen2.5-coder:7b")

    def test_routing_fallback_reversion(self):
        """
        Confirms ORACLE falls back gracefully if the targeted model is not currently installed.
        """
        # VISION requires llava:latest, which is not in our mock running list.
        # It should fall back to first active model: qwen2.5-coder:7b
        selected_model = self.oracle.route_task("VISION", "Analyze this image")
        self.assertEqual(selected_model, "qwen2.5-coder:7b")

    def test_metrics_logging(self):
        """
        Confirms model processing performance records are written correctly.
        """
        self.oracle.log_metrics("llama3:latest", "CHAT", 22.5)
        
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            row = conn.execute("SELECT * FROM model_performance_logs").fetchone()
            
        self.assertIsNotNone(row)
        self.assertEqual(row["model_name"], "llama3:latest")
        self.assertEqual(row["tokens_per_sec"], 22.5)

if __name__ == "__main__":
    unittest.main()
