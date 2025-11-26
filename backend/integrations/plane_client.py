"""
Plane.so Integration for Velo
Provides interface to Plane API for project management
"""

import os
from typing import Dict, List, Any, Optional
from plane import PlaneClient
import hmac
import hashlib


# Initialize Plane configuration
PLANE_API_KEY = os.getenv("PLANE_API_KEY", "")
PLANE_WORKSPACE_SLUG = os.getenv("PLANE_WORKSPACE_SLUG", "")
PLANE_BASE_URL = os.getenv("PLANE_BASE_URL", "https://api.plane.so")
PLANE_WEBHOOK_SECRET = os.getenv("PLANE_WEBHOOK_SECRET", "")


class VeloPlaneClient:
    """Client for interacting with Plane.so"""

    def __init__(self):
        """Initialize Plane client"""
        if not PLANE_API_KEY:
            print("⚠️  WARNING: PLANE_API_KEY not configured")
            self.client = None
        else:
            self.client = PlaneClient(
                api_key=PLANE_API_KEY,
                base_url=PLANE_BASE_URL
            )

        self.workspace_slug = PLANE_WORKSPACE_SLUG

    def is_configured(self) -> bool:
        """Check if Plane is properly configured"""
        return self.client is not None and bool(self.workspace_slug)

    # ========================================================================
    # PROJECTS
    # ========================================================================

    def list_projects(self) -> List[Dict[str, Any]]:
        """
        List all projects in workspace

        Returns:
            List of project dictionaries
        """
        if not self.is_configured():
            return []

        try:
            response = self.client.projects.list(self.workspace_slug)
            return response if response else []
        except Exception as e:
            print(f"Error listing Plane projects: {e}")
            return []

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get project details

        Args:
            project_id: Plane project ID

        Returns:
            Project dictionary or None
        """
        if not self.is_configured():
            return None

        try:
            return self.client.projects.get(
                self.workspace_slug,
                project_id
            )
        except Exception as e:
            print(f"Error getting Plane project: {e}")
            return None

    def create_project(
        self,
        name: str,
        description: str = "",
        identifier: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new project

        Args:
            name: Project name
            description: Project description
            identifier: Short identifier (e.g., "PROJ")

        Returns:
            Created project dictionary or None
        """
        if not self.is_configured():
            return None

        try:
            project_data = {
                "name": name,
                "description": description,
            }
            if identifier:
                project_data["identifier"] = identifier

            return self.client.projects.create(
                self.workspace_slug,
                project_data
            )
        except Exception as e:
            print(f"Error creating Plane project: {e}")
            return None

    def update_project(
        self,
        project_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update project

        Args:
            project_id: Plane project ID
            updates: Dictionary of fields to update

        Returns:
            Updated project or None
        """
        if not self.is_configured():
            return None

        try:
            return self.client.projects.update(
                self.workspace_slug,
                project_id,
                updates
            )
        except Exception as e:
            print(f"Error updating Plane project: {e}")
            return None

    # ========================================================================
    # ISSUES (TASKS)
    # ========================================================================

    def list_issues(
        self,
        project_id: str,
        filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        List issues in a project

        Args:
            project_id: Plane project ID
            filters: Optional filters (state, priority, assignee, etc.)

        Returns:
            List of issue dictionaries
        """
        if not self.is_configured():
            return []

        try:
            response = self.client.issues.list(
                self.workspace_slug,
                project_id,
                filters=filters
            )
            return response if response else []
        except Exception as e:
            print(f"Error listing Plane issues: {e}")
            return []

    def get_issue(self, project_id: str, issue_id: str) -> Optional[Dict[str, Any]]:
        """Get issue details"""
        if not self.is_configured():
            return None

        try:
            return self.client.issues.get(
                self.workspace_slug,
                project_id,
                issue_id
            )
        except Exception as e:
            print(f"Error getting Plane issue: {e}")
            return None

    def create_issue(
        self,
        project_id: str,
        title: str,
        description: str = "",
        priority: str = "medium",
        assignee_id: str = None,
        state_id: str = None,
        labels: List[str] = None,
        start_date: str = None,
        target_date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new issue

        Args:
            project_id: Plane project ID
            title: Issue title
            description: Issue description
            priority: Priority (urgent, high, medium, low, none)
            assignee_id: User ID to assign
            state_id: State ID
            labels: List of label IDs
            start_date: Start date (YYYY-MM-DD)
            target_date: Due date (YYYY-MM-DD)

        Returns:
            Created issue or None
        """
        if not self.is_configured():
            return None

        try:
            issue_data = {
                "name": title,
                "description_html": description,
                "priority": priority
            }

            if assignee_id:
                issue_data["assignees"] = [assignee_id]
            if state_id:
                issue_data["state"] = state_id
            if labels:
                issue_data["labels"] = labels
            if start_date:
                issue_data["start_date"] = start_date
            if target_date:
                issue_data["target_date"] = target_date

            return self.client.issues.create(
                self.workspace_slug,
                project_id,
                issue_data
            )
        except Exception as e:
            print(f"Error creating Plane issue: {e}")
            return None

    def update_issue(
        self,
        project_id: str,
        issue_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update issue"""
        if not self.is_configured():
            return None

        try:
            return self.client.issues.update(
                self.workspace_slug,
                project_id,
                issue_id,
                updates
            )
        except Exception as e:
            print(f"Error updating Plane issue: {e}")
            return None

    def delete_issue(self, project_id: str, issue_id: str) -> bool:
        """Delete issue"""
        if not self.is_configured():
            return False

        try:
            self.client.issues.delete(
                self.workspace_slug,
                project_id,
                issue_id
            )
            return True
        except Exception as e:
            print(f"Error deleting Plane issue: {e}")
            return False

    # ========================================================================
    # CYCLES (SPRINTS)
    # ========================================================================

    def list_cycles(self, project_id: str) -> List[Dict[str, Any]]:
        """List cycles in project"""
        if not self.is_configured():
            return []

        try:
            response = self.client.cycles.list(
                self.workspace_slug,
                project_id
            )
            return response if response else []
        except Exception as e:
            print(f"Error listing Plane cycles: {e}")
            return []

    def create_cycle(
        self,
        project_id: str,
        name: str,
        start_date: str,
        end_date: str,
        description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new cycle

        Args:
            project_id: Plane project ID
            name: Cycle name
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            description: Cycle description

        Returns:
            Created cycle or None
        """
        if not self.is_configured():
            return None

        try:
            cycle_data = {
                "name": name,
                "start_date": start_date,
                "end_date": end_date,
                "description": description
            }

            return self.client.cycles.create(
                self.workspace_slug,
                project_id,
                cycle_data
            )
        except Exception as e:
            print(f"Error creating Plane cycle: {e}")
            return None

    def add_issue_to_cycle(
        self,
        project_id: str,
        cycle_id: str,
        issue_id: str
    ) -> bool:
        """Add issue to cycle"""
        if not self.is_configured():
            return False

        try:
            self.client.cycle_issues.create(
                self.workspace_slug,
                project_id,
                cycle_id,
                {"issue": issue_id}
            )
            return True
        except Exception as e:
            print(f"Error adding issue to cycle: {e}")
            return False

    # ========================================================================
    # MODULES
    # ========================================================================

    def list_modules(self, project_id: str) -> List[Dict[str, Any]]:
        """List modules in project"""
        if not self.is_configured():
            return []

        try:
            response = self.client.modules.list(
                self.workspace_slug,
                project_id
            )
            return response if response else []
        except Exception as e:
            print(f"Error listing Plane modules: {e}")
            return []

    def create_module(
        self,
        project_id: str,
        name: str,
        description: str = "",
        start_date: str = None,
        target_date: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new module

        Args:
            project_id: Plane project ID
            name: Module name
            description: Module description
            start_date: Start date (YYYY-MM-DD)
            target_date: Target date (YYYY-MM-DD)

        Returns:
            Created module or None
        """
        if not self.is_configured():
            return None

        try:
            module_data = {
                "name": name,
                "description": description
            }
            if start_date:
                module_data["start_date"] = start_date
            if target_date:
                module_data["target_date"] = target_date

            return self.client.modules.create(
                self.workspace_slug,
                project_id,
                module_data
            )
        except Exception as e:
            print(f"Error creating Plane module: {e}")
            return None

    def add_issue_to_module(
        self,
        project_id: str,
        module_id: str,
        issue_id: str
    ) -> bool:
        """Add issue to module"""
        if not self.is_configured():
            return False

        try:
            self.client.module_issues.create(
                self.workspace_slug,
                project_id,
                module_id,
                {"issue": issue_id}
            )
            return True
        except Exception as e:
            print(f"Error adding issue to module: {e}")
            return False

    # ========================================================================
    # PAGES (DOCUMENTATION)
    # ========================================================================

    def list_pages(self, project_id: str) -> List[Dict[str, Any]]:
        """List pages in project"""
        if not self.is_configured():
            return []

        try:
            response = self.client.pages.list(
                self.workspace_slug,
                project_id
            )
            return response if response else []
        except Exception as e:
            print(f"Error listing Plane pages: {e}")
            return []

    def create_page(
        self,
        project_id: str,
        name: str,
        description: str = ""
    ) -> Optional[Dict[str, Any]]:
        """
        Create a new page

        Args:
            project_id: Plane project ID
            name: Page name
            description: Page content (HTML)

        Returns:
            Created page or None
        """
        if not self.is_configured():
            return None

        try:
            page_data = {
                "name": name,
                "description_html": description
            }

            return self.client.pages.create(
                self.workspace_slug,
                project_id,
                page_data
            )
        except Exception as e:
            print(f"Error creating Plane page: {e}")
            return None

    # ========================================================================
    # STATES (WORKFLOW)
    # ========================================================================

    def list_states(self, project_id: str) -> List[Dict[str, Any]]:
        """List workflow states in project"""
        if not self.is_configured():
            return []

        try:
            response = self.client.states.list(
                self.workspace_slug,
                project_id
            )
            return response if response else []
        except Exception as e:
            print(f"Error listing Plane states: {e}")
            return []

    # ========================================================================
    # LABELS
    # ========================================================================

    def list_labels(self, project_id: str) -> List[Dict[str, Any]]:
        """List labels in project"""
        if not self.is_configured():
            return []

        try:
            response = self.client.labels.list(
                self.workspace_slug,
                project_id
            )
            return response if response else []
        except Exception as e:
            print(f"Error listing Plane labels: {e}")
            return []

    # ========================================================================
    # WEBHOOKS
    # ========================================================================

    @staticmethod
    def verify_webhook_signature(payload: str, signature: str) -> bool:
        """
        Verify webhook signature

        Args:
            payload: Request body as string
            signature: X-Plane-Signature header value

        Returns:
            True if signature is valid
        """
        if not PLANE_WEBHOOK_SECRET:
            print("⚠️  WARNING: PLANE_WEBHOOK_SECRET not configured")
            return False

        computed = hmac.new(
            PLANE_WEBHOOK_SECRET.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(computed, signature)


# Singleton instance
_plane_client = None


def get_plane_client() -> VeloPlaneClient:
    """Get or create Plane client instance"""
    global _plane_client
    if _plane_client is None:
        _plane_client = VeloPlaneClient()
    return _plane_client
