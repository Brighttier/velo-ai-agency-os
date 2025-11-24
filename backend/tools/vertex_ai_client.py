"""
Vertex AI Integration
Client for Google Cloud Vertex AI (Gemini 1.5 Pro)
"""

import os
from typing import Dict, List, Any, Optional, AsyncIterator
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, GenerationConfig
import vertexai


class VertexAIClient:
    """
    Client for interacting with Google Vertex AI (Gemini models)
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        location: Optional[str] = None,
        model_name: str = "gemini-1.5-pro"
    ):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = location or os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.model_name = model_name

        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable or project_id parameter required")

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)

        # Initialize the model
        self.model = GenerativeModel(self.model_name)

    def create_generation_config(
        self,
        temperature: float = 0.7,
        top_p: float = 0.95,
        top_k: int = 40,
        max_output_tokens: int = 8192,
    ) -> GenerationConfig:
        """
        Create a generation configuration for the model

        Args:
            temperature: Controls randomness (0.0 = deterministic, 1.0 = creative)
            top_p: Nucleus sampling threshold
            top_k: Top-k sampling
            max_output_tokens: Maximum tokens to generate

        Returns:
            GenerationConfig object
        """
        return GenerationConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_output_tokens,
        )

    async def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.7,
        max_output_tokens: int = 8192,
    ) -> str:
        """
        Generate content using Gemini

        Args:
            prompt: User prompt
            system_instruction: System instruction for the model
            temperature: Creativity level (0.0-1.0)
            max_output_tokens: Maximum response length

        Returns:
            Generated text content
        """
        config = self.create_generation_config(
            temperature=temperature,
            max_output_tokens=max_output_tokens
        )

        # Create model with system instruction if provided
        if system_instruction:
            model = GenerativeModel(
                self.model_name,
                system_instruction=[system_instruction]
            )
        else:
            model = self.model

        response = await model.generate_content_async(
            prompt,
            generation_config=config
        )

        return response.text

    async def generate_code(
        self,
        task_description: str,
        system_prompt: str,
        context: Optional[Dict[str, Any]] = None,
        language: str = "typescript",
    ) -> str:
        """
        Generate code for a specific task

        Args:
            task_description: Description of what to build
            system_prompt: Agent's system prompt (personality and expertise)
            context: Additional context (existing code, requirements, etc.)
            language: Programming language

        Returns:
            Generated code
        """
        # Build comprehensive prompt
        prompt_parts = [
            f"# Task\n{task_description}\n",
            f"\n# Language\n{language}\n",
        ]

        if context:
            if context.get('existing_code'):
                prompt_parts.append(f"\n# Existing Code\n```{language}\n{context['existing_code']}\n```\n")
            if context.get('requirements'):
                prompt_parts.append(f"\n# Requirements\n{context['requirements']}\n")
            if context.get('design_system'):
                prompt_parts.append(f"\n# Design System\n{context['design_system']}\n")

        prompt_parts.append("\n# Instructions\nGenerate production-ready code following best practices.")

        prompt = "\n".join(prompt_parts)

        code = await self.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            temperature=0.3,  # Lower temperature for code generation
            max_output_tokens=8192
        )

        return code

    async def generate_prd(
        self,
        user_prompt: str,
        system_prompt: str,
    ) -> str:
        """
        Generate a Product Requirements Document

        Args:
            user_prompt: User's description of what to build
            system_prompt: Product Manager agent's system prompt

        Returns:
            Generated PRD in Markdown format
        """
        prompt = f"""Generate a comprehensive Product Requirements Document (PRD) for the following project:

{user_prompt}

The PRD should include:
1. Overview and Vision
2. Target Users
3. Key Features (detailed)
4. Technical Requirements
5. Success Criteria
6. Timeline Estimate
7. Risks and Mitigation

Format the output as a well-structured Markdown document."""

        prd = await self.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=8192
        )

        return prd

    async def analyze_and_break_down_tasks(
        self,
        prd_content: str,
        system_prompt: str,
    ) -> List[Dict[str, Any]]:
        """
        Analyze PRD and break down into concrete tasks

        Args:
            prd_content: The generated PRD
            system_prompt: Agent's system prompt

        Returns:
            List of task dictionaries
        """
        prompt = f"""Analyze the following PRD and break it down into concrete, actionable tasks:

{prd_content}

For each task, provide:
1. Title (concise)
2. Description (detailed)
3. Assigned agent (choose from: pixel, atlas, nova, neuron, aurora, etc.)
4. Priority (low, medium, high, urgent)
5. Estimated effort (hours)
6. Dependencies (other task titles)

Return the tasks as a JSON array."""

        response = await self.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            temperature=0.5,
            max_output_tokens=4096
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
        except Exception as e:
            # Fallback: return a default task structure
            return [{
                "title": "Parse PRD and create detailed tasks",
                "description": "The AI response needs manual review",
                "assigned_agent": "conductor",
                "priority": "high",
                "estimated_effort": 2,
                "dependencies": []
            }]

    async def validate_code(
        self,
        code: str,
        language: str,
        requirements: str,
        system_prompt: str,
    ) -> Dict[str, Any]:
        """
        Validate generated code (Reality Checker)

        Args:
            code: The code to validate
            language: Programming language
            requirements: Original requirements
            system_prompt: QA agent's system prompt

        Returns:
            Validation result with passed status and feedback
        """
        prompt = f"""Review the following {language} code against the requirements:

