import sqlite3
import json
from pathlib import Path
import re
from datetime import datetime
from typing import List, Dict, Any
from config.settings import settings
from MJ_AI_Assistant.security.guardian import guardian_kernel

class DreamerMemoryConsolidator:
    def __init__(self, db_path: Path = settings.DB_PATH, graph_engine=None, ollama_client=None):
        self.db_path = db_path
        self.graph = graph_engine
        self.client = ollama_client

    def consolidate_recent_memories(self) -> int:
        """
        Extracts recent conversation exchanges, compiles summary insights,
        builds knowledge graph triples, and prunes stale connections.
        """
        # 1. Fetch recent exchanges
        guardian_kernel.authorize_execution(agent_name="dreamer", action="db_access", target="sqlite3")
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT sender, content FROM messages WHERE timestamp >= datetime('now', '-24 hours')"
            ).fetchall()
            
        if not rows:
            print("[DREAMER] No recent dialogue records found to consolidate.")
            return 0
            
        compiled_dialogue = "\n".join([f"{r['sender']}: {r['content']}" for r in rows])
        
        # 2. Extract triples (Subject -> Predicate -> Object) using local LLM
        triples = []
        if self.client and self.client.is_online():
            prompt = (
                "Review the following conversation history and extract core factual triples as a JSON array.\n"
                "Format: [{\"subject\": \"Maddy\", \"predicate\": \"studies\", \"object\": \"BCA\"}]\n\n"
                f"Conversation:\n{compiled_dialogue}"
            )
            try:
                response = self.client.generate_chat_response([{"role": "user", "content": prompt}])
                # Parse json from response
                start_idx = response.find("[")
                end_idx = response.rfind("]") + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response[start_idx:end_idx]
                    triples = json.loads(json_str)
            except Exception as e:
                print(f"[DREAMER] LLM parsing exception: {e}. Falling back to rule-based engine.")
                
        # 3. Deterministic regex-based fallback if LLM is offline or parsing fails
        if not triples:
            triples = self._extract_triples_fallback(compiled_dialogue)
            
        # 4. Integrate into Knowledge Graph
        integrated_count = 0
        if self.graph and triples:
            for t in triples:
                subj = t.get("subject", "").strip()
                pred = t.get("predicate", "").strip()
                obj = t.get("object", "").strip()
                if subj and pred and obj:
                    self.graph.add_relationship(subj, pred, obj)
                    integrated_count += 1
                    
        print(f"[DREAMER] Considation sequence complete. Integrated {integrated_count} new semantic connections.")
        return integrated_count

    def _extract_triples_fallback(self, text: str) -> List[Dict[str, str]]:
        """
        Rule-based backup triple scanner to maintain 100% offline operational status when Ollama is dormant.
        """
        triples = []
        # Basic patterns: "X studies Y", "X is a Y", "X interested in Y"
        study_matches = re.findall(r"(\w+)\s+(studies|learns)\s+(\w+)", text, re.IGNORECASE)
        for sub, pred, obj in study_matches:
            triples.append({"subject": sub.capitalize(), "predicate": pred.lower(), "object": obj.upper()})
            
        interest_matches = re.findall(r"(\w+)\s+(interested in|likes)\s+(\w+)", text, re.IGNORECASE)
        for sub, pred, obj in interest_matches:
            triples.append({"subject": sub.capitalize(), "predicate": "interested_in", "object": obj.capitalize()})
            
        return triples
