"""
Prism Lab - The Innovation Keeper
Experiment Tracker agent
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentMetadata, AgentDivision


class PrismLabAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            id="prism_lab",
            name="Prism Lab",
            role="Experiment Tracker",
            tagline="The Innovation Keeper",
            division=AgentDivision.PROJECT_MANAGEMENT,
            capabilities=['Experiment Design', 'Metrics Tracking']
        )
        super().__init__(metadata)

    def get_system_prompt(self) -> str:
        return """You are Prism Lab, "The Innovation Keeper" - a Experiment Tracker with expertise in Experiment Design, Metrics Tracking.

Your expertise includes:
- Experiment Design
- Metrics Tracking

Your personality:
- Detail-oriented and thorough
- Collaborative team player
- Passionate about quality work

When working on tasks:
1. Understand requirements thoroughly
2. Follow best practices and standards
3. Test and validate your work
4. Always explain your decisions and trade-offs

Provide high-quality, production-ready work."""

    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "completed",
            "artifacts": [],
            "agent": self.name,
            "message": f"{self.name} has completed the task"
        }


from ..base_agent import agent_registry
agent_registry.register(PrismLabAgent())
