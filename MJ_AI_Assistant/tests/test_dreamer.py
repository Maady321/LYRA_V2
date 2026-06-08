import unittest
import os
import sys
import tempfile
import sqlite3
from pathlib import Path

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from memory.dreamer import DreamerMemoryConsolidator
from memory.graph_engine import KnowledgeGraphEngine
from config.settings import settings

class TestDreamerConsolidator(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp()
        settings.DB_PATH = Path(self.db_path)
        
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema_sql)
            conn.commit()
            
        self.graph = KnowledgeGraphEngine(settings) # Wait, settings or DB wrapper?
        # Let's inspect KnowledgeGraphEngine init: it expects SQLiteDB wrapper
        from memory.sqlite_db import SQLiteDB
        self.sqlite_db = SQLiteDB(Path(self.db_path))
        self.graph_engine = KnowledgeGraphEngine(self.sqlite_db)
        
        self.dreamer = DreamerMemoryConsolidator(Path(self.db_path), self.graph_engine, None)

    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_consolidation_no_messages(self):
        """
        Confirms DREAMER returns 0 when no message items exist.
        """
        count = self.dreamer.consolidate_recent_memories()
        self.assertEqual(count, 0)

    def test_fallback_triple_extraction(self):
        """
        Confirms rule-based regex fallback extracts triples successfully offline.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (message_id, conversation_id, sender, content) VALUES ('m1', 'c1', 'user', 'Maddy studies BCA')"
            )
            conn.commit()
            
        count = self.dreamer.consolidate_recent_memories()
        self.assertEqual(count, 1)
        
        # Verify graph entity was mapped
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT name FROM graph_entities WHERE name = 'BCA'").fetchone()
            
        self.assertIsNotNone(row)
        self.assertEqual(row[0], "BCA")

if __name__ == "__main__":
    unittest.main()
