"""
Nova - The Cross-Platform Pioneer
Mobile App Builder specializing in React Native and cross-platform development
"""

from typing import Dict, Any
from ..base_agent import BaseAgent, AgentMetadata, AgentDivision


class NovaAgent(BaseAgent):
    """
    Nova specializes in:
    - React Native development
    - iOS and Android development
    - Cross-platform mobile apps
    - Mobile UX patterns
    - Native modules integration
    """

    def __init__(self):
        metadata = AgentMetadata(
            id="nova",
            name="Nova",
            role="Mobile App Builder",
            tagline="The Cross-Platform Pioneer",
            division=AgentDivision.ENGINEERING,
            capabilities=[
                "React Native", "iOS", "Android", "Mobile UX",
                "Expo", "Native Modules", "Mobile Performance",
                "App Store Deployment", "Push Notifications", "Mobile APIs"
            ]
        )
        super().__init__(metadata)

    def get_system_prompt(self) -> str:
        return """You are Nova, "The Cross-Platform Pioneer" - a mobile development specialist with expertise in building high-quality cross-platform applications.

Your expertise includes:
- React Native for iOS and Android
- Expo for rapid development
- Native modules and platform-specific code
- Mobile UX patterns and guidelines
- Performance optimization for mobile
- App Store and Play Store deployment
- Push notifications and deep linking
- Mobile-first architecture

Your personality:
- Pragmatic about platform choices
- Obsessed with mobile performance
- Advocates for user-centric design
- Experienced with both platforms
- Efficient and productivity-focused

When building mobile apps:
1. Use React Native with TypeScript
2. Follow iOS and Android design guidelines
3. Optimize for performance (60 FPS)
4. Handle platform-specific code gracefully
5. Implement proper navigation patterns
6. Consider offline-first architecture
7. Test on both iOS and Android
8. Plan for app store submission

Always explain mobile-specific considerations and trade-offs."""

    async def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "status": "completed",
            "artifacts": [
                {
                    "type": "mobile_component",
                    "path": "mobile/screens/HomeScreen.tsx",
                    "content": "// React Native component"
                }
            ],
            "agent": self.name,
            "message": f"{self.name} has completed the mobile development task"
        }


from ..base_agent import agent_registry
agent_registry.register(NovaAgent())
