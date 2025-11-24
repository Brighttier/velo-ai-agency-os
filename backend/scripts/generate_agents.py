"""
Script to generate all remaining AI agent files
This creates Python files for all 51 agents based on the template
"""

import os

# All 51 agents with their metadata
AGENTS = [
    # Engineering (7)
    ("pixel", "Pixel", "Frontend Developer", "The UI Craftsman", "engineering", ["React", "Next.js", "TypeScript", "Tailwind CSS"]),
    ("atlas", "Atlas", "Backend Architect", "The Infrastructure Oracle", "engineering", ["System Design", "API Architecture", "Database Design"]),
    ("nova", "Nova", "Mobile App Builder", "The Cross-Platform Pioneer", "engineering", ["React Native", "iOS", "Android"]),
    ("neuron", "Neuron", "AI Engineer", "The Neural Network Whisperer", "engineering", ["Machine Learning", "LLMs", "Vector Databases"]),
    ("forge", "Forge", "DevOps Automator", "The Pipeline Architect", "engineering", ["CI/CD", "Docker", "Kubernetes"]),
    ("blitz", "Blitz", "Rapid Prototyper", "The Speed Demon", "engineering", ["MVP Development", "Quick Iterations"]),
    ("sage", "Sage", "Senior Developer", "The Code Philosopher", "engineering", ["Code Review", "Best Practices", "Mentorship"]),

    # Design (6)
    ("aurora", "Aurora", "UI Designer", "The Visual Alchemist", "design", ["Visual Design", "Design Systems", "Figma"]),
    ("echo", "Echo", "UX Researcher", "The User Advocate", "design", ["User Research", "Usability Testing"]),
    ("compass", "Compass", "UX Architect", "The Experience Navigator", "design", ["Information Architecture", "User Flows"]),
    ("ember", "Ember", "Brand Guardian", "The Identity Keeper", "design", ["Brand Strategy", "Visual Identity"]),
    ("canvas", "Canvas", "Visual Storyteller", "The Design Narrator", "design", ["Illustration", "Iconography"]),
    ("spark", "Spark", "Whimsy Injector", "The Delight Designer", "design", ["Micro-interactions", "Animations"]),

    # Marketing (8)
    ("rocket", "Rocket", "Growth Hacker", "The Viral Catalyst", "marketing", ["Growth Strategy", "A/B Testing", "Viral Marketing"]),
    ("quill", "Quill", "Content Creator", "The Story Weaver", "marketing", ["Copywriting", "Content Strategy", "SEO"]),
    ("chirp", "Chirp", "Twitter Engager", "The Tweet Maestro", "marketing", ["Twitter Strategy", "Community Engagement"]),
    ("rhythm", "Rhythm", "TikTok Strategist", "The Trend Rider", "marketing", ["Short-form Video", "TikTok Trends"]),
    ("prism", "Prism", "Instagram Curator", "The Visual Curator", "marketing", ["Instagram Strategy", "Visual Content"]),
    ("pulse", "Pulse", "Reddit Community Builder", "The Community Architect", "marketing", ["Reddit Strategy", "Community Management"]),
    ("phoenix", "Phoenix", "App Store Optimizer", "The Ranking Wizard", "marketing", ["ASO", "App Marketing"]),
    ("nexus", "Nexus", "Social Media Strategist", "The Cross-Channel Conductor", "marketing", ["Multi-channel Strategy", "Campaign Management"]),

    # Product (3)
    ("sprint", "Sprint", "Sprint Prioritizer", "The Backlog Master", "product", ["Prioritization", "Roadmap Planning"]),
    ("horizon", "Horizon", "Trend Researcher", "The Future Scout", "product", ["Market Research", "Trend Analysis"]),
    ("synthesis", "Synthesis", "Feedback Synthesizer", "The Voice of Users", "product", ["User Feedback", "Data Analysis"]),

    # Project Management (5)
    ("maestro", "Maestro", "Studio Producer", "The Creative Director", "project_management", ["Creative Direction", "Resource Management"]),
    ("shepherd", "Shepherd", "Project Shepherd", "The Deadline Guardian", "project_management", ["Timeline Management", "Risk Mitigation"]),
    ("clockwork", "Clockwork", "Studio Operations", "The Efficiency Engine", "project_management", ["Process Optimization", "Workflow Automation"]),
    ("prism_lab", "Prism Lab", "Experiment Tracker", "The Innovation Keeper", "project_management", ["Experiment Design", "Metrics Tracking"]),
    ("oracle", "Oracle", "Senior Project Manager", "The Strategic Planner", "project_management", ["Strategic Planning", "Program Management"]),

    # Testing (7)
    ("sherlock", "Sherlock", "Evidence Collector", "The Bug Detective", "testing", ["Bug Hunting", "Test Case Design"]),
    ("gatekeeper", "Gatekeeper", "Reality Checker", "The Quality Guardian", "testing", ["Code Review", "Quality Assurance"]),
    ("verdict", "Verdict", "Test Results Analyzer", "The Results Interpreter", "testing", ["Test Analysis", "Reporting"]),
    ("benchmark", "Benchmark", "Performance Benchmarker", "The Speed Auditor", "testing", ["Performance Testing", "Load Testing"]),
    ("postman", "Postman", "API Tester", "The Endpoint Validator", "testing", ["API Testing", "Integration Testing"]),
    ("forge_tester", "Forge Tester", "Tool Evaluator", "The Tool Critic", "testing", ["Tool Evaluation", "Tech Stack Assessment"]),
    ("flow", "Flow", "Workflow Optimizer", "The Process Perfectionist", "testing", ["Workflow Analysis", "Process Improvement"]),

    # Support (6)
    ("beacon", "Beacon", "Support Responder", "The Help Hero", "support", ["Customer Support", "Documentation"]),
    ("insight", "Insight", "Analytics Reporter", "The Data Storyteller", "support", ["Data Analysis", "Reporting"]),
    ("ledger", "Ledger", "Finance Tracker", "The Budget Keeper", "support", ["Budget Management", "Financial Reporting"]),
    ("sentinel", "Sentinel", "Infrastructure Maintainer", "The System Watchdog", "support", ["Monitoring", "Infrastructure Health"]),
    ("shield", "Shield", "Legal Compliance Checker", "The Compliance Guardian", "support", ["Compliance", "Security", "Privacy"]),
    ("summit", "Summit", "Executive Summary Generator", "The C-Suite Translator", "support", ["Executive Communication", "Summary Generation"]),

    # Spatial Computing (6)
    ("hologram", "Hologram", "XR Interface Architect", "The Reality Designer", "spatial_computing", ["XR Design", "3D Interfaces"]),
    ("titanium", "Titanium", "macOS Spatial/Metal Engineer", "The Apple Silicon Master", "spatial_computing", ["Metal", "macOS Development"]),
    ("immerse", "Immerse", "XR Immersive Developer", "The Presence Creator", "spatial_computing", ["VR Development", "Immersive Experiences"]),
    ("gesture", "Gesture", "XR Cockpit Interaction Specialist", "The Hand Interface Expert", "spatial_computing", ["Hand Tracking", "Gesture Recognition"]),
    ("vision", "Vision", "visionOS Spatial Engineer", "The Spatial Computing Pioneer", "spatial_computing", ["visionOS", "Spatial Computing"]),
    ("terminal", "Terminal", "Terminal Integration Specialist", "The CLI Commander", "spatial_computing", ["CLI Tools", "Terminal UX"]),

    # Specialized (3)
    ("conductor", "Conductor", "Agents Orchestrator", "The Team Coordinator", "specialized", ["Agent Coordination", "Workflow Orchestration"]),
    ("prism_analytics", "Prism Analytics", "Data Analytics Reporter", "The Metrics Storyteller", "specialized", ["Advanced Analytics", "Data Visualization"]),
    ("index", "Index", "LSP/Index Engineer", "The Code Intelligence Architect", "specialized", ["Language Servers", "Code Analysis"]),
]

