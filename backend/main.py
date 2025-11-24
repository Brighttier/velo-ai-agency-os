"""
Velo Backend - Main Entry Point
Firebase Genkit + LangGraph powered AI Agent System
"""

import os
import uuid
import asyncio
import json
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Firestore database
from database.firestore_db import get_db

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

# Firestore database instance
db = get_db()

# In-memory task lookup (for backwards compatibility with existing websocket code)
# TODO: Migrate to Firestore queries
tasks_lookup: Dict[str, str] = {}  # task_id -> project_id mapping

# Request/Response Models
class ProjectCreateRequest(BaseModel):
    name: str
    description: str

class ProjectUpdateRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None

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
    # No initialization needed - Firestore handles creation dynamically

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

        # If Oracle just finished generating PRD, create the artifact
        if step["agent"] == "Oracle" and "Generating" in step["action"]:
            artifact_id = f"art_{uuid.uuid4().hex[:8]}"
            prd_content = f"""# Product Requirements Document: {project_name}

## Project Overview
{description}

## Goals & Objectives
- Build a scalable and maintainable solution
- Deliver high-quality user experience
- Ensure security and performance

## Core Features
1. User Authentication & Authorization
2. Database Architecture
3. API Development
4. Frontend UI/UX
5. Payment Processing
6. Testing & Quality Assurance

## Technical Stack
- Backend: Python/FastAPI
- Frontend: Next.js/React
- Database: PostgreSQL
- Deployment: Google Cloud Platform

## Success Criteria
- All core features implemented
- 90%+ test coverage
- Performance benchmarks met
- Security audit passed

## Timeline
- Planning Phase: Complete
- Development Phase: 2-4 weeks
- QA & Testing: 1 week
- Deployment: 3 days

Generated by Oracle AI Agent
"""

            artifact_data = {
                "project_id": project_id,
                "agent_name": "Oracle",
                "file_type": "prd",
                "file_name": f"{project_name.replace(' ', '_')}_PRD.md",
                "content": prd_content
            }
            artifact = db.create_artifact(artifact_data)

            # Broadcast artifact creation
            await manager.broadcast({
                "type": "artifact_created",
                "project_id": project_id,
                "artifact": artifact,
                "timestamp": datetime.utcnow().isoformat()
            })

        # If this is the Neuron step, create tasks
        if step["agent"] == "Neuron":
            sample_tasks = [
                {"title": "Design Database Schema", "description": "Create entity relationship diagram and define database tables", "assigned_agent": "Atlas"},
                {"title": "Build User Authentication", "description": "Implement login, signup, and password reset functionality", "assigned_agent": "Pixel"},
                {"title": "Create API Endpoints", "description": "Build RESTful API endpoints for core features", "assigned_agent": "Byte"},
                {"title": "Design UI Components", "description": "Create reusable UI components following design system", "assigned_agent": "Pixel"},
                {"title": "Implement Payment Integration", "description": "Integrate payment gateway for transactions", "assigned_agent": "Atlas"},
                {"title": "Write Unit Tests", "description": "Add comprehensive test coverage for all modules", "assigned_agent": "Judge"},
            ]

            for task_data in sample_tasks:
                task_create_data = {
                    "project_id": project_id,
                    "title": task_data["title"],
                    "description": task_data["description"],
                    "status": "todo",
                    "assigned_agent": task_data["assigned_agent"]
                }
                task = db.create_task(task_create_data)

                # Store in lookup for backwards compatibility
                tasks_lookup[task["id"]] = project_id

                # Broadcast task creation
                await manager.broadcast({
                    "type": "task_created",
                    "project_id": project_id,
                    "task": task,
                    "timestamp": datetime.utcnow().isoformat()
                })

                # Small delay between task creations for visual effect
                await asyncio.sleep(0.3)

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

    # Update project with task count
    tasks_list = db.list_tasks(project_id)
    total_tasks = len(tasks_list)
    db.update_project(project_id, {
        "total_tasks": total_tasks,
        "status": "ready"
    })

    # Final status update
    await manager.broadcast({
        "type": "project_status",
        "project_id": project_id,
        "status": "ready",
        "message": f"Project '{project_name}' is ready! {total_tasks} tasks created.",
        "timestamp": datetime.utcnow().isoformat()
    })

