import asyncio
import logging
from typing import Dict, List, Any, Set
from core.redis_broker import Task, RedisMessageBus

logger = logging.getLogger("DAGExecutor")

class DAGNode:
    def __init__(self, task: Task, dependencies: List[str] = None):
        self.task = task
        self.dependencies = set(dependencies) if dependencies else set()
        self.completed = False
        self.result = None

class TaskDAG:
    def __init__(self):
        self.nodes: Dict[str, DAGNode] = {}

    def add_node(self, task: Task, dependencies: List[str] = None):
        self.nodes[task.task_id] = DAGNode(task, dependencies)

    def is_ready(self, task_id: str, completed_tasks: Set[str]) -> bool:
        node = self.nodes[task_id]
        return not node.completed and node.dependencies.issubset(completed_tasks)

class ParallelExecutor:
    """
    Executes a Directed Acyclic Graph (DAG) of tasks by identifying independent 
    subtasks and running them concurrently using asyncio.gather().
    """
    def __init__(self, bus: RedisMessageBus):
        self.bus = bus

    async def execute_dag(self, dag: TaskDAG) -> Dict[str, Any]:
        completed_tasks: Set[str] = set()
        results: Dict[str, Any] = {}
        
        while len(completed_tasks) < len(dag.nodes):
            # Find all tasks that are ready to run right now
            ready_nodes = [
                node for node_id, node in dag.nodes.items() 
                if dag.is_ready(node_id, completed_tasks)
            ]
            
            if not ready_nodes and len(completed_tasks) < len(dag.nodes):
                logger.error("DAG Deadlock detected! Dependencies cannot be resolved.")
                break
            
            logger.info(f"Executing {len(ready_nodes)} parallel tasks: {[n.task.task_id for n in ready_nodes]}")
            
            # Execute all ready tasks concurrently across the Redis Bus
            tasks_to_await = [self.bus.dispatch_task(n.task) for n in ready_nodes]
            batch_results = await asyncio.gather(*tasks_to_await, return_exceptions=True)
            
            # Process results and mark as completed
            for node, result in zip(ready_nodes, batch_results):
                node.completed = True
                node.result = result
                results[node.task.task_id] = result
                completed_tasks.add(node.task.task_id)
                
                if isinstance(result, Exception) or (isinstance(result, str) and result.startswith("Error:")):
                    logger.error(f"Task {node.task.task_id} failed in DAG: {result}")
                    # In a production DAG, we might halt execution of dependent nodes here
                    
        return results