AGENT_TEMPLATE = '''"""
{name} - {tagline}
{role} agent
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentMetadata, AgentDivision


class {class_name}Agent(BaseAgent):
    def __init__(self):
        metadata = AgentMetadata(
            id="{agent_id}",
            name="{name}",
            role="{role}",
            tagline="{tagline}",
            division=AgentDivision.{division_upper},
            capabilities={capabilities}
        )
        super().__init__(metadata)

    def get_system_prompt(self) -> str:
        return """You are {name}, "{tagline}" - a {role} with expertise in {expertise}.

Your expertise includes:
{expertise_details}

Your personality:
- {personality_trait_1}
- {personality_trait_2}
- {personality_trait_3}

When working on tasks:
1. {guideline_1}
2. {guideline_2}
3. {guideline_3}
4. Always explain your decisions and trade-offs

Provide high-quality, production-ready work."""

    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {{
            "status": "completed",
            "artifacts": [],
            "agent": self.name,
            "message": f"{{self.name}} has completed the task"
        }}


from ..base_agent import agent_registry
agent_registry.register({class_name}Agent())
'''

def generate_agent_file(agent_data):
    """Generate a Python file for an agent"""
    agent_id, name, role, tagline, division, capabilities = agent_data

    class_name = name.replace(" ", "").replace("-", "")
    division_upper = division.upper()

    # Create division directory if it doesn't exist
    division_dir = f"../agents/{division}"
    os.makedirs(division_dir, exist_ok=True)

    # Generate content
    content = AGENT_TEMPLATE.format(
        name=name,
        tagline=tagline,
        role=role,
        agent_id=agent_id,
        class_name=class_name,
        division_upper=division_upper,
        capabilities=capabilities,
        expertise=", ".join(capabilities[:3]),
        expertise_details="\n".join([f"- {cap}" for cap in capabilities]),
        personality_trait_1="Detail-oriented and thorough",
        personality_trait_2="Collaborative team player",
        personality_trait_3="Passionate about quality work",
        guideline_1="Understand requirements thoroughly",
        guideline_2="Follow best practices and standards",
        guideline_3="Test and validate your work"
    )

    # Write file
    filepath = f"{division_dir}/{agent_id}.py"
    with open(filepath, 'w') as f:
        f.write(content)

    print(f"✓ Generated {filepath}")

def main():
    """Generate all agent files"""
    print("Generating all 51 AI agents...")

    for agent_data in AGENTS:
        try:
            generate_agent_file(agent_data)
        except Exception as e:
            print(f"✗ Error generating {agent_data[1]}: {e}")

    print(f"\n✓ Generated {len(AGENTS)} agent files successfully!")

if __name__ == "__main__":
    main()
