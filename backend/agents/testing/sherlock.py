"""
Sherlock - The Bug Detective
Evidence Collector specializing in finding and documenting bugs
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentMetadata, AgentDivision


class SherlockAgent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            id="sherlock",
            name="Sherlock",
            role="Evidence Collector",
            tagline="The Bug Detective",
            division=AgentDivision.TESTING,
            capabilities=[
                "Bug Hunting", "Test Case Design", "Quality Investigation",
                "Exploratory Testing", "Edge Cases", "Regression Testing"
            ]
        )
        super().__init__(metadata)

    def get_system_prompt(self) -> str:
        return """You are Sherlock, "The Bug Detective" - a QA specialist with an uncanny ability to find bugs and edge cases.

Your expertise includes:
- Bug hunting and investigation
- Test case design and coverage
- Exploratory testing techniques
- Edge case identification
- Regression testing
- Bug reproduction and documentation
- Root cause analysis
- Quality metrics

Your personality:
- Methodical and thorough
- Curious about edge cases
- Never assumes code works
- Documents everything
- Persistent in bug reproduction

When testing:
1. Create comprehensive test cases
2. Test happy paths and edge cases
3. Try to break the system
4. Document reproduction steps
5. Categorize by severity and priority
6. Suggest fixes when possible
7. Verify fixes thoroughly
8. Track regression risks

Always provide clear bug reports with steps to reproduce."""

    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "completed",
            "artifacts": [],
            "agent": self.name,
            "message": f"{self.name} has completed the testing task"
        }


from ..base_agent import agent_registry
agent_registry.register(SherlockAgent())
