import sqlite3
import uuid
import json
from typing import List, Dict, Any, Tuple, Optional
from memory.sqlite_db import SQLiteDB

class KnowledgeGraphEngine:
    def __init__(self, db: SQLiteDB):
        self.db = db

    def add_entity(self, name: str, entity_type: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        """
        Registers an entity inside the graph database.
        """
        entity_id = str(uuid.uuid4())
        metadata_str = json.dumps(metadata) if metadata else None
        
        with sqlite3.connect(self.db.db_path) as conn:
            try:
                conn.execute(
                    "INSERT INTO graph_entities (entity_id, name, type, metadata) VALUES (?, ?, ?, ?)",
                    (entity_id, name, entity_type, metadata_str)
                )
                conn.commit()
                return entity_id
            except sqlite3.IntegrityError:
                # Entity already exists, retrieve existing id
                cursor = conn.execute("SELECT entity_id FROM graph_entities WHERE name = ?", (name,))
                row = cursor.fetchone()
                return row[0] if row else ""

    def add_relationship(self, source_name: str, predicate: str, target_name: str, weight: float = 1.0) -> None:
        """
        Creates an entity relationship triple (Subject -> Predicate -> Object) inside SQLite.
        """
        # Ensure subject and object entities exist
        source_id = self.add_entity(source_name, "concept")
        target_id = self.add_entity(target_name, "concept")
        
        relationship_id = str(uuid.uuid4())
        with sqlite3.connect(self.db.db_path) as conn:
            try:
                conn.execute(
                    """INSERT OR REPLACE INTO graph_relationships 
                       (relationship_id, source_id, predicate, target_id, weight) 
                       VALUES (?, ?, ?, ?, ?)""",
                    (relationship_id, source_id, predicate.lower().strip(), target_id, weight)
                )
                conn.commit()
            except Exception as e:
                print(f"[GraphEngine] Failed to map relationship: {e}")

    def traverse_multi_hop(self, start_name: str, max_hops: int = 2) -> List[Dict[str, Any]]:
        """
        Recursively crawls relationships up to max_hops using recursive Common Table Expressions (CTE).
        """
        query = """
        WITH RECURSIVE GraphPath(source_id, target_id, predicate, depth, path) AS (
            SELECT source_id, target_id, predicate, 1, source_id || '->' || target_id
            FROM graph_relationships
            WHERE source_id = (SELECT entity_id FROM graph_entities WHERE name = ?)
            
            UNION ALL
            
            SELECT r.source_id, r.target_id, r.predicate, gp.depth + 1, gp.path || '->' || r.target_id
            FROM graph_relationships r
            JOIN GraphPath gp ON r.source_id = gp.target_id
            WHERE gp.depth < ? AND gp.path NOT LIKE '%' || r.target_id || '%'
        )
        SELECT gp.source_id, e_s.name as source_name, gp.predicate, gp.target_id, e_t.name as target_name, gp.depth
        FROM GraphPath gp
        JOIN graph_entities e_s ON gp.source_id = e_s.entity_id
        JOIN graph_entities e_t ON gp.target_id = e_t.entity_id;
        """
        
        paths = []
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            try:
                cursor = conn.execute(query, (start_name, max_hops))
                rows = cursor.fetchall()
                paths = [dict(r) for r in rows]
            except Exception as e:
                print(f"[GraphEngine] Traversal error: {e}")
        return paths

    def query_semantic_context(self, user_query: str) -> str:
        """
        Looks up keywords inside query, crawls multi-hop links, and summarizes context.
        """
        found_contexts = []
        # Basic token keyword extractor
        keywords = [word.strip('?,.!"\'') for word in user_query.split() if len(word) >= 2]
        
        with sqlite3.connect(self.db.db_path) as conn:
            conn.row_factory = sqlite3.Row
            for kw in keywords:
                # Find matching entities OR relationships with matching predicate
                cursor = conn.execute(
                    """SELECT DISTINCT e.name FROM graph_entities e
                       LEFT JOIN graph_relationships r ON e.entity_id = r.source_id OR e.entity_id = r.target_id
                       WHERE e.name LIKE ? OR r.predicate LIKE ?""",
                    (f"%{kw}%", f"%{kw}%")
                )
                entities = cursor.fetchall()
                for entity in entities:
                    paths = self.traverse_multi_hop(entity["name"], max_hops=2)
                    for p in paths:
                        found_contexts.append(f"- {p['source_name']} {p['predicate']} {p['target_name']}")
                        
        # Deduplicate
        unique_contexts = list(set(found_contexts))
        return "\n".join(unique_contexts) if unique_contexts else "No semantic graph links found."
