"""
Shield - The Compliance Guardian
Legal Compliance Checker agent
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentMetadata, AgentDivision


class ShieldAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            id="shield",
            name="Shield",
            role="Legal Compliance Checker",
            tagline="The Compliance Guardian",
            division=AgentDivision.SUPPORT,
            capabilities=['Compliance', 'Security', 'Privacy']
        )
        super().__init__(metadata)

    def get_system_prompt(self) -> str:
        return """You are Shield, "The Compliance Guardian" - a Legal Compliance Checker with expertise in Compliance, Security, Privacy.

Your expertise includes:
- Compliance
- Security
- Privacy

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
agent_registry.register(ShieldAgent())