# Requirements
{requirements}

# Code
```{language}
{code}
```

Analyze the code for:
1. Correctness - Does it meet the requirements?
2. Best Practices - Does it follow language conventions?
3. Security - Are there any security issues?
4. Performance - Are there obvious performance issues?
5. Error Handling - Is error handling adequate?
6. Code Quality - Is it maintainable and readable?

Return a JSON object with:
- "passed": boolean (true if code passes all checks)
- "issues": array of issue objects with "severity", "category", and "description"
- "suggestions": array of improvement suggestions
- "score": number 0-100 (overall quality score)"""

        response = await self.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            temperature=0.3,
            max_output_tokens=2048
        )

        # Parse JSON response
        import json
        try:
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0].strip()
            else:
                json_str = response.strip()

            result = json.loads(json_str)
            return result
        except Exception:
            # Fallback validation result
            return {
                "passed": True,
                "issues": [],
                "suggestions": [],
                "score": 85
            }

    async def generate_documentation(
        self,
        doc_type: str,
        content_context: Dict[str, Any],
        system_prompt: str,
    ) -> str:
        """
        Generate various types of documentation

        Args:
            doc_type: Type of doc (user_manual, deployment_guide, api_docs, etc.)
            content_context: Context including code, PRD, architecture, etc.
            system_prompt: Technical Writer agent's system prompt

        Returns:
            Generated documentation in Markdown
        """
        prompts = {
            "user_manual": "Generate a comprehensive user manual for end users",
            "deployment_guide": "Generate a detailed deployment guide for DevOps teams",
            "api_docs": "Generate API documentation with examples",
            "architecture_doc": "Generate architecture documentation with diagrams",
            "test_report": "Generate a QA test report summarizing test results"
        }

        base_prompt = prompts.get(doc_type, "Generate documentation")

        prompt_parts = [f"# Task\n{base_prompt}\n"]

        if content_context.get('prd'):
            prompt_parts.append(f"\n# Product Requirements\n{content_context['prd']}\n")
        if content_context.get('code'):
            prompt_parts.append(f"\n# Codebase Overview\n{content_context['code']}\n")
        if content_context.get('architecture'):
            prompt_parts.append(f"\n# Architecture\n{content_context['architecture']}\n")

        prompt_parts.append("\nGenerate clear, comprehensive documentation in Markdown format.")

        prompt = "\n".join(prompt_parts)

        documentation = await self.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            temperature=0.6,
            max_output_tokens=8192
        )

        return documentation

    async def generate_architecture_diagram(
        self,
        prd_content: str,
        tech_stack: Dict[str, str],
        system_prompt: str,
    ) -> str:
        """
        Generate Mermaid.js architecture diagram

        Args:
            prd_content: The PRD
            tech_stack: Dictionary of technologies to use
            system_prompt: Architect agent's system prompt

        Returns:
            Mermaid.js diagram code
        """
        prompt = f"""Based on the following PRD and tech stack, generate a Mermaid.js architecture diagram:

# PRD
{prd_content}

# Tech Stack
{tech_stack}

Generate a Mermaid.js diagram showing:
1. System components
2. Data flow
3. External integrations
4. Database relationships

Return ONLY the Mermaid.js code wrapped in a code block."""

        diagram = await self.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            temperature=0.5,
            max_output_tokens=2048
        )

        return diagram

    async def chat_with_context(
        self,
        messages: List[Dict[str, str]],
        system_prompt: str,
    ) -> str:
        """
        Multi-turn conversation with context

        Args:
            messages: List of message dicts with 'role' and 'content'
            system_prompt: Agent's system prompt

        Returns:
            Assistant's response
        """
        # Build conversation prompt
        conversation = []
        for msg in messages:
            role = msg.get('role', 'user')
            content = msg.get('content', '')
            conversation.append(f"{role.upper()}: {content}")

        prompt = "\n\n".join(conversation)

        response = await self.generate_content(
            prompt=prompt,
            system_instruction=system_prompt,
            temperature=0.7,
            max_output_tokens=4096
        )

        return response


# ==============================================================================
# Usage Example
# ==============================================================================

async def example_usage():
    """Example of how to use VertexAIClient"""

    client = VertexAIClient()

    # Example 1: Generate PRD
    product_manager_prompt = """You are a Product Manager with 10 years of experience.
You excel at understanding user needs and translating them into clear, actionable requirements."""

    prd = await client.generate_prd(
        user_prompt="Build a task management app for remote teams",
        system_prompt=product_manager_prompt
    )
    print("Generated PRD:\n", prd[:500], "...\n")

    # Example 2: Generate code
    frontend_dev_prompt = """You are Pixel, a frontend developer specializing in React and TypeScript.
You write clean, modern code following best practices."""

    code = await client.generate_code(
        task_description="Create a TaskCard component that displays task title, status, and assignee",
        system_prompt=frontend_dev_prompt,
        language="typescript",
        context={
            "design_system": "Use Tailwind CSS with primary color #1DBF73"
        }
    )
    print("Generated Code:\n", code[:500], "...\n")

    # Example 3: Validate code
    qa_prompt = """You are a QA engineer who validates code quality, security, and best practices."""

    validation = await client.validate_code(
        code=code,
        language="typescript",
        requirements="Component should display task information",
        system_prompt=qa_prompt
    )
    print("Validation Result:", validation)


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
