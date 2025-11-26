"""
Gemini AI Integration for Velo
Provides interface to Google's Gemini API (replaces Vertex AI)
"""

import os
import json
from typing import Dict, Any, List, Optional
import google.generativeai as genai

# Initialize Gemini AI
API_KEY = os.getenv("GEMINI_API_KEY", "")

if API_KEY:
    genai.configure(api_key=API_KEY)


class GeminiAIClient:
    """Client for interacting with Gemini AI models"""

    def __init__(self, model_name: str = "gemini-1.5-flash"):
        """
        Initialize Gemini AI client

        Args:
            model_name: Model to use (gemini-1.5-pro, gemini-1.5-flash, gemini-2.0-flash-exp)
        """
        self.model_name = model_name
        if API_KEY:
            self.model = genai.GenerativeModel(model_name)
        else:
            self.model = None

    async def detect_project_type(self, project_name: str, project_description: str) -> str:
        """
        Detect the type of project based on name and description

        Args:
            project_name: Name of the project
            project_description: Description of the project

        Returns:
            Project type: 'software', 'marketing', 'design', 'business', or 'content'
        """
        if not self.model or not API_KEY:
            # Fallback to keyword-based detection
            desc_lower = f"{project_name} {project_description}".lower()

            # Marketing keywords
            if any(keyword in desc_lower for keyword in [
                'marketing', 'campaign', 'social media', 'tiktok', 'instagram',
                'facebook', 'twitter', 'ad', 'promotion', 'viral', 'influencer',
                'seo', 'content marketing', 'email marketing', 'growth'
            ]):
                return 'marketing'

            # Design keywords
            if any(keyword in desc_lower for keyword in [
                'design', 'branding', 'logo', 'ui', 'ux', 'visual', 'graphics',
                'illustration', 'mockup', 'prototype', 'figma', 'adobe'
            ]):
                return 'design'

            # Business/Strategy keywords
            if any(keyword in desc_lower for keyword in [
                'strategy', 'business plan', 'market research', 'analysis',
                'consulting', 'roadmap', 'planning', 'presentation'
            ]):
                return 'business'

            # Content creation keywords
            if any(keyword in desc_lower for keyword in [
                'blog', 'article', 'content', 'copywriting', 'writing',
                'documentation', 'video script', 'podcast'
            ]):
                return 'content'

            # Default to software
            return 'software'

        # Use AI for more accurate detection
        prompt = f"""Analyze this project and determine its type.

Project Name: {project_name}
Description: {project_description}

Return ONLY ONE of these types:
- software (app development, web development, API, backend, frontend, mobile app, etc.)
- marketing (campaigns, social media, ads, growth, SEO, etc.)
- design (branding, UI/UX, graphics, visual identity, etc.)
- business (strategy, plans, analysis, consulting, etc.)
- content (blogs, articles, videos, copywriting, etc.)

Answer with just the type, nothing else:"""

        try:
            response = await self.generate_content(prompt, temperature=0.1, max_tokens=10)
            project_type = response.strip().lower()
            if project_type in ['software', 'marketing', 'design', 'business', 'content']:
                return project_type
            return 'software'  # Default fallback
        except:
            return 'software'  # Default fallback on error

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        **kwargs
    ) -> str:
        """
        Generate content using Gemini AI

        Args:
            prompt: User prompt
            system_instruction: System instruction for model behavior
            temperature: Sampling temperature (0.0-2.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text content
        """
        if not self.model or not API_KEY:
            raise Exception("Gemini API key not configured. Set GEMINI_API_KEY environment variable.")

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,
            "top_k": 40,
        }

        # If system instruction provided, create model with it
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model

        response = model.generate_content(
            prompt,
            generation_config=generation_config,
            **kwargs
        )

        return response.text

    async def generate_with_history(
        self,
        messages: List[Dict[str, str]],
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192
    ) -> str:
        """
        Generate content with conversation history

        Args:
            messages: List of {"role": "user"|"model", "content": "..."}
            system_instruction: System instruction
            temperature: Sampling temperature
            max_tokens: Maximum tokens

        Returns:
            Generated response
        """
        if not self.model or not API_KEY:
            raise Exception("Gemini API key not configured. Set GEMINI_API_KEY environment variable.")

        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,
            "top_k": 40,
        }

        # Create model with system instruction
        if system_instruction:
            model = genai.GenerativeModel(
                self.model_name,
                system_instruction=system_instruction
            )
        else:
            model = self.model

        # Start chat session
        chat = model.start_chat()

        # Add history (all but last message)
        for msg in messages[:-1]:
            role = "user" if msg["role"] == "user" else "model"
            if role == "user":
                response = chat.send_message(msg["content"])

        # Send final message and get response
        final_message = messages[-1]["content"]
        response = chat.send_message(
            final_message,
            generation_config=generation_config
        )

        return response.text

    async def generate_prd(
        self,
        project_name: str,
        project_description: str,
        user_requirements: str
    ) -> str:
        """
        Generate Product Requirements Document

        Args:
            project_name: Name of the project
            project_description: Brief description
            user_requirements: Detailed user requirements

        Returns:
            Comprehensive PRD in Markdown format
        """
        system_instruction = """You are Oracle, a Senior Project Manager and Strategic Planner.
Your expertise is in creating comprehensive Product Requirements Documents (PRDs).

Generate a detailed, professional PRD that includes:
1. Executive Summary
2. Project Overview and Goals
3. User Personas and Use Cases
4. Functional Requirements (detailed)
5. Non-Functional Requirements (performance, security, scalability)
6. Technical Architecture Recommendations
7. Success Criteria and KPIs
8. Timeline and Milestones
9. Risk Assessment
10. Dependencies and Constraints

Use clear, professional language. Include specific details and measurable criteria.
Format the PRD in Markdown with proper headings and sections."""

        prompt = f"""Create a comprehensive Product Requirements Document for:

Project Name: {project_name}
Description: {project_description}

User Requirements:
{user_requirements}

Generate a detailed, production-ready PRD following best practices."""

        return await self.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.5,
            max_tokens=8192
        )

    async def generate_task_breakdown(
        self,
        prd_content: str,
        project_name: str
    ) -> List[Dict[str, Any]]:
        """
        Break down PRD into actionable tasks

        Args:
            prd_content: The PRD content
            project_name: Project name

        Returns:
            List of task dictionaries
        """
        system_instruction = """You are Neuron, an AI Engineer and Task Breakdown Specialist.
Your expertise is in analyzing PRDs and breaking them into clear, actionable development tasks.

For each task, specify:
- title: Clear, action-oriented title
- description: Detailed description of what needs to be done
- assigned_agent: Which Velo agent should handle it (pixel, atlas, nova, etc.)
- priority: high, medium, or low
- dependencies: List of task titles this depends on
- estimated_hours: Realistic time estimate

Return ONLY valid JSON array format."""

        prompt = f"""Analyze this PRD and break it into development tasks:

Project: {project_name}

PRD:
{prd_content[:4000]}  # Limit PRD length for context

Return a JSON array of tasks with the structure:
[
  {{
    "title": "Task name",
    "description": "Detailed description",
    "assigned_agent": "atlas",
    "priority": "high",
    "dependencies": [],
    "estimated_hours": 8
  }}
]

Focus on creating 10-15 key tasks that cover all major aspects of the project."""

        response = await self.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3,
            max_tokens=4096
        )

        # Parse JSON response
        try:
            # Extract JSON from markdown code blocks if present
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            tasks = json.loads(json_str)
            return tasks
        except json.JSONDecodeError as e:
            print(f"Failed to parse tasks JSON: {e}")
            print(f"Response was: {response}")
            # Return fallback tasks
            return [
                {
                    "title": "Design System Architecture",
                    "description": f"Design the overall system architecture for {project_name}",
                    "assigned_agent": "atlas",
                    "priority": "high",
                    "dependencies": [],
                    "estimated_hours": 16
                },
                {
                    "title": "Create Database Schema",
                    "description": "Design and implement database schema",
                    "assigned_agent": "atlas",
                    "priority": "high",
                    "dependencies": ["Design System Architecture"],
                    "estimated_hours": 8
                },
                {
                    "title": "Build Backend API",
                    "description": "Implement core backend API endpoints",
                    "assigned_agent": "atlas",
                    "priority": "high",
                    "dependencies": ["Create Database Schema"],
                    "estimated_hours": 24
                },
                {
                    "title": "Design UI Components",
                    "description": "Design and implement frontend UI components",
                    "assigned_agent": "pixel",
                    "priority": "medium",
                    "dependencies": ["Build Backend API"],
                    "estimated_hours": 20
                }
            ]

    async def generate_content_for_task(
        self,
        task_title: str,
        task_description: str,
        agent_name: str,
        project_type: str = 'software',
        project_context: str = '',
        context: Dict[str, Any] = None
    ) -> str:
        """
        Generate appropriate content for a task based on project type

        Args:
            task_title: Title of the task
            task_description: Detailed description
            agent_name: Which agent is generating the content
            project_type: Type of project (software, marketing, design, business, content)
            project_context: Additional project context
            context: Additional context dictionary

        Returns:
            Generated content (code, campaign strategy, design brief, etc.)
        """
        # Map agents to their specializations by project type
        agent_specs = {
            # Software agents
            "pixel": "Frontend Developer (React, Next.js, TypeScript)",
            "atlas": "Backend Architect (Python, FastAPI, PostgreSQL)",
            "nova": "Mobile App Builder (React Native)",
            "neuron": "AI Engineer (LangChain, LangGraph, Gemini AI)",
            "forge": "DevOps Automator (Docker, Kubernetes, CI/CD)",
            "sherlock": "QA Tester (Testing, Quality Assurance)",
            "judge": "Code Reviewer (Best Practices, Architecture)",

            # Marketing agents
            "rocket": "Growth Hacker (Viral Marketing, A/B Testing, Growth Strategy)",
            "quill": "Content Creator (Copywriting, Content Strategy, Storytelling)",
            "chirp": "Twitter Strategist (Twitter Engagement, Viral Tweets)",
            "rhythm": "TikTok Strategist (Short-form Video, TikTok Trends, Viral Content)",
            "prism": "Instagram Curator (Instagram Strategy, Visual Content)",
            "pulse": "Reddit Community Builder (Reddit Strategy, Community Management)",
            "nexus": "Social Media Strategist (Multi-channel Strategy, Campaign Management)",

            # Design agents
            "aurora": "UI/UX Designer (Interface Design, User Experience)",

            # Business/Strategy agents
            "oracle": "Strategic Planner (Business Strategy, Market Analysis, Planning)",
        }

        specialization = agent_specs.get(agent_name.lower(), "Project Specialist")

        # Build system instruction based on project type
        if project_type == 'marketing':
            system_instruction = f"""You are {agent_name.title()}, a {specialization}.
Generate comprehensive marketing content and strategies.

Your deliverables should include:
- Campaign strategies and tactics
- Target audience analysis
- Content calendars and posting schedules
- Copywriting (captions, ad copy, scripts)
- Performance metrics and KPIs
- Platform-specific recommendations
- Creative briefs and guidelines

Format: Use Markdown with clear sections. Be specific and actionable."""

            prompt = f"""Create marketing content for this task:

Task: {task_title}
Description: {task_description}
Project Context: {project_context}

Deliver a comprehensive marketing strategy/content document."""

        elif project_type == 'design':
            system_instruction = f"""You are {agent_name.title()}, a {specialization}.
Generate design specifications and creative direction.

Your deliverables should include:
- Design specifications and guidelines
- Color palettes and typography
- Layout recommendations
- Visual style guidelines
- Component specifications
- Accessibility considerations

Format: Use Markdown. Include specific hex codes, measurements, and clear guidelines."""

            prompt = f"""Create design specifications for this task:

Task: {task_title}
Description: {task_description}
Project Context: {project_context}

Deliver comprehensive design documentation."""

        elif project_type == 'business':
            system_instruction = f"""You are {agent_name.title()}, a {specialization}.
Generate business strategy and analysis.

Your deliverables should include:
- Strategic recommendations
- Market analysis
- Competitive landscape
- Action plans and timelines
- Success metrics
- Risk assessment

Format: Use Markdown with executive summary and detailed sections."""

            prompt = f"""Create business strategy for this task:

Task: {task_title}
Description: {task_description}
Project Context: {project_context}

Deliver a comprehensive business strategy document."""

        elif project_type == 'content':
            system_instruction = f"""You are {agent_name.title()}, a {specialization}.
Generate high-quality written content.

Your deliverables should include:
- Well-structured content
- SEO optimization
- Engaging copy
- Clear call-to-actions
- Target audience considerations

Format: Professional, publication-ready content."""

            prompt = f"""Create content for this task:

Task: {task_title}
Description: {task_description}
Project Context: {project_context}

Deliver polished, publication-ready content."""

        else:  # software
            system_instruction = f"""You are {agent_name.title()}, a {specialization}.
Generate production-ready, well-documented code following best practices.

Guidelines:
- Write clean, maintainable code
- Include comprehensive comments
- Handle errors appropriately
- Follow tech stack conventions
- Include type hints/annotations
- Consider security and performance"""

            context_str = ""
            if context:
                context_str = f"\n\nContext:\n{json.dumps(context, indent=2)}"

            prompt = f"""Generate code for this task:

Task: {task_title}
Description: {task_description}
Project Context: {project_context}{context_str}

Provide complete, production-ready code with comments."""

        return await self.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.3 if project_type == 'software' else 0.7,
            max_tokens=8192
        )

    # Keep backward compatibility
    async def generate_code(self, task_title: str, task_description: str, agent_name: str, context: Dict[str, Any] = None) -> str:
        """Legacy method for backward compatibility"""
        return await self.generate_content_for_task(
            task_title=task_title,
            task_description=task_description,
            agent_name=agent_name,
            project_type='software',
            context=context
        )


# Singleton instance
_gemini_client = None

def get_gemini_client(model_name: str = "gemini-1.5-flash") -> GeminiAIClient:
    """Get or create Gemini AI client instance"""
    global _gemini_client
    if _gemini_client is None or _gemini_client.model_name != model_name:
        _gemini_client = GeminiAIClient(model_name)
    return _gemini_client
