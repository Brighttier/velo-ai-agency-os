"""
Sentinel - The System Watchdog
Infrastructure Maintainer agent
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentMetadata, AgentDivision


class SentinelAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            id="sentinel",
            name="Sentinel",
            role="Infrastructure Maintainer",
            tagline="The System Watchdog",
            division=AgentDivision.SUPPORT,
            capabilities=['Monitoring', 'Infrastructure Health']
        )
        super().__init__(metadata)

    def get_system_prompt(self) -> str:
        return """You are Sentinel, "The System Watchdog" - a Infrastructure Maintainer with expertise in Monitoring, Infrastructure Health.

Your expertise includes:
- Monitoring
- Infrastructure Health

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
agent_registry.register(SentinelAgent())
