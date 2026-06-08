import logging
from typing import List, Dict, Any
from memory.neo4j_engine import Neo4jEngine

logger = logging.getLogger("GraphReasoner")

class KnowledgeGraphReasoner:
    """
    Active reasoning engine over the Neo4j Enterprise Graph.
    Uses Cypher algorithms to infer missing knowledge, expand context, 
    and identify entity relationships.
    """
    def __init__(self, engine: Neo4jEngine):
        self.engine = engine

    async def expand_query_context(self, keywords: List[str]) -> str:
        """
        Takes keywords from a user query and finds directly connected concepts
        and historical projects to expand the LLM's context window.
        """
        if not keywords:
            return ""

        # Cypher: Find any node matching the keywords, and retrieve its immediate neighbors
        query = """
        UNWIND $keywords AS kw
        MATCH (n) WHERE toLower(n.name) CONTAINS toLower(kw) OR toLower(n.id) CONTAINS toLower(kw)
        MATCH (n)-[r]-(neighbor)
        RETURN coalesce(labels(n)[0], 'Node') AS EntityType, coalesce(n.name, n.id, 'Unknown') AS Entity, type(r) AS Relation, 
               coalesce(labels(neighbor)[0], 'Node') AS NeighborType, coalesce(neighbor.name, neighbor.id, 'Unknown') AS Neighbor
        LIMIT 20
        """
        
        try:
            results = await self.engine.execute_query(query, {"keywords": keywords})
            if not results:
                return "No extended graph context found."
            
            context = "Extended Knowledge Graph Context:\n"
            for row in results:
                entity = row.get("Entity", "Unknown")
                relation = row.get("Relation", "RELATED_TO")
                neighbor = row.get("Neighbor", "Unknown")
                context += f"- {entity} [{relation}] {neighbor}\n"
            
            return context
        except Exception as e:
            logger.error(f"Context expansion failed: {e}")
            return ""

    async def detect_knowledge_gaps(self) -> List[str]:
        """
        Identifies orphaned concepts or agents missing specific skills
        to trigger exploratory research goals.
        """
        query = """
        MATCH (a:Agent)
        WHERE NOT (a)-[:HAS_SKILL]->()
        RETURN a.name AS AgentName
        """
        results = await self.engine.execute_query(query)
        gaps = []
        for row in results:
            gaps.append(f"Agent {row['AgentName']} currently has no mapped skills in the graph.")
        return gaps

    async def infer_project_dependencies(self, project_name: str) -> List[str]:
        """
        Finds overlapping skills/agents between projects to suggest
        dependencies or resource sharing.
        """
        query = """
        MATCH (p1:Project {name: $project_name})<-[:WORKS_ON]-(a:Agent)-[:WORKS_ON]->(p2:Project)
        WHERE p1 <> p2
        RETURN DISTINCT coalesce(p2.name, 'Unknown') AS RelatedProject, count(a) AS SharedAgents
        ORDER BY SharedAgents DESC
        """
        results = await self.engine.execute_query(query, {"project_name": project_name})
        return [f"Shares {r['SharedAgents']} agents with project: {r['RelatedProject']}" for r in results]
