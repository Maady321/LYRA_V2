import uuid
import numpy as np
from typing import List, Dict, Any, Tuple
from core.ollama_client import OllamaClient
from memory.sqlite_db import SQLiteDB
from MJ_AI_Assistant.security.guardian import guardian_kernel

class SQLiteVectorStore:
    def __init__(self, db: SQLiteDB, client: OllamaClient):
        self.db = db
        self.client = client

    async def add_memory(self, fact: str) -> None:
        """
        Embeds a fact using Ollama and stores it inside the SQLite database.
        """
        embedding = await self.client.generate_embedding(fact)
        if not embedding:
            # Fallback to a zero-vector if embedding endpoint fails
            embedding = [0.0] * 768
            
        memory_id = str(uuid.uuid4())
        self.db.add_raw_memory(memory_id, fact, embedding)

    async def search_similar_memories(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Retrieves top_k similar factual memories using Hybrid Vector + FTS5 Search and Reciprocal Rank Fusion (RRF).
        """
        import re
        import sqlite3

        # 1. Vector Search
        query_vector = await self.client.generate_embedding(query)
        if not query_vector:
            q_vec = None
        else:
            q_vec = np.array(query_vector)
            q_norm = np.linalg.norm(q_vec)
            if q_norm == 0:
                q_vec = None

        all_memories = self.db.get_all_raw_memories()
        if not all_memories:
            return []

        # Calculate cosine similarity and score
        vector_results = []
        if q_vec is not None:
            for memory in all_memories:
                m_vec = np.array(memory["vector"])
                m_norm = np.linalg.norm(m_vec)
                if m_norm == 0:
                    continue
                score = float(np.dot(q_vec, m_vec) / (q_norm * m_norm))
                vector_results.append((memory["memory_id"], memory["fact"], score))
            # Sort descending by vector score
            vector_results.sort(key=lambda x: x[2], reverse=True)

        # 2. FTS5 Keyword Search
        fts_results = []
        # Clean query: extract alphanumeric words and construct an OR query with prefix wildcard
        clean_words = [re.sub(r'[^a-zA-Z0-9]', '', w) for w in query.split()]
        clean_query = " OR ".join([f"{w}*" for w in clean_words if w])
        
        if clean_query:
            try:
                guardian_kernel.authorize_execution(agent_name="vector_store", action="db_access", target="sqlite3")
                with sqlite3.connect(self.db.db_path) as conn:
                    conn.row_factory = sqlite3.Row
                    cursor = conn.execute(
                        "SELECT memory_id, fact FROM memories_fts WHERE memories_fts MATCH ?",
                        (clean_query,)
                    )
                    rows = cursor.fetchall()
                    fts_results = [(row["memory_id"], row["fact"]) for row in rows]
            except Exception:
                # Fallback or pass if FTS syntax error
                pass

        # 3. Reciprocal Rank Fusion (RRF)
        # Create mapping of memory_id to fact
        id_to_fact = {m["memory_id"]: m["fact"] for m in all_memories}

        # Dict of ranks: rank is 0-indexed position
        vector_ranks = {item[0]: rank for rank, item in enumerate(vector_results)}
        fts_ranks = {item[0]: rank for rank, item in enumerate(fts_results)}

        # Fusion score constant
        k = 60.0
        rrf_scores = {}
        for m_id in id_to_fact:
            score = 0.0
            if m_id in vector_ranks:
                score += 1.0 / (k + vector_ranks[m_id])
            if m_id in fts_ranks:
                score += 1.0 / (k + fts_ranks[m_id])
            
            if score > 0.0:
                rrf_scores[m_id] = score

        # Sort combined results descending
        sorted_ids = sorted(rrf_scores.keys(), key=lambda x: rrf_scores[x], reverse=True)
        
        # Format as list of tuples (fact, fused_score)
        result = [(id_to_fact[m_id], rrf_scores[m_id]) for m_id in sorted_ids]
        return result[:top_k]
