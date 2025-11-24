"""
Velo Backend - Main Entry Point
Firebase Genkit + LangGraph powered AI Agent System
"""

import os
import uuid
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Velo API",
    description="AI Agency OS - Backend API",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print(f"✅ WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        print(f"❌ WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """Broadcast message to all connected clients"""
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                print(f"Failed to send to connection: {e}")
                disconnected.append(connection)

        # Remove disconnected clients
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)

manager = ConnectionManager()

# Request/Response Models
class ProjectCreateRequest(BaseModel):
    name: str
    description: str

class ProjectResponse(BaseModel):
    id: str
    name: str
    description: str
    status: str
    created_at: str

class TaskExecuteRequest(BaseModel):
    task_id: str

class AgentResponse(BaseModel):
    id: str
    name: str
    role: str
    tagline: str
    division: str
    status: str

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    Clients can subscribe to project updates, agent activities, and task status changes
    """
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            # Echo back a ping response
            await websocket.send_json({
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)

# Health check endpoint
@app.get("/")
async def root():
    return {
        "service": "Velo API",
        "status": "running",
        "version": "1.0.0",
        "websocket_connections": len(manager.active_connections)
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "websocket_connections": len(manager.active_connections)
    }

# Background task for planning phase
async def run_planning_phase(project_id: str, project_name: str, description: str):
    """
    Simulate the Planning Phase workflow with real-time progress updates
    In production, this would call the LangGraph Planning workflow
    """
    steps = [
        {"agent": "Oracle", "action": "Analyzing project requirements", "duration": 2},
        {"agent": "Oracle", "action": "Generating comprehensive PRD", "duration": 3},
        {"agent": "Neuron", "action": "Breaking down features into tasks", "duration": 2},
        {"agent": "Atlas", "action": "Creating Plane project workspace", "duration": 1},
        {"agent": "Atlas", "action": "Syncing tasks to Plane", "duration": 2},
    ]

    for i, step in enumerate(steps):
        # Broadcast agent activity
        await manager.broadcast({
            "type": "agent_activity",
            "project_id": project_id,
            "agent_name": step["agent"],
            "action": step["action"],
            "status": "in_progress",
            "timestamp": datetime.utcnow().isoformat(),
            "progress": int((i / len(steps)) * 100)
        })

        # Simulate work
        await asyncio.sleep(step["duration"])

        # Broadcast completion
        await manager.broadcast({
            "type": "agent_activity",
            "project_id": project_id,
            "agent_name": step["agent"],
            "action": step["action"],
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat(),
            "progress": int(((i + 1) / len(steps)) * 100)
        })

    # Final status update
    await manager.broadcast({
        "type": "project_status",
        "project_id": project_id,
        "status": "ready",
        "message": f"Project '{project_name}' is ready! Planning phase completed.",
        "timestamp": datetime.utcnow().isoformat()
    })

# Project endpoints
@app.post("/api/project/create")
async def create_project(request: ProjectCreateRequest, background_tasks: BackgroundTasks):
    """
    Create a new project and initiate the Planning Phase.
    This will:
    1. Generate a PRD using the Product Manager agent
    2. Create a Plane project
    3. Break down tasks and create Plane issues

    Returns immediately with project_id and starts planning in background
    """
    # Generate unique project ID
    project_id = f"proj_{uuid.uuid4().hex[:12]}"

    # Broadcast project creation
    await manager.broadcast({
        "type": "project_created",
        "project_id": project_id,
        "project_name": request.name,
        "status": "planning",
        "timestamp": datetime.utcnow().isoformat()
    })

    # Start planning phase in background
    background_tasks.add_task(run_planning_phase, project_id, request.name, request.description)

    # Return immediately
    return {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "status": "planning",
        "created_at": datetime.utcnow().isoformat(),
        "message": "Project created. Planning phase initiated. Connect to WebSocket for real-time updates."
    }

@app.get("/api/project/list")
async def list_projects():
    """Get all projects for the current tenant"""
    # TODO: Implement database query
    return {
        "projects": [
            {
                "id": "proj_123",
                "name": "E-Commerce Platform",
                "status": "in_progress",
                "progress": 65,
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]
    }

@app.get("/api/project/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    # TODO: Implement database query
    return {
        "id": project_id,
        "name": "E-Commerce Platform",
        "description": "A full-featured e-commerce platform",
        "status": "in_progress",
        "created_at": "2024-01-15T10:00:00Z"
    }

@app.post("/api/project/{project_id}/export")
async def export_project(project_id: str):
    """
    Export project as a ZIP package with all artifacts
    """
    # TODO: Implement ZIP generation from GCS
    return {
        "download_url": f"https://storage.googleapis.com/velo-artifacts/{project_id}/export.zip",
        "expires_at": "2024-01-20T10:00:00Z"
    }

# Task endpoints
@app.post("/api/task/{task_id}/execute")
async def execute_task(task_id: str):
    """
    Execute a specific task using the Build & QA Loop workflow
    """
    # TODO: Implement LangGraph Build & QA workflow
    return {
        "task_id": task_id,
        "status": "executing",
        "message": "Task execution started"
    }

@app.get("/api/task/list")
async def list_tasks(project_id: str):
    """Get all tasks for a project"""
    # TODO: Query Plane API
    return {
        "tasks": [
            {
                "id": "task_1",
                "title": "Design Database Schema",
                "status": "completed",
                "assigned_agent": "Atlas"
            },
            {
                "id": "task_2",
                "title": "Build User Authentication",
                "status": "in_progress",
                "assigned_agent": "Pixel"
            }
        ]
    }

# Agent endpoints
@app.get("/api/agent/list")
async def list_agents():
    """Get all available agents"""
    # TODO: Return from agents registry
    return {
        "agents": [
            {
                "id": "pixel",
                "name": "Pixel",
                "role": "Frontend Developer",
                "tagline": "The UI Craftsman",
                "division": "engineering",
                "status": "idle"
            },
            {
                "id": "atlas",
                "name": "Atlas",
                "role": "Backend Architect",
                "tagline": "The Infrastructure Oracle",
                "division": "engineering",
                "status": "working"
            }
        ]
    }

@app.get("/api/agent/{agent_name}")
async def get_agent(agent_name: str):
    """Get details for a specific agent"""
    # TODO: Return from agents registry
    return {
        "id": agent_name,
        "name": agent_name.capitalize(),
        "status": "idle",
        "recent_tasks": []
    }

@app.get("/api/agent/activity")
async def get_agent_activity(project_id: str):
    """Get agent activity for a project"""
    # TODO: Query activity logs
    return {
        "activities": [
            {
                "agent_name": "Atlas",
                "action": "Generated database schema",
                "status": "completed",
                "timestamp": "2024-01-15T10:30:00Z"
            }
        ]
    }

# Artifact endpoints
@app.get("/api/artifact/list")
async def list_artifacts(project_id: str):
    """Get all artifacts for a project"""
    # TODO: Query from database and GCS
    return {
        "artifacts": [
            {
                "id": "art_1",
                "project_id": project_id,
                "agent_name": "Oracle",
                "file_type": "prd",
                "file_name": "Product_Requirements.md",
                "created_at": "2024-01-15T10:00:00Z"
            }
        ]
    }

@app.get("/api/artifact/{artifact_id}")
async def get_artifact(artifact_id: str):
    """Get artifact content"""
    # TODO: Fetch from GCS
    return {
        "id": artifact_id,
        "content": "# Product Requirements Document\n\n...",
        "metadata": {}
    }

@app.get("/api/artifact/{artifact_id}/versions")
async def get_artifact_versions(artifact_id: str):
    """Get version history for an artifact"""
    # TODO: Query version table
    return {
        "versions": []
    }

@app.post("/api/artifact/{artifact_id}/comment")
async def add_artifact_comment(artifact_id: str, content: str):
    """Add a comment to an artifact"""
    # TODO: Insert into comments table
    return {
        "comment_id": "comment_123",
        "message": "Comment added successfully"
    }

# Tenant endpoints
@app.post("/api/tenant/create")
async def create_tenant(request: dict):
    """
    Create a new tenant account
    Called during signup process
    """
    # TODO: Verify Firebase token from Authorization header
    # TODO: Create tenant in database with user_id and company_name

    tenant_id = f"tenant_{uuid.uuid4().hex[:12]}"

    return {
        "id": tenant_id,
        "company_name": request.get("company_name"),
        "user_id": request.get("user_id"),
        "plan_tier": "free",
        "created_at": datetime.utcnow().isoformat()
    }

@app.get("/api/tenant")
async def get_tenant():
    """Get current tenant information"""
    # TODO: Get from auth context
    return {
        "id": "tenant_123",
        "company_name": "Bright Tier Solutions",
        "plan_tier": "enterprise"
    }

@app.get("/api/tenant/usage")
async def get_tenant_usage():
    """Get usage statistics for billing"""
    # TODO: Query usage_logs table
    return {
        "current_period": {
            "projects": 12,
            "tokens_used": 150000,
            "agents_active": 8
        }
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")

    print(f"🚀 Velo API starting on {host}:{port}")
    print(f"📝 Docs available at http://localhost:{port}/docs")

    uvicorn.run("main:app", host=host, port=port, reload=True)
