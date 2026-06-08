import math
import numpy as np
from typing import List, Dict, Any, Tuple
from memory.vector_store import SQLiteVectorStore

class HybridRAGEngine:
    def __init__(self, vector_store: SQLiteVectorStore):
        self.vector_store = vector_store

    def _compute_tf_idf_score(self, chunk: str, query: str) -> float:
        """
        Lightweight, pure-python BM25 term frequency analyzer.
        """
        words = chunk.lower().split()
        q_words = query.lower().split()
        if not words or not q_words:
            return 0.0

        score = 0.0
        for qw in q_words:
            tf = words.count(qw) / len(words)
            # Safe basic term relevance amplification
            if tf > 0:
                score += tf * math.log(1.5 / tf)
        return score

    def retrieve_hybrid_context(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Performs hybrid re-ranking: merges vector semantic scores and TF-IDF lexical matches.
        """
        # 1. Fetch vector similarity matches
        vector_results = self.vector_store.search_similar_memories(query, top_k=10)
        
        # 2. Re-rank utilizing term frequency lexical logic
        re_ranked = []
        for chunk, v_score in vector_results:
            lexical_score = self._compute_tf_idf_score(chunk, query)
            # Combine normalized weights: 70% dense vector + 30% lexical search
            combined_score = (0.7 * v_score) + (0.3 * min(lexical_score, 1.0))
            re_ranked.append((chunk, combined_score))

        # Sort descending
        re_ranked.sort(key=lambda x: x[1], reverse=True)
        return re_ranked[:top_k]
