"""
Velo AI Agents
Registry of all 51 specialized agents
"""

from .base_agent import agent_registry, BaseAgent, AgentMetadata, AgentDivision

# Import all agent modules to auto-register them
from .engineering import *
from .design import *
from .testing import *

# Additional agents will be imported as they're implemented

def get_all_agents():
    """Get all registered agents"""
    return agent_registry.get_all()

def get_agent(agent_id: str):
    """Get agent by ID"""
    return agent_registry.get(agent_id)

def get_agents_by_division(division: AgentDivision):
    """Get all agents in a division"""
    return agent_registry.get_by_division(division)

__all__ = [
    'agent_registry',
    'get_all_agents',
    'get_agent',
    'get_agents_by_division',
    'BaseAgent',
    'AgentMetadata',
    'AgentDivision'
]
