import logging
from typing import List, Dict, Any, Optional
from neo4j import AsyncGraphDatabase, AsyncDriver

logger = logging.getLogger("Neo4jEngine")

class Neo4jEngine:
    def __init__(self, uri: str = "bolt://localhost:7687", user: str = "neo4j", password: str = "lyra_neo4j_password"):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[AsyncDriver] = None

    async def connect(self):
        try:
            self.driver = AsyncGraphDatabase.driver(self.uri, auth=(self.user, self.password))
            # Verify connectivity
            await self.driver.verify_connectivity()
            logger.info(f"Connected to Neo4j Graph Database at {self.uri}")
            await self._init_schema()
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")

    async def close(self):
        if self.driver:
            await self.driver.close()
            logger.info("Closed Neo4j connection.")

    async def _init_schema(self):
        """Create constraints and indexes for enterprise graph performance."""
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (pr:Project) REQUIRE pr.name IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (m:Memory) REQUIRE m.id IS UNIQUE",
        ]
        try:
            async with self.driver.session() as session:
                for q in queries:
                    await session.run(q)
            logger.info("Neo4j schema constraints initialized.")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j schema: {e}")

    async def execute_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a generic Cypher query and return results."""
        if parameters is None:
            parameters = {}
            
        async def work(tx):
            result = await tx.run(query, parameters)
            records = await result.data()
            return records

        try:
            async with self.driver.session() as session:
                return await session.execute_read(work)
        except Exception as e:
            logger.error(f"Cypher query execution failed: {e}")
            return []

    async def execute_write(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Execute a mutating Cypher query."""
        if parameters is None:
            parameters = {}
            
        async def work(tx):
            result = await tx.run(query, parameters)
            records = await result.data()
            return records

        try:
            async with self.driver.session() as session:
                return await session.execute_write(work)
        except Exception as e:
            logger.error(f"Cypher write execution failed: {e}")
            return []

    # --- Active Reasoning Methods ---
    async def find_shortest_path(self, start_label: str, start_prop: str, start_val: str, 
                                 end_label: str, end_prop: str, end_val: str) -> List[Dict[str, Any]]:
        """Graph reasoning: find shortest contextual path between two entities."""
        query = f"""
        MATCH (start:{start_label} {{{start_prop}: $start_val}}), (end:{end_label} {{{end_prop}: $end_val}})
        MATCH p = shortestPath((start)-[*]-(end))
        RETURN p
        """
        return await self.execute_query(query, {"start_val": start_val, "end_val": end_val})

    async def infer_missing_links(self) -> List[Dict[str, Any]]:
        """Graph reasoning: Suggest new links based on collaborative filtering / common neighbors."""
        query = """
        MATCH (p1:Person)-[:KNOWS]->(p2:Person)-[:KNOWS]->(p3:Person)
        WHERE NOT (p1)-[:KNOWS]-(p3) AND p1 <> p3
        RETURN p1.id AS Person1, p3.id AS SuggestedConnection, count(*) AS Strength
        ORDER BY Strength DESC
        """
        return await self.execute_query(query)
