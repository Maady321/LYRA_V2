import unittest
import os
import sys
import tempfile
import sqlite3
import asyncio
from pathlib import Path

# Setup paths to import core and memory modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.settings import settings
from memory.sqlite_db import SQLiteDB
from memory.vector_store import SQLiteVectorStore
from core.bus import MessageBus, Task
from core.negotiation import PeerNegotiationBroker

class MockOllamaClient:
    def generate_embedding(self, text: str) -> list:
        # Returns a simple deterministic embedding
        vec = [0.0] * 768
        for i, char in enumerate(text[:768]):
            vec[i] = float(ord(char)) / 256.0
        return vec

class TestNegotiationAndFTS(unittest.TestCase):
    def setUp(self):
        # Create temp db
        self.db_fd, self.db_path = tempfile.mkstemp()
        settings.DB_PATH = Path(self.db_path)
        
        # Build schema
        schema_path = Path(__file__).parent.parent / "database" / "schema.sql"
        with open(schema_path, "r", encoding="utf-8") as f:
            schema_sql = f.read()
            
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema_sql)
            conn.commit()
            
        self.db = SQLiteDB(Path(self.db_path))
        self.client = MockOllamaClient()
        self.vector_store = SQLiteVectorStore(self.db, self.client)
        self.bus = MessageBus(self.db)
        
        # Seed default roles and capabilities in the database
        with sqlite3.connect(self.db_path) as conn:
            # Clear them if any
            conn.execute("DELETE FROM agent_capabilities")
            conn.execute("DELETE FROM agent_roles")
            
            # Insert test roles
            roles = [
                ("FURY", 4, "Coordinator"),
                ("BANNER", 2, "Researcher"),
                ("STARK", 3, "Executor"),
                ("GHOST", 4, "Controller")
            ]
            for name, level, desc in roles:
                conn.execute(
                    "INSERT INTO agent_roles (agent_name, trust_level, role_description) VALUES (?, ?, ?)",
                    (name, level, desc)
                )
            
            # Insert test capabilities
            capabilities = [
                ("cap_stark_exec", "STARK", "CMD_EXEC", None),
                ("cap_ghost_exec", "GHOST", "CMD_EXEC", None),
                ("cap_banner_read", "BANNER", "FILE_READ", None)
            ]
            for cap_id, agent, cap_type, pattern in capabilities:
                conn.execute(
                    "INSERT INTO agent_capabilities (capability_id, agent_name, capability_type, constraint_pattern) VALUES (?, ?, ?, ?)",
                    (cap_id, agent, cap_type, pattern)
                )
            conn.commit()

        self.loop = asyncio.get_event_loop()

    def tearDown(self):
        os.close(self.db_fd)
        try:
            os.unlink(self.db_path)
        except Exception:
            pass

    def test_fts5_trigger_sync(self):
        """
        Verify that adding a memory automatically creates a row in the memories_fts FTS5 table,
        and deleting it deletes the corresponding row.
        """
        # 1. Add memory
        self.vector_store.add_memory("Sabari works on artificial intelligence projects.")
        
        # Query memories_fts directly to check sync
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute("SELECT * FROM memories_fts").fetchall()
            self.assertEqual(len(rows), 1)
            self.assertIn("Sabari", rows[0]["fact"])
            memory_id = rows[0]["memory_id"]
            
        # 2. Delete memory
        self.db.delete_memory(memory_id)
        
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute("SELECT * FROM memories_fts").fetchall()
            self.assertEqual(len(rows), 0)

    def test_hybrid_search_rrf(self):
        """
        Verify that search_similar_memories queries both vector search and FTS5 search,
        combining their scores correctly using Reciprocal Rank Fusion.
        """
        # Seed memories
        self.vector_store.add_memory("Python is an interpreted programming language.")
        self.vector_store.add_memory("Rust is a systems programming language focusing on safety.")
        self.vector_store.add_memory("Deep learning models are trained using gradient descent.")
        
        # Search for "programming language"
        results = self.vector_store.search_similar_memories("programming language", top_k=2)
        
        # The first two seeded memories contain "programming" or "language" or both, so they should rank higher
        self.assertEqual(len(results), 2)
        facts = [res[0] for res in results]
        self.assertTrue(any("programming language" in f or "systems programming" in f for f in facts))

    def test_peer_negotiation_broker(self):
        """
        Verify that task negotiation selects the correct assignee based on bidding and trust level.
        """
        async def run_negotiation_test():
            # 1. Set agent statuses
            self.bus.active_agents["STARK"] = "ONLINE" # trust level 3
            self.bus.active_agents["GHOST"] = "BUSY"   # trust level 4 * 0.5 = 2.0 score
            self.bus.active_agents["BANNER"] = "ONLINE" # trust level 2
            
            # Negotiate CMD_EXEC: STARK (3 * 1.0 = 3.0) should beat GHOST (4 * 0.5 = 2.0)
            best_agent = await self.bus.negotiator.negotiate_best_agent(
                task_id="test_task_1",
                subtask_title="Execute safe shell validation script",
                required_capability="CMD_EXEC"
            )
            self.assertEqual(best_agent, "STARK")
            
            # Make GHOST ONLINE: GHOST (4 * 1.0 = 4.0) should beat STARK (3 * 1.0 = 3.0)
            self.bus.active_agents["GHOST"] = "ONLINE"
            best_agent_2 = await self.bus.negotiator.negotiate_best_agent(
                task_id="test_task_2",
                subtask_title="Execute desktop folder setup",
                required_capability="CMD_EXEC"
            )
            self.assertEqual(best_agent_2, "GHOST")

        self.loop.run_until_complete(run_negotiation_test())

if __name__ == "__main__":
    unittest.main()
