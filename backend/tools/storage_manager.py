"""
Google Cloud Storage Manager
Handles artifact storage, versioning, and retrieval
"""

import os
import io
import json
from typing import Dict, List, Any, Optional, BinaryIO
from datetime import datetime, timedelta
from google.cloud import storage
from google.cloud.exceptions import NotFound


class StorageManager:
    """
    Manager for Google Cloud Storage operations
    Handles artifacts, versioning, and downloads
    """

    def __init__(
        self,
        project_id: Optional[str] = None,
        bucket_name: Optional[str] = None
    ):
        self.project_id = project_id or os.getenv("GOOGLE_CLOUD_PROJECT")
        self.bucket_name = bucket_name or os.getenv("FIREBASE_STORAGE_BUCKET", "velo-artifacts")

        if not self.project_id:
            raise ValueError("GOOGLE_CLOUD_PROJECT environment variable or project_id parameter required")

        # Initialize storage client
        self.client = storage.Client(project=self.project_id)
        self.bucket = self.client.bucket(self.bucket_name)

    # ==============================================================================
    # Artifact Upload
    # ==============================================================================

    def upload_artifact(
        self,
        tenant_id: str,
        project_id: str,
        artifact_id: str,
        content: str,
        filename: str,
        content_type: str = "text/plain",
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload an artifact to GCS

        Args:
            tenant_id: Tenant UUID for partitioning
            project_id: Project UUID
            artifact_id: Artifact UUID
            content: File content (string or bytes)
            filename: Original filename
            content_type: MIME type
            metadata: Additional metadata

        Returns:
            GCS path (gs://bucket/path/to/file)
        """
        # Create path with tenant partitioning
        blob_path = f"{tenant_id}/{project_id}/artifacts/{artifact_id}/{filename}"

        blob = self.bucket.blob(blob_path)

        # Set metadata
        blob.metadata = metadata or {}
        blob.metadata.update({
            "tenant_id": tenant_id,
            "project_id": project_id,
            "artifact_id": artifact_id,
            "uploaded_at": datetime.utcnow().isoformat()
        })

        # Upload content
        if isinstance(content, str):
            blob.upload_from_string(content, content_type=content_type)
        else:
            blob.upload_from_string(content, content_type=content_type)

        return f"gs://{self.bucket_name}/{blob_path}"

    def upload_file(
        self,
        tenant_id: str,
        project_id: str,
        artifact_id: str,
        file_obj: BinaryIO,
        filename: str,
        content_type: str = "application/octet-stream",
        metadata: Optional[Dict[str, str]] = None
    ) -> str:
        """
        Upload a file object to GCS

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID
            artifact_id: Artifact UUID
            file_obj: File-like object
            filename: Original filename
            content_type: MIME type
            metadata: Additional metadata

        Returns:
            GCS path
        """
        blob_path = f"{tenant_id}/{project_id}/artifacts/{artifact_id}/{filename}"

        blob = self.bucket.blob(blob_path)
        blob.metadata = metadata or {}
        blob.metadata.update({
            "tenant_id": tenant_id,
            "project_id": project_id,
            "artifact_id": artifact_id,
            "uploaded_at": datetime.utcnow().isoformat()
        })

        blob.upload_from_file(file_obj, content_type=content_type)

        return f"gs://{self.bucket_name}/{blob_path}"

    # ==============================================================================
    # Artifact Download
    # ==============================================================================

    def download_artifact(self, gcs_path: str) -> bytes:
        """
        Download an artifact by GCS path

        Args:
            gcs_path: Full GCS path (gs://bucket/path/to/file)

        Returns:
            File content as bytes
        """
        # Parse GCS path
        if not gcs_path.startswith("gs://"):
            raise ValueError("Invalid GCS path format")

        path = gcs_path.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(path)

        try:
            return blob.download_as_bytes()
        except NotFound:
            raise FileNotFoundError(f"Artifact not found: {gcs_path}")

    def download_artifact_as_string(self, gcs_path: str) -> str:
        """
        Download artifact as string (for text files)

        Args:
            gcs_path: Full GCS path

        Returns:
            File content as string
        """
        content = self.download_artifact(gcs_path)
        return content.decode('utf-8')

    def get_artifact_url(
        self,
        gcs_path: str,
        expiration_hours: int = 24
    ) -> str:
        """
        Generate a signed URL for temporary access

        Args:
            gcs_path: Full GCS path
            expiration_hours: URL validity period

        Returns:
            Signed URL
        """
        path = gcs_path.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(path)

        expiration = timedelta(hours=expiration_hours)

        url = blob.generate_signed_url(
            version="v4",
            expiration=expiration,
            method="GET"
        )

        return url

    # ==============================================================================
    # Artifact Listing
    # ==============================================================================

    def list_project_artifacts(
        self,
        tenant_id: str,
        project_id: str
    ) -> List[Dict[str, Any]]:
        """
        List all artifacts for a project

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID

        Returns:
            List of artifact metadata
        """
        prefix = f"{tenant_id}/{project_id}/artifacts/"
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)

        artifacts = []
        for blob in blobs:
            artifacts.append({
                "name": blob.name,
                "size": blob.size,
                "content_type": blob.content_type,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "updated": blob.updated.isoformat() if blob.updated else None,
                "gcs_path": f"gs://{self.bucket_name}/{blob.name}",
                "metadata": blob.metadata or {}
            })

        return artifacts

    # ==============================================================================
    # Version Management
    # ==============================================================================

    def upload_artifact_version(
        self,
        tenant_id: str,
        project_id: str,
        artifact_id: str,
        version: int,
        content: str,
        filename: str,
        content_type: str = "text/plain"
    ) -> str:
        """
        Upload a specific version of an artifact

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID
            artifact_id: Artifact UUID
            version: Version number
            content: File content
            filename: Original filename
            content_type: MIME type

        Returns:
            GCS path for this version
        """
        blob_path = f"{tenant_id}/{project_id}/artifacts/{artifact_id}/versions/v{version}/{filename}"

        blob = self.bucket.blob(blob_path)
        blob.metadata = {
            "tenant_id": tenant_id,
            "project_id": project_id,
            "artifact_id": artifact_id,
            "version": str(version),
            "uploaded_at": datetime.utcnow().isoformat()
        }

        if isinstance(content, str):
            blob.upload_from_string(content, content_type=content_type)
        else:
            blob.upload_from_string(content, content_type=content_type)

        return f"gs://{self.bucket_name}/{blob_path}"

    def list_artifact_versions(
        self,
        tenant_id: str,
        project_id: str,
        artifact_id: str
    ) -> List[Dict[str, Any]]:
        """
        List all versions of an artifact

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID
            artifact_id: Artifact UUID

        Returns:
            List of version metadata
        """
        prefix = f"{tenant_id}/{project_id}/artifacts/{artifact_id}/versions/"
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)

        versions = []
        for blob in blobs:
            versions.append({
                "name": blob.name,
                "version": blob.metadata.get("version") if blob.metadata else None,
                "size": blob.size,
                "created": blob.time_created.isoformat() if blob.time_created else None,
                "gcs_path": f"gs://{self.bucket_name}/{blob.name}"
            })

        # Sort by version number
        versions.sort(key=lambda x: int(x["version"] or 0), reverse=True)

        return versions

    # ==============================================================================
    # ZIP Package Generation
    # ==============================================================================

    def create_project_export(
        self,
        tenant_id: str,
        project_id: str,
        project_name: str
    ) -> str:
        """
        Create a ZIP export of all project artifacts

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID
            project_name: Project name for the ZIP

        Returns:
            GCS path to the generated ZIP file
        """
        import zipfile
        from io import BytesIO

        # List all project artifacts
        artifacts = self.list_project_artifacts(tenant_id, project_id)

        # Create ZIP in memory
        zip_buffer = BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Organize by folder structure
            folders = {
                "01_Strategy": [],
                "02_Architecture": [],
                "03_Source_Code": [],
                "04_Quality_Assurance": [],
                "05_Manuals": []
            }

            # Categorize artifacts
            for artifact in artifacts:
                filename = artifact["name"].split("/")[-1]
                gcs_path = artifact["gcs_path"]
                content = self.download_artifact(gcs_path)

                # Determine folder based on filename
                if "prd" in filename.lower() or "requirements" in filename.lower():
                    folder = "01_Strategy"
                elif "architecture" in filename.lower() or "diagram" in filename.lower():
                    folder = "02_Architecture"
                elif any(ext in filename for ext in [".ts", ".tsx", ".py", ".js", ".jsx"]):
                    folder = "03_Source_Code"
                elif "test" in filename.lower() or "qa" in filename.lower():
                    folder = "04_Quality_Assurance"
                else:
                    folder = "05_Manuals"

                # Add to ZIP
                zip_file.writestr(f"{folder}/{filename}", content)

            # Add README
            readme = f"""# {project_name} - Export Package

This package contains all artifacts generated by Velo AI Agents.

## Contents

- 01_Strategy/ - Product requirements and analysis
- 02_Architecture/ - System design and diagrams
- 03_Source_Code/ - Generated codebase
- 04_Quality_Assurance/ - Test reports and results
- 05_Manuals/ - User guides and documentation

Generated by Velo - The AI Agency OS
Date: {datetime.utcnow().isoformat()}
"""
            zip_file.writestr("README.md", readme)

        # Upload ZIP to GCS
        zip_buffer.seek(0)
        zip_path = f"{tenant_id}/{project_id}/exports/{project_name}_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.zip"

        blob = self.bucket.blob(zip_path)
        blob.upload_from_file(zip_buffer, content_type="application/zip")

        return f"gs://{self.bucket_name}/{zip_path}"

    # ==============================================================================
    # Cleanup
    # ==============================================================================

    def delete_artifact(self, gcs_path: str) -> bool:
        """
        Delete an artifact from GCS

        Args:
            gcs_path: Full GCS path

        Returns:
            True if deleted successfully
        """
        path = gcs_path.replace(f"gs://{self.bucket_name}/", "")
        blob = self.bucket.blob(path)

        try:
            blob.delete()
            return True
        except NotFound:
            return False

    def delete_project_artifacts(
        self,
        tenant_id: str,
        project_id: str
    ) -> int:
        """
        Delete all artifacts for a project

        Args:
            tenant_id: Tenant UUID
            project_id: Project UUID

        Returns:
            Number of artifacts deleted
        """
        prefix = f"{tenant_id}/{project_id}/"
        blobs = self.client.list_blobs(self.bucket_name, prefix=prefix)

        count = 0
        for blob in blobs:
            blob.delete()
            count += 1

        return count


# ==============================================================================
# Usage Example
# ==============================================================================

def example_usage():
    """Example of how to use StorageManager"""

    manager = StorageManager()

    # Upload an artifact
    gcs_path = manager.upload_artifact(
        tenant_id="tenant_123",
        project_id="proj_456",
        artifact_id="art_789",
        content="# Product Requirements Document\n\n...",
        filename="PRD.md",
        content_type="text/markdown",
        metadata={"agent": "Oracle", "type": "prd"}
    )
    print(f"Uploaded to: {gcs_path}")

    # Download artifact
    content = manager.download_artifact_as_string(gcs_path)
    print(f"Downloaded: {content[:100]}...")

    # Generate signed URL
    url = manager.get_artifact_url(gcs_path, expiration_hours=24)
    print(f"Temporary URL: {url[:100]}...")

    # List project artifacts
    artifacts = manager.list_project_artifacts("tenant_123", "proj_456")
    print(f"Found {len(artifacts)} artifacts")

    # Create project export
    zip_path = manager.create_project_export(
        tenant_id="tenant_123",
        project_id="proj_456",
        project_name="ECommerce Platform"
    )
    print(f"Export created: {zip_path}")


if __name__ == "__main__":
    example_usage()