async def run_task_execution(task_id: str, project_id: str, task: Dict[str, Any]):
    """
    Simulate task execution with Build & QA Loop
    This demonstrates the human-in-the-loop workflow
    """
    agent_name = task.get("assigned_agent", "Agent")
    task_title = task["title"]

    # Update task status to in_progress
    db.update_task(task_id, {
        "status": "in_progress"
    })
    task = db.get_task(task_id)

    # Broadcast start
    await manager.broadcast({
        "type": "task_execution_started",
        "project_id": project_id,
        "task_id": task_id,
        "agent_name": agent_name,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Step 1: Agent analyzes task
    await manager.broadcast({
        "type": "agent_activity",
        "project_id": project_id,
        "agent_name": agent_name,
        "action": f"Analyzing task: {task_title}",
        "status": "working",
        "timestamp": datetime.utcnow().isoformat()
    })
    await asyncio.sleep(2)

    # Step 2: Agent generates code/output
    await manager.broadcast({
        "type": "agent_activity",
        "project_id": project_id,
        "agent_name": agent_name,
        "action": f"Generating solution for: {task_title}",
        "status": "working",
        "timestamp": datetime.utcnow().isoformat()
    })
    await asyncio.sleep(3)

    # Step 3: Code Judge reviews (simulated QA)
    await manager.broadcast({
        "type": "agent_activity",
        "project_id": project_id,
        "agent_name": "Judge",
        "action": f"Reviewing {agent_name}'s work",
        "status": "working",
        "timestamp": datetime.utcnow().isoformat()
    })
    await asyncio.sleep(2)

    # Generate simulated code output
    code_output = f"""// Generated by {agent_name}
// Task: {task_title}

function implement_{task_title.lower().replace(' ', '_')}() {{
  // TODO: Implementation
  console.log('Task completed: {task_title}')
  return {{
    status: 'success',
    message: 'Implementation ready for review'
  }}
}}

// Unit tests
describe('{task_title}', () => {{
  it('should work correctly', () => {{
    const result = implement_{task_title.lower().replace(' ', '_')}()
    expect(result.status).toBe('success')
  }})
}})
"""

    # Create artifact for the task output
    artifact_data = {
        "project_id": project_id,
        "task_id": task_id,
        "agent_name": agent_name,
        "file_type": "code",
        "file_name": f"{task_title.replace(' ', '_').lower()}.js",
        "content": code_output
    }

    # Store artifact in Firestore
    artifact = db.create_artifact(artifact_data)
    artifact_id = artifact["id"]

    # Update task with artifact reference
    db.update_task(task_id, {
        "status": "pending_review",
        "artifact_id": artifact_id
    })
    task = db.get_task(task_id)

    # Broadcast completion and request human approval
    await manager.broadcast({
        "type": "task_execution_complete",
        "project_id": project_id,
        "task_id": task_id,
        "task": task,
        "artifact": artifact,
        "message": f"{agent_name} completed the task. Please review and approve or reject.",
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
    # Create project in Firestore
    project_data = {
        "name": request.name,
        "description": request.description,
        "status": "planning",
        "progress": 0,
        "agents": 0,
        "total_tasks": 0,
        "completed_tasks": 0
    }

    created_project = db.create_project(project_data)
    project_id = created_project["id"]
    created_at = created_project["created_at"]

    # Broadcast project creation
    await manager.broadcast({
        "type": "project_created",
        "project_id": project_id,
        "project_name": request.name,
        "status": "planning",
        "timestamp": created_at
    })

    # Start planning phase in background
    background_tasks.add_task(run_planning_phase, project_id, request.name, request.description)

    # Return immediately
    return {
        "id": project_id,
        "name": request.name,
        "description": request.description,
        "status": "planning",
        "created_at": created_at,
        "message": "Project created. Planning phase initiated. Connect to WebSocket for real-time updates."
    }

@app.get("/api/project/list")
async def list_projects():
    """Get all projects for the current tenant"""
    # Get all projects from Firestore (already sorted by created_at DESC)
    projects_list = db.list_projects()
    return {"projects": projects_list}

@app.get("/api/project/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    project = db.get_project(project_id)
    if project:
        return project
    else:
        raise HTTPException(status_code=404, detail="Project not found")

@app.patch("/api/project/{project_id}")
async def update_project(project_id: str, request: ProjectUpdateRequest):
    """Update project details"""
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Prepare update data
    update_data = {}
    if request.name is not None:
        update_data['name'] = request.name
    if request.description is not None:
        update_data['description'] = request.description

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Update in Firestore
    db.update_project(project_id, update_data)

    # Return updated project
    updated_project = db.get_project(project_id)
    return updated_project

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
async def execute_task(task_id: str, background_tasks: BackgroundTasks):
    """
    Execute a specific task using the Build & QA Loop workflow
    This simulates agent work that will require human approval
    """
    # Get the task from Firestore (which contains project_id)
    task = db.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Extract project_id from the task
    project_id = task.get("project_id")

    if not project_id:
        raise HTTPException(status_code=400, detail="Task missing project_id")

    # Store in lookup for backwards compatibility
    tasks_lookup[task_id] = project_id

    # Start execution in background
    background_tasks.add_task(run_task_execution, task_id, project_id, task)

    return {
        "task_id": task_id,
        "status": "executing",
        "message": "Task execution started"
    }

@app.post("/api/task/{task_id}/approve")
async def approve_task(task_id: str):
    """
    Human approves the task output
    """
    # Find the task
    project_id = tasks_lookup.get(task_id)

    if not project_id:
        raise HTTPException(status_code=404, detail="Task not found in lookup")

    task = db.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task status in Firestore
    db.update_task(task_id, {"status": "completed"})

    # Broadcast approval
    await manager.broadcast({
        "type": "task_approved",
        "project_id": project_id,
        "task_id": task_id,
        "task": task,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "task_id": task_id,
        "status": "approved",
        "message": "Task approved and marked as complete"
    }

@app.post("/api/task/{task_id}/reject")
async def reject_task(task_id: str, background_tasks: BackgroundTasks):
    """
    Human rejects the task output, agent will retry
    """
    # Find the task
    project_id = tasks_lookup.get(task_id)

    if not project_id:
        raise HTTPException(status_code=404, detail="Task not found in lookup")

    task = db.get_task(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # Update task to retry
    retry_count = task.get("retry_count", 0) + 1
    db.update_task(task_id, {
        "status": "pending",
        "retry_count": retry_count
    })

    # Get updated task
    task = db.get_task(task_id)

    # Broadcast rejection
    await manager.broadcast({
        "type": "task_rejected",
        "project_id": project_id,
        "task_id": task_id,
        "task": task,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Re-execute the task
    background_tasks.add_task(run_task_execution, task_id, project_id, task)

    return {
        "task_id": task_id,
        "status": "retrying",
        "message": "Task rejected, agent will retry"
    }

@app.get("/api/task/list")
async def list_tasks(project_id: str):
    """Get all tasks for a project"""
    # Get tasks from Firestore
    tasks_list = db.list_tasks(project_id)
    return {"tasks": tasks_list}

# Agent endpoints
@app.get("/api/agent/list")
async def list_agents():
    """Get all available agents"""
    try:
        # Load agents from JSON file
        agents_file_path = os.path.join(os.path.dirname(__file__), 'data', 'agents.json')
        with open(agents_file_path, 'r') as f:
            agents_data = json.load(f)
        return {"agents": agents_data}
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail="Agents data file not found")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Invalid agents data format")

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
    # Get artifacts from Firestore
    artifacts_list = db.list_artifacts(project_id)
    return {"artifacts": artifacts_list}

@app.get("/api/artifact/{artifact_id}")
async def get_artifact(artifact_id: str):
    """Get artifact content"""
    # Get artifact from Firestore
    artifact = db.get_artifact(artifact_id)

    if not artifact:
        raise HTTPException(status_code=404, detail="Artifact not found")

    return artifact

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
