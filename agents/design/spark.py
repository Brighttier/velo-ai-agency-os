"""
Spark - The Delight Designer
Whimsy Injector agent
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentMetadata, AgentDivision


class SparkAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            id="spark",
            name="Spark",
            role="Whimsy Injector",
            tagline="The Delight Designer",
            division=AgentDivision.DESIGN,
            capabilities=['Micro-interactions', 'Animations']
        )
        super().__init__(metadata)

    def get_system_prompt(self) -> str:
        return """You are Spark, "The Delight Designer" - a Whimsy Injector with expertise in Micro-interactions, Animations.

Your expertise includes:
- Micro-interactions
- Animations

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
agent_registry.register(SparkAgent())
