"""
Base Agent Class
All 51 specialized agents inherit from this base class
"""

from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class AgentDivision(str, Enum):
    """Agent organization divisions"""
    ENGINEERING = "engineering"
    DESIGN = "design"
    MARKETING = "marketing"
    PRODUCT = "product"
    PROJECT_MANAGEMENT = "project_management"
    TESTING = "testing"
    SUPPORT = "support"
    SPATIAL_COMPUTING = "spatial_computing"
    SPECIALIZED = "specialized"


class AgentStatus(str, Enum):
    """Agent current status"""
    IDLE = "idle"
    ACTIVE = "active"
    WORKING = "working"
    ERROR = "error"


@dataclass
class AgentMetadata:
    """Metadata for each agent"""
    id: str
    name: str
    role: str
    tagline: str
    division: AgentDivision
    capabilities: List[str]
    model: str = "gemini-1.5-pro"  # Default Vertex AI model


class BaseAgent(ABC):
    """
    Base class for all Velo AI Agents

    Each agent has:
    - Unique personality and expertise
    - Specific capabilities
    - Access to Vertex AI (Gemini)
    - Common interface for task execution
    """

    def __init__(self, metadata: AgentMetadata):
        self.metadata = metadata
        self.status = AgentStatus.IDLE
        self.current_task: Optional[str] = None

    @property
    def id(self) -> str:
        return self.metadata.id

    @property
    def name(self) -> str:
        return self.metadata.name

    @property
    def division(self) -> AgentDivision:
        return self.metadata.division

    @abstractmethod
    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a task assigned to this agent

        Args:
            task: Task details including requirements, constraints
            context: Project context, previous artifacts, etc.

        Returns:
            Result dictionary with generated artifacts, status, etc.
        """
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """
        Get the agent's system prompt that defines its personality and expertise
        """
        pass

    def set_status(self, status: AgentStatus):
        """Update agent status"""
        self.status = status

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation"""
        return {
            "id": self.id,
            "name": self.name,
            "role": self.metadata.role,
            "tagline": self.metadata.tagline,
            "division": self.division.value,
            "status": self.status.value,
            "capabilities": self.metadata.capabilities,
            "current_task": self.current_task
        }


class AgentRegistry:
    """
    Central registry for all 51 agents
    Allows dynamic agent lookup and assignment
    """

    def __init__(self):
        self._agents: Dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent):
        """Register an agent"""
        self._agents[agent.id] = agent

    def get(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self._agents.get(agent_id)

    def get_by_division(self, division: AgentDivision) -> List[BaseAgent]:
        """Get all agents in a division"""
        return [
            agent for agent in self._agents.values()
            if agent.division == division
        ]

    def get_all(self) -> List[BaseAgent]:
        """Get all agents"""
        return list(self._agents.values())

    def find_best_agent(self, task_type: str, required_capabilities: List[str]) -> Optional[BaseAgent]:
        """
        Find the best agent for a task based on capabilities

        Args:
            task_type: Type of task (e.g., "frontend", "backend", "design")
            required_capabilities: List of required skills

        Returns:
            Best matching agent or None
        """
        candidates = []

        for agent in self._agents.values():
            if agent.status in [AgentStatus.IDLE, AgentStatus.ACTIVE]:
                # Calculate match score
                matching_capabilities = set(agent.metadata.capabilities) & set(required_capabilities)
                score = len(matching_capabilities)

                if score > 0:
                    candidates.append((agent, score))

        if not candidates:
            return None

        # Return agent with highest score
        candidates.sort(key=lambda x: x[1], reverse=True)
        return candidates[0][0]


# Global agent registry instance
agent_registry = AgentRegistry()
