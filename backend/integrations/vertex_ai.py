"""
Vertex AI Integration for Velo
Provides interface to Google's Vertex AI (Gemini models)
"""

import os
from typing import Dict, Any, List, Optional
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession, Content, Part

# Initialize Vertex AI
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "velo-479115")
LOCATION = "us-central1"

vertexai.init(project=PROJECT_ID, location=LOCATION)


class VertexAIClient:
    """Client for interacting with Vertex AI Gemini models"""

    def __init__(self, model_name: str = "gemini-1.5-pro"):
        """
        Initialize Vertex AI client

        Args:
            model_name: Model to use (gemini-1.5-pro, gemini-1.5-flash)
        """
        self.model_name = model_name
        self.model = GenerativeModel(model_name)

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 8192,
        **kwargs
    ) -> str:
        """
        Generate content using Vertex AI

        Args:
            prompt: User prompt
            system_instruction: System instruction for model behavior
            temperature: Sampling temperature (0.0-1.0)
            max_tokens: Maximum tokens to generate

        Returns:
            Generated text content
        """
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,
            "top_k": 40,
        }

        # If system instruction provided, create model with it
        if system_instruction:
            model = GenerativeModel(
                self.model_name,
                system_instruction=[system_instruction]
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
        generation_config = {
            "temperature": temperature,
            "max_output_tokens": max_tokens,
            "top_p": 0.95,
            "top_k": 40,
        }

        # Create model with system instruction
        if system_instruction:
            model = GenerativeModel(
                self.model_name,
                system_instruction=[system_instruction]
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
        import json
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

    async def generate_code(
        self,
        task_title: str,
        task_description: str,
        agent_name: str,
        context: Dict[str, Any] = None
    ) -> str:
        """
        Generate code for a specific task

        Args:
            task_title: Title of the task
            task_description: Detailed description
            agent_name: Which agent is generating the code
            context: Additional context (tech stack, existing code, etc.)

        Returns:
            Generated code
        """
        # Map agent to their specialization
        agent_specializations = {
            "pixel": "Frontend Developer (React, Next.js, TypeScript)",
            "atlas": "Backend Architect (Python, FastAPI, PostgreSQL)",
            "nova": "Mobile App Builder (React Native)",
            "neuron": "AI Engineer (LangChain, LangGraph, Vertex AI)",
            "forge": "DevOps Automator (Docker, Kubernetes, CI/CD)",
        }

        specialization = agent_specializations.get(
            agent_name,
            "Full-Stack Developer"
        )

        system_instruction = f"""You are {agent_name.title()}, a {specialization}.
Generate production-ready, well-documented code following best practices.

Guidelines:
- Write clean, maintainable code
- Include comprehensive comments
- Handle errors appropriately
- Follow the tech stack conventions
- Include type hints/annotations
- Consider security and performance"""

        context_str = ""
        if context:
            context_str = f"\n\nContext:\n{json.dumps(context, indent=2)}"

        prompt = f"""Generate code for this task:

Task: {task_title}
Description: {task_description}{context_str}

Provide complete, production-ready code with comments."""

        return await self.generate_content(
            prompt=prompt,
            system_instruction=system_instruction,
            temperature=0.2,
            max_tokens=8192
        )


# Singleton instance
_vertex_client = None

def get_vertex_client(model_name: str = "gemini-1.5-pro") -> VertexAIClient:
    """Get or create Vertex AI client instance"""
    global _vertex_client
    if _vertex_client is None or _vertex_client.model_name != model_name:
        _vertex_client = VertexAIClient(model_name)
    return _vertex_client
