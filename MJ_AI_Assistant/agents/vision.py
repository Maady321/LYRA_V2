from agents.base import BaseAgent
from core.bus import Task
from memory.vector_store import SQLiteVectorStore

class VisionAgent(BaseAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.vector_store = SQLiteVectorStore(self.db, self.client)

    async def handle_task(self, task: Task) -> str:
        """
        Manages semantic context retrieval, user preferences, and short-term dialogue sequences.
        """
        action = task.payload.get("action", "retrieve")
        
        if action == "store":
            fact = task.payload.get("fact", "")
            if fact:
                await self.emit_log(f"Archiving factual long-term memory: '{fact}'")
                self.vector_store.add_memory(fact)
                return "Memory successfully stored."
            return "No fact provided."

        # Default action: Retrieve memory context
        query = task.payload.get("query", "")
        conversation_id = task.payload.get("conversation_id", "default")
        await self.emit_log(f"Retrieving dialogue history and similar memories for: '{query}'")

        # 1. Fetch SQLite conversation logs
        chat_rows = self.db.get_conversation_history(conversation_id)
        short_term_str = ""
        if chat_rows:
            short_term_str = "\n".join([f"{r['sender']}: {r['content']}" for r in chat_rows[-6:]])

        # 2. Query Vector similarity memories
        similar_mems = self.vector_store.search_similar_memories(query, top_k=3)
        long_term_str = ""
        if similar_mems:
            long_term_str = "\n".join([f"- {fact} (confidence: {score:.2f})" for fact, score in similar_mems])

        # 3. Retrieve default user preferences
        user_pref = self.db.get_preference("name", "Friend")

        context = (
            f"User Profile / Preferences: Default User Name is {user_pref}\n\n"
            f"Factual Long-term Memories:\n{long_term_str if long_term_str else 'None stored yet.'}\n\n"
            f"Recent Conversations:\n{short_term_str if short_term_str else 'This is a brand new session.'}"
        )
        return context
