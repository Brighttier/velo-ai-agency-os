"""
Database Repositories for Velo
Provides clean interface for database operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from .connection import get_db


class TenantRepository:
    """Repository for tenant operations"""

    @staticmethod
    async def create(
        company_name: str,
        subdomain: str,
        plan_tier: str = "free"
    ) -> Dict[str, Any]:
        """Create new tenant"""
        db = get_db()

        query = """
            INSERT INTO tenants (company_name, subdomain, plan_tier)
            VALUES ($1, $2, $3)
            RETURNING id, company_name, subdomain, plan_tier, created_at
        """

        return await db.fetchrow(query, company_name, subdomain, plan_tier)

    @staticmethod
    async def get_by_id(tenant_id: str) -> Optional[Dict[str, Any]]:
        """Get tenant by ID"""
        db = get_db()
        query = "SELECT * FROM tenants WHERE id = $1"
        return await db.fetchrow(query, tenant_id)

    @staticmethod
    async def get_by_subdomain(subdomain: str) -> Optional[Dict[str, Any]]:
        """Get tenant by subdomain"""
        db = get_db()
        query = "SELECT * FROM tenants WHERE subdomain = $1"
        return await db.fetchrow(query, subdomain)


class UserRepository:
    """Repository for user operations"""

    @staticmethod
    async def create(
        tenant_id: str,
        firebase_uid: str,
        email: str,
        display_name: Optional[str] = None,
        role: str = "admin"
    ) -> Dict[str, Any]:
        """Create new user"""
        db = get_db()

        query = """
            INSERT INTO users (tenant_id, firebase_uid, email, display_name, role)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, tenant_id, firebase_uid, email, display_name, role, created_at
        """

        return await db.fetchrow(query, tenant_id, firebase_uid, email, display_name, role)

    @staticmethod
    async def get_by_firebase_uid(firebase_uid: str) -> Optional[Dict[str, Any]]:
        """Get user by Firebase UID"""
        db = get_db()
        query = "SELECT * FROM users WHERE firebase_uid = $1"
        return await db.fetchrow(query, firebase_uid)

    @staticmethod
    async def update_last_login(user_id: str):
        """Update user's last login timestamp"""
        db = get_db()
        query = "UPDATE users SET last_login_at = CURRENT_TIMESTAMP WHERE id = $1"
        await db.execute(query, user_id)


class ProjectRepository:
    """Repository for project operations"""

    @staticmethod
    async def create(
        tenant_id: str,
        user_id: str,
        name: str,
        description: Optional[str] = None,
        status: str = "planning"
    ) -> Dict[str, Any]:
        """Create new project"""
        db = get_db()

        query = """
            INSERT INTO projects (tenant_id, user_id, name, description, status)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id, tenant_id, user_id, name, description, status, created_at, updated_at
        """

        return await db.fetchrow(query, tenant_id, user_id, name, description, status)

    @staticmethod
    async def get_by_id(project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        db = get_db()
        query = "SELECT * FROM projects WHERE id = $1"
        return await db.fetchrow(query, project_id)

    @staticmethod
    async def list_by_tenant(
        tenant_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """List projects for a tenant"""
        db = get_db()

        query = """
            SELECT * FROM projects
            WHERE tenant_id = $1
            ORDER BY created_at DESC
            LIMIT $2 OFFSET $3
        """

        return await db.fetch(query, tenant_id, limit, offset)

    @staticmethod
    async def update_status(project_id: str, status: str):
        """Update project status"""
        db = get_db()
        query = "UPDATE projects SET status = $1 WHERE id = $2"
        await db.execute(query, status, project_id)

    @staticmethod
    async def update_plane_project_id(project_id: str, plane_project_id: str):
        """Link Plane.so project"""
        db = get_db()
        query = "UPDATE projects SET plane_project_id = $1 WHERE id = $2"
        await db.execute(query, plane_project_id, project_id)


class TaskRepository:
    """Repository for task operations"""

    @staticmethod
    async def create(
        project_id: str,
        title: str,
        description: Optional[str] = None,
        status: str = "pending",
        priority: str = "medium",
        assigned_agent: Optional[str] = None,
        plane_issue_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create new task"""
        db = get_db()

        query = """
            INSERT INTO tasks (
                project_id, title, description, status,
                priority, assigned_agent, plane_issue_id
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            RETURNING id, project_id, title, description, status,
                      priority, assigned_agent, plane_issue_id, created_at
        """

        return await db.fetchrow(
            query,
            project_id, title, description, status,
            priority, assigned_agent, plane_issue_id
        )

    @staticmethod
    async def list_by_project(project_id: str) -> List[Dict[str, Any]]:
        """List tasks for a project"""
        db = get_db()
        query = """
            SELECT * FROM tasks
            WHERE project_id = $1
            ORDER BY priority DESC, created_at ASC
        """
        return await db.fetch(query, project_id)

    @staticmethod
    async def update_status(task_id: str, status: str):
        """Update task status"""
        db = get_db()
        query = "UPDATE tasks SET status = $1 WHERE id = $2"
        await db.execute(query, status, task_id)


class AgentActivityRepository:
    """Repository for agent activity logging"""

    @staticmethod
    async def log(
        project_id: str,
        agent_name: str,
        agent_division: str,
        action: str,
        status: str,
        task_id: Optional[str] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict] = None,
        duration_ms: Optional[int] = None
    ) -> Dict[str, Any]:
        """Log agent activity"""
        db = get_db()

        query = """
            INSERT INTO agent_activities (
                project_id, task_id, agent_name, agent_division,
                action, status, error_message, metadata, duration_ms
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
            RETURNING id, project_id, agent_name, action, status, timestamp
        """

        metadata_json = metadata or {}

        return await db.fetchrow(
            query,
            project_id, task_id, agent_name, agent_division,
            action, status, error_message, metadata_json, duration_ms
        )

    @staticmethod
    async def list_by_project(
        project_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get agent activities for a project"""
        db = get_db()

        query = """
            SELECT * FROM agent_activities
            WHERE project_id = $1
            ORDER BY timestamp DESC
            LIMIT $2
        """

        return await db.fetch(query, project_id, limit)


class ArtifactRepository:
    """Repository for artifact operations"""

    @staticmethod
    async def create(
        project_id: str,
        agent_name: str,
        agent_division: str,
        file_name: str,
        file_type: str,
        gcs_path: str,
        created_by: str,
        metadata: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Create artifact record"""
        db = get_db()

        query = """
            INSERT INTO artifacts (
                project_id, agent_name, agent_division, file_name,
                file_type, gcs_path, created_by, metadata
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            RETURNING id, project_id, agent_name, file_name, file_type,
                      gcs_path, version, created_at
        """

        metadata_json = metadata or {}

        return await db.fetchrow(
            query,
            project_id, agent_name, agent_division, file_name,
            file_type, gcs_path, created_by, metadata_json
        )

    @staticmethod
    async def list_by_project(
        project_id: str,
        file_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List artifacts for a project"""
        db = get_db()

        if file_type:
            query = """
                SELECT * FROM artifacts
                WHERE project_id = $1 AND file_type = $2
                ORDER BY created_at DESC
            """
            return await db.fetch(query, project_id, file_type)
        else:
            query = """
                SELECT * FROM artifacts
                WHERE project_id = $1
                ORDER BY created_at DESC
            """
            return await db.fetch(query, project_id)
