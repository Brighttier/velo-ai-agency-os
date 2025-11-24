"""
Atlas - The Infrastructure Oracle
Backend Architect Agent specializing in system design and APIs
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentMetadata, AgentDivision


class AtlasAgent(BaseAgent):
    """
    Atlas specializes in:
    - System architecture design
    - API development (REST, GraphQL)
    - Database design
    - Microservices
    - Cloud infrastructure
    - Performance optimization
    """

    def __init__(self):
        metadata = AgentMetadata(
            id="atlas",
            name="Atlas",
            role="Backend Architect",
            tagline="The Infrastructure Oracle",
            division=AgentDivision.ENGINEERING,
            capabilities=[
                "System Design", "API Architecture", "Database Design",
                "Microservices", "Python", "Node.js", "PostgreSQL",
                "Redis", "Message Queues", "Cloud Architecture",
                "Performance Optimization", "Scalability"
            ]
        )
        super().__init__(metadata)

    def get_system_prompt(self) -> str:
        return """You are Atlas, "The Infrastructure Oracle" - a backend architecture specialist with expertise in building scalable, reliable systems.

Your expertise includes:
- System architecture and design patterns
- RESTful and GraphQL API design
- Database schema design (PostgreSQL, MongoDB, Redis)
- Microservices architecture
- Python (FastAPI, Django) and Node.js
- Message queues and event-driven systems
- Caching strategies
- Cloud infrastructure (GCP, AWS)
- Performance optimization and scalability

Your personality:
- Strategic thinker who sees the big picture
- Obsessed with reliability and performance
- Pragmatic about technology choices
- Security-conscious
- Advocates for maintainable architecture

When designing systems:
1. Start with clear system requirements
2. Design scalable, maintainable architectures
3. Choose appropriate databases and data models
4. Design clean, well-documented APIs
5. Consider security from the start
6. Plan for observability (logging, monitoring)
7. Think about error handling and resilience
8. Document architectural decisions and trade-offs

Always explain your reasoning and consider trade-offs between different approaches."""

    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a backend architecture task

        Args:
            task: Contains requirements, scale expectations, constraints
            context: Project context, existing systems, infrastructure

        Returns:
            System design documents, API specs, database schemas
        """
        # TODO: Implement Vertex AI integration
        # TODO: Generate architecture artifacts
        # TODO: Create database schemas
        # TODO: Design API endpoints

        return {
            "status": "completed",
            "artifacts": [
                {
                    "type": "architecture_diagram",
                    "path": "docs/architecture.md",
                    "content": "# System Architecture"
                },
                {
                    "type": "database_schema",
                    "path": "database/schema.sql",
                    "content": "-- Database schema"
                },
                {
                    "type": "api_spec",
                    "path": "docs/api-spec.yaml",
                    "content": "# API Specification"
                }
            ],
            "agent": self.name,
            "message": f"{self.name} has completed the backend architecture"
        }


# Register agent
from ..base_agent import agent_registry
agent_registry.register(AtlasAgent())
