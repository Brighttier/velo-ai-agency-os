"""
Firestore Database Layer for Velo
Replaces PostgreSQL with Firebase Firestore for simpler, serverless data persistence
"""

import firebase_admin
from firebase_admin import credentials, firestore
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

# Initialize Firebase Admin SDK
def initialize_firestore():
    """Initialize Firestore client"""
    try:
        # Check if already initialized
        firebase_admin.get_app()
    except ValueError:
        # Initialize with default credentials (works in Cloud Functions/Cloud Run)
        # For local development, set GOOGLE_APPLICATION_CREDENTIALS env var
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            cred = credentials.Certificate(os.getenv('GOOGLE_APPLICATION_CREDENTIALS'))
            firebase_admin.initialize_app(cred)
        else:
            # Use default credentials (works in GCP environment)
            firebase_admin.initialize_app()

    return firestore.client()


class FirestoreDB:
    """Firestore database operations"""

    def __init__(self):
        self.db = initialize_firestore()

    # ==================== PROJECT OPERATIONS ====================

    def create_project(self, project_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new project"""
        project_ref = self.db.collection('projects').document()

        # Add timestamps if not present
        now = datetime.utcnow().isoformat()
        project_data.setdefault('created_at', now)
        project_data.setdefault('updated_at', now)
        project_data['id'] = project_ref.id

        project_ref.set(project_data)
        return project_data

    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        doc = self.db.collection('projects').document(project_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def update_project(self, project_id: str, data: Dict[str, Any]) -> None:
        """Update project fields"""
        # Add updated_at timestamp
        data['updated_at'] = datetime.utcnow()
        self.db.collection('projects').document(project_id).update(data)

    def list_projects(self, tenant_id: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """List all projects"""
        query = self.db.collection('projects')

        if tenant_id:
            query = query.where('tenant_id', '==', tenant_id)

        query = query.order_by('created_at', direction=firestore.Query.DESCENDING).limit(limit)

        docs = query.stream()
        return [doc.to_dict() for doc in docs]

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> None:
        """Update project fields"""
        updates['updated_at'] = datetime.utcnow().isoformat()
        self.db.collection('projects').document(project_id).update(updates)

    def delete_project(self, project_id: str) -> None:
        """Delete a project"""
        self.db.collection('projects').document(project_id).delete()

    # ==================== TASK OPERATIONS ====================

    def create_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new task"""
        task_ref = self.db.collection('tasks').document()

        now = datetime.utcnow().isoformat()
        task_data.setdefault('created_at', now)
        task_data.setdefault('updated_at', now)
        task_data['id'] = task_ref.id

        task_ref.set(task_data)
        return task_data

    def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get task by ID"""
        doc = self.db.collection('tasks').document(task_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def list_tasks(self, project_id: str) -> List[Dict[str, Any]]:
        """List all tasks for a project"""
        docs = self.db.collection('tasks') \
            .where('project_id', '==', project_id) \
            .order_by('created_at') \
            .stream()
        return [doc.to_dict() for doc in docs]

    def update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        """Update task fields"""
        updates['updated_at'] = datetime.utcnow().isoformat()
        self.db.collection('tasks').document(task_id).update(updates)

    def delete_task(self, task_id: str) -> None:
        """Delete a task"""
        self.db.collection('tasks').document(task_id).delete()

    # ==================== ARTIFACT OPERATIONS ====================

    def create_artifact(self, artifact_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new artifact"""
        artifact_ref = self.db.collection('artifacts').document()

        now = datetime.utcnow().isoformat()
        artifact_data.setdefault('created_at', now)
        artifact_data['id'] = artifact_ref.id

        artifact_ref.set(artifact_data)
        return artifact_data

    def get_artifact(self, artifact_id: str) -> Optional[Dict[str, Any]]:
        """Get artifact by ID"""
        doc = self.db.collection('artifacts').document(artifact_id).get()
        if doc.exists:
            return doc.to_dict()
        return None

    def list_artifacts(self, project_id: str) -> List[Dict[str, Any]]:
        """List all artifacts for a project"""
        docs = self.db.collection('artifacts') \
            .where('project_id', '==', project_id) \
            .order_by('created_at', direction=firestore.Query.DESCENDING) \
            .stream()
        return [doc.to_dict() for doc in docs]

    def delete_artifact(self, artifact_id: str) -> None:
        """Delete an artifact"""
        self.db.collection('artifacts').document(artifact_id).delete()

    # ==================== ACTIVITY OPERATIONS ====================

    def create_activity(self, activity_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new activity log entry"""
        activity_ref = self.db.collection('activities').document()

        activity_data.setdefault('timestamp', datetime.utcnow().isoformat())
        activity_data['id'] = activity_ref.id

        activity_ref.set(activity_data)
        return activity_data

    def list_activities(self, project_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """List recent activities for a project"""
        docs = self.db.collection('activities') \
            .where('project_id', '==', project_id) \
            .order_by('timestamp', direction=firestore.Query.DESCENDING) \
            .limit(limit) \
            .stream()
        return [doc.to_dict() for doc in docs]


# Global instance
_db_instance = None

def get_db() -> FirestoreDB:
    """Get or create Firestore database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = FirestoreDB()
    return _db_instance
