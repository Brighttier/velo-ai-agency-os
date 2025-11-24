"""
Oracle - The Strategic Planner
Senior Project Manager agent
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentMetadata, AgentDivision


class OracleAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            id="oracle",
            name="Oracle",
            role="Senior Project Manager",
            tagline="The Strategic Planner",
            division=AgentDivision.PROJECT_MANAGEMENT,
            capabilities=['Strategic Planning', 'Program Management']
        )
        super().__init__(metadata)

    def get_system_prompt(self) -> str:
        return """You are Oracle, "The Strategic Planner" - a Senior Project Manager with expertise in Strategic Planning, Program Management.

Your expertise includes:
- Strategic Planning
- Program Management

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
agent_registry.register(OracleAgent())
