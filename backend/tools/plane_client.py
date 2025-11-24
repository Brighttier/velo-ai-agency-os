"""
Plane.so API Client
Wrapper for Plane.so Community Edition API
Handles workspace, project, and issue management
"""

import os
import httpx
from typing import Dict, List, Any, Optional
from datetime import datetime


class PlaneClient:
    """
    API client for Plane.so integration
    Provides methods to interact with Plane's REST API
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        self.api_url = api_url or os.getenv("PLANE_API_URL", "http://localhost:8001")
        self.api_key = api_key or os.getenv("PLANE_API_KEY")

        if not self.api_key:
            raise ValueError("PLANE_API_KEY environment variable or api_key parameter required")

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        self.client = httpx.AsyncClient(
            base_url=self.api_url,
            headers=self.headers,
            timeout=30.0
        )

    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()

    # ==============================================================================
    # Workspace Management
    # ==============================================================================

    async def create_workspace(
        self,
        name: str,
        slug: str,
        tenant_id: str
    ) -> Dict[str, Any]:
        """
        Create a new workspace for a tenant

        Args:
            name: Workspace display name
            slug: URL-friendly workspace identifier
            tenant_id: Velo tenant ID for tracking

        Returns:
            Workspace data including workspace_id
        """
        payload = {
            "name": name,
            "slug": slug,
            "metadata": {
                "velo_tenant_id": tenant_id
            }
        }

        response = await self.client.post("/api/workspaces/", json=payload)
        response.raise_for_status()
        return response.json()

    async def get_workspace(self, workspace_slug: str) -> Dict[str, Any]:
        """Get workspace details"""
        response = await self.client.get(f"/api/workspaces/{workspace_slug}/")
        response.raise_for_status()
        return response.json()

    async def list_workspaces(self) -> List[Dict[str, Any]]:
        """List all workspaces"""
        response = await self.client.get("/api/workspaces/")
        response.raise_for_status()
        return response.json()

    # ==============================================================================
    # Project Management
    # ==============================================================================

    async def create_project(
        self,
        workspace_slug: str,
        name: str,
        description: str,
        velo_project_id: str,
        identifier: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new project in a workspace

        Args:
            workspace_slug: Workspace identifier
            name: Project name
            description: Project description
            velo_project_id: Velo project UUID for linking
            identifier: Optional short identifier (e.g., "ECOM")

        Returns:
            Project data including project_id
        """
        payload = {
            "name": name,
            "description": description,
            "identifier": identifier or name[:4].upper(),
            "metadata": {
                "velo_project_id": velo_project_id
            }
        }

        response = await self.client.post(
            f"/api/workspaces/{workspace_slug}/projects/",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    async def get_project(
        self,
        workspace_slug: str,
        project_id: str
    ) -> Dict[str, Any]:
        """Get project details"""
        response = await self.client.get(
            f"/api/workspaces/{workspace_slug}/projects/{project_id}/"
        )
        response.raise_for_status()
        return response.json()

    async def list_projects(self, workspace_slug: str) -> List[Dict[str, Any]]:
        """List all projects in a workspace"""
        response = await self.client.get(
            f"/api/workspaces/{workspace_slug}/projects/"
        )
        response.raise_for_status()
        return response.json()

    # ==============================================================================
    # Issue Management (Tasks)
    # ==============================================================================

    async def create_issue(
        self,
        workspace_slug: str,
        project_id: str,
        title: str,
        description: str,
        priority: str = "medium",
        assignee: Optional[str] = None,
        velo_task_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new issue (task) in a project

        Args:
            workspace_slug: Workspace identifier
            project_id: Project identifier
            title: Issue title
            description: Issue description
            priority: low, medium, high, urgent
            assignee: User ID to assign (optional)
            velo_task_id: Velo task UUID for linking

        Returns:
            Issue data including issue_id
        """
        payload = {
            "name": title,
            "description": description,
            "priority": priority,
            "state": "todo",  # Default state
            "assignee": assignee,
            "metadata": {
                "velo_task_id": velo_task_id
            }
        }

        response = await self.client.post(
            f"/api/workspaces/{workspace_slug}/projects/{project_id}/issues/",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    async def bulk_create_issues(
        self,
        workspace_slug: str,
        project_id: str,
        issues: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Create multiple issues at once

        Args:
            workspace_slug: Workspace identifier
            project_id: Project identifier
            issues: List of issue dictionaries

        Returns:
            List of created issue data
        """
        results = []
        for issue_data in issues:
            result = await self.create_issue(
                workspace_slug=workspace_slug,
                project_id=project_id,
                title=issue_data.get('title'),
                description=issue_data.get('description', ''),
                priority=issue_data.get('priority', 'medium'),
                assignee=issue_data.get('assignee'),
                velo_task_id=issue_data.get('velo_task_id')
            )
            results.append(result)

        return results

    async def update_issue(
        self,
        workspace_slug: str,
        project_id: str,
        issue_id: str,
        updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update an existing issue

        Args:
            workspace_slug: Workspace identifier
            project_id: Project identifier
            issue_id: Issue identifier
            updates: Dictionary of fields to update

        Returns:
            Updated issue data
        """
        response = await self.client.patch(
            f"/api/workspaces/{workspace_slug}/projects/{project_id}/issues/{issue_id}/",
            json=updates
        )
        response.raise_for_status()
        return response.json()

    async def update_issue_status(
        self,
        workspace_slug: str,
        project_id: str,
        issue_id: str,
        status: str
    ) -> Dict[str, Any]:
        """
        Update issue status

        Args:
            status: todo, in_progress, done, cancelled
        """
        return await self.update_issue(
            workspace_slug,
            project_id,
            issue_id,
            {"state": status}
        )

    async def get_issue(
        self,
        workspace_slug: str,
        project_id: str,
        issue_id: str
    ) -> Dict[str, Any]:
        """Get issue details"""
        response = await self.client.get(
            f"/api/workspaces/{workspace_slug}/projects/{project_id}/issues/{issue_id}/"
        )
        response.raise_for_status()
        return response.json()

    async def list_issues(
        self,
        workspace_slug: str,
        project_id: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List issues in a project

        Args:
            workspace_slug: Workspace identifier
            project_id: Project identifier
            filters: Optional filters (status, priority, assignee, etc.)

        Returns:
            List of issues
        """
        params = filters or {}

        response = await self.client.get(
            f"/api/workspaces/{workspace_slug}/projects/{project_id}/issues/",
            params=params
        )
        response.raise_for_status()
        return response.json()

    # ==============================================================================
    # Comments
    # ==============================================================================

    async def add_issue_comment(
        self,
        workspace_slug: str,
        project_id: str,
        issue_id: str,
        comment: str
    ) -> Dict[str, Any]:
        """Add a comment to an issue"""
        payload = {
            "comment": comment,
            "created_at": datetime.utcnow().isoformat()
        }

        response = await self.client.post(
            f"/api/workspaces/{workspace_slug}/projects/{project_id}/issues/{issue_id}/comments/",
            json=payload
        )
        response.raise_for_status()
        return response.json()

    # ==============================================================================
    # Helper Methods
    # ==============================================================================

    async def setup_velo_workspace(
        self,
        tenant_id: str,
        company_name: str
    ) -> Dict[str, Any]:
        """
        Set up a complete Velo workspace for a tenant

        Args:
            tenant_id: Velo tenant UUID
            company_name: Company display name

        Returns:
            Dictionary with workspace details
        """
        # Create slug from company name
        slug = company_name.lower().replace(' ', '-').replace('_', '-')

        # Create workspace
        workspace = await self.create_workspace(
            name=f"{company_name} - Velo",
            slug=slug,
            tenant_id=tenant_id
        )

        return {
            'workspace_id': workspace.get('id'),
            'workspace_slug': slug,
            'name': workspace.get('name'),
            'created': True
        }

    async def sync_velo_project_to_plane(
        self,
        workspace_slug: str,
        velo_project: Dict[str, Any],
        tasks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Sync a complete Velo project to Plane

        Args:
            workspace_slug: Plane workspace slug
            velo_project: Velo project data
            tasks: List of Velo tasks to create as issues

        Returns:
            Dictionary with project_id and created issue IDs
        """
        # Create project
        project = await self.create_project(
            workspace_slug=workspace_slug,
            name=velo_project['name'],
            description=velo_project.get('description', ''),
            velo_project_id=velo_project['id']
        )

        project_id = project.get('id')

        # Create issues from tasks
        plane_issues = []
        for task in tasks:
            issue_data = {
                'title': task.get('title'),
                'description': task.get('description', ''),
                'priority': task.get('priority', 'medium'),
                'velo_task_id': task.get('id')
            }
            plane_issues.append(issue_data)

        created_issues = await self.bulk_create_issues(
            workspace_slug=workspace_slug,
            project_id=project_id,
            issues=plane_issues
        )

        return {
            'project_id': project_id,
            'issue_ids': [issue.get('id') for issue in created_issues],
            'synced': True
        }


# ==============================================================================
# Usage Example
# ==============================================================================

async def example_usage():
    """Example of how to use PlaneClient"""

    client = PlaneClient()

    try:
        # Set up workspace for a tenant
        workspace = await client.setup_velo_workspace(
            tenant_id="tenant_uuid_123",
            company_name="Bright Tier Solutions"
        )

        print(f"Created workspace: {workspace['workspace_slug']}")

        # Create a project
        project = await client.create_project(
            workspace_slug=workspace['workspace_slug'],
            name="E-Commerce Platform",
            description="Full-featured e-commerce platform",
            velo_project_id="proj_uuid_456"
        )

        print(f"Created project: {project.get('id')}")

        # Create tasks
        tasks = [
            {
                'title': 'Design Database Schema',
                'description': 'Create PostgreSQL schema',
                'priority': 'high'
            },
            {
                'title': 'Build Backend API',
                'description': 'Implement FastAPI endpoints',
                'priority': 'high'
            }
        ]

        issues = await client.bulk_create_issues(
            workspace_slug=workspace['workspace_slug'],
            project_id=project.get('id'),
            issues=tasks
        )

        print(f"Created {len(issues)} issues")

    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(example_usage())
