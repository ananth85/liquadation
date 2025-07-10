import asyncio
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import uuid

class AgentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class AgentTask:
    task_id: str
    task_type: str
    input_data: Dict[str, Any]
    status: AgentStatus
    result: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: Optional[str] = None
    completed_at: Optional[str] = None

class BaseAgent(ABC):
    """Base class for all MCP agents in the liquidation document generation system"""
    
    def __init__(self, agent_name: str, logger: Optional[logging.Logger] = None):
        self.agent_name = agent_name
        self.agent_id = str(uuid.uuid4())
        self.status = AgentStatus.IDLE
        self.logger = logger or logging.getLogger(f"Agent.{agent_name}")
        self.task_queue: List[AgentTask] = []
        self.completed_tasks: List[AgentTask] = []
        
        # In-memory storage for this agent (per user rules - no external cache)
        self.memory: Dict[str, Any] = {}
        
    @abstractmethod
    async def process_task(self, task: AgentTask) -> Dict[str, Any]:
        """Process a single task - must be implemented by each agent"""
        pass
    
    @abstractmethod
    def get_capabilities(self) -> List[str]:
        """Return list of capabilities this agent provides"""
        pass
    
    async def add_task(self, task_type: str, input_data: Dict[str, Any]) -> str:
        """Add a new task to the agent's queue"""
        task_id = str(uuid.uuid4())
        task = AgentTask(
            task_id=task_id,
            task_type=task_type,
            input_data=input_data,
            status=AgentStatus.IDLE
        )
        self.task_queue.append(task)
        self.logger.info(f"Task {task_id} added to {self.agent_name}")
        return task_id
    
    async def execute_next_task(self) -> Optional[AgentTask]:
        """Execute the next task in queue"""
        if not self.task_queue:
            return None
            
        task = self.task_queue.pop(0)
        task.status = AgentStatus.RUNNING
        self.status = AgentStatus.RUNNING
        
        try:
            self.logger.info(f"Executing task {task.task_id} of type {task.task_type}")
            result = await self.process_task(task)
            task.result = result
            task.status = AgentStatus.COMPLETED
            self.status = AgentStatus.IDLE
            
        except Exception as e:
            task.error_message = str(e)
            task.status = AgentStatus.ERROR
            self.status = AgentStatus.ERROR
            self.logger.error(f"Task {task.task_id} failed: {e}")
            
        self.completed_tasks.append(task)
        return task
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status and metrics"""
        return {
            "agent_name": self.agent_name,
            "agent_id": self.agent_id,
            "status": self.status.value,
            "queued_tasks": len(self.task_queue),
            "completed_tasks": len(self.completed_tasks),
            "capabilities": self.get_capabilities()
        }
    
    def store_data(self, key: str, data: Any) -> None:
        """Store data in agent's in-memory storage"""
        self.memory[key] = data
        
    def retrieve_data(self, key: str) -> Any:
        """Retrieve data from agent's in-memory storage"""
        return self.memory.get(key)
    
    def clear_memory(self) -> None:
        """Clear agent's memory (security cleanup)"""
        self.memory.clear()
        self.logger.info(f"Memory cleared for agent {self.agent_name}") 