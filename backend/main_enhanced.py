"""
Velo Backend - Enhanced with Vertex AI and Database Integration
Firebase Genkit + LangGraph powered AI Agent System
"""

import os
import uuid
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Load environment variables
load_dotenv()

# Import database
from database.connection import get_db, init_db_pool, close_db_pool
from database.repositories import (
    TenantRepository,
    UserRepository,
    ProjectRepository,
    TaskRepository,
    AgentActivityRepository,
    ArtifactRepository
)

# Import Vertex AI
from integrations.vertex_ai import get_vertex_client

# Initialize FastAPI app
app = FastAPI(
    title="Velo API",
    description="AI Agency OS - Backend API with Vertex AI Integration",
    version="2.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ProjectCreateRequest(BaseModel):
    name: str
    description: str

class TenantCreateRequest(BaseModel):
    company_name: str
    user_id: str
    email: str

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

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    """Initialize database pool on startup"""
    print("🚀 Starting Velo API...")
    try:
        await init_db_pool()
        db = get_db()
        await db.initialize()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️  Database initialization failed: {e}")
        print("   Running without database (using mock data)")

@app.on_event("shutdown")
async def shutdown():
    """Close database pool on shutdown"""
    print("👋 Shutting down Velo API...")
    try:
        db = get_db()
        await db.close()
        await close_db_pool()
        print("✅ Database closed")
    except Exception as e:
        print(f"⚠️  Error during shutdown: {e}")

# Planning Phase with Vertex AI
async def run_planning_phase_with_ai(
    project_id: str,
    project_name: str,
    description: str,
    tenant_id: str,
    user_id: str
):
    """
    Real Planning Phase workflow with Vertex AI
    """
    vertex = get_vertex_client()

    try:
        # Step 1: Generate PRD using Vertex AI
        await manager.broadcast({
            "type": "agent_activity",
            "project_id": project_id,
            "agent_name": "Oracle",
            "action": "Analyzing project requirements",
            "status": "in_progress",
            "timestamp": datetime.utcnow().isoformat()
        })

        await AgentActivityRepository.log(
            project_id=project_id,
            agent_name="Oracle",
            agent_division="project_management",
            action="Generating PRD",
            status="started"
        )

        prd_content = await vertex.generate_prd(
            project_name=project_name,
            project_description=description,
            user_requirements=description
        )

        await manager.broadcast({
            "type": "agent_activity",
            "project_id": project_id,
            "agent_name": "Oracle",
            "action": "PRD generated successfully",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        })

        await AgentActivityRepository.log(
            project_id=project_id,
            agent_name="Oracle",
            agent_division="project_management",
            action="Generated PRD",
            status="completed",
            metadata={"prd_length": len(prd_content)}
        )

        # Step 2: Break down into tasks
        await manager.broadcast({
            "type": "agent_activity",
            "project_id": project_id,
            "agent_name": "Neuron",
            "action": "Breaking down PRD into tasks",
            "status": "in_progress",
            "timestamp": datetime.utcnow().isoformat()
        })

        tasks = await vertex.generate_task_breakdown(prd_content, project_name)

        # Step 3: Create tasks in database
        for task_data in tasks:
            await TaskRepository.create(
                project_id=project_id,
                title=task_data["title"],
                description=task_data.get("description", ""),
                priority=task_data.get("priority", "medium"),
                assigned_agent=task_data.get("assigned_agent"),
                status="pending"
            )

        await manager.broadcast({
            "type": "agent_activity",
            "project_id": project_id,
            "agent_name": "Neuron",
            "action": f"Created {len(tasks)} tasks",
            "status": "completed",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Step 4: Update project status
        await ProjectRepository.update_status(project_id, "in_progress")

        # Final broadcast
        await manager.broadcast({
            "type": "project_status",
            "project_id": project_id,
            "status": "ready",
            "message": f"Project '{project_name}' is ready! Planning phase completed with {len(tasks)} tasks.",
            "timestamp": datetime.utcnow().isoformat()
        })

    except Exception as e:
        print(f"Error in planning phase: {e}")
        await manager.broadcast({
            "type": "project_status",
            "project_id": project_id,
            "status": "error",
            "message": f"Planning phase failed: {str(e)}",
            "timestamp": datetime.utcnow().isoformat()
        })


# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time updates
    """
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_json({
                "type": "ping",
                "timestamp": datetime.utcnow().isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        print(f"WebSocket error: {e}")
        manager.disconnect(websocket)


# Tenant endpoints
@app.post("/api/tenant/create")
async def create_tenant(request: TenantCreateRequest):
    """Create a new tenant account"""
    try:
        # Generate subdomain from company name
        subdomain = request.company_name.lower().replace(" ", "-").replace("_", "-")

        # Create tenant
        tenant = await TenantRepository.create(
            company_name=request.company_name,
            subdomain=subdomain,
            plan_tier="free"
        )

        # Create user
        user = await UserRepository.create(
            tenant_id=tenant["id"],
            firebase_uid=request.user_id,
            email=request.email,
            display_name=request.company_name,
            role="admin"
        )

        return {
            "id": tenant["id"],
            "company_name": tenant["company_name"],
            "subdomain": tenant["subdomain"],
            "plan_tier": tenant["plan_tier"],
            "user_id": user["id"],
            "created_at": tenant["created_at"].isoformat()
        }

    except Exception as e:
        print(f"Error creating tenant: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Project endpoints
@app.post("/api/project/create")
async def create_project(request: ProjectCreateRequest, background_tasks: BackgroundTasks):
    """Create a new project and initiate the Planning Phase"""
    try:
        # TODO: Get tenant_id and user_id from JWT token
        # For now, using mock values
        tenant_id = "mock-tenant-id"
        user_id = "mock-user-id"

        # Create project in database
        project = await ProjectRepository.create(
            tenant_id=tenant_id,
            user_id=user_id,
            name=request.name,
            description=request.description,
            status="planning"
        )

        project_id = project["id"]

        # Broadcast project creation
        await manager.broadcast({
            "type": "project_created",
            "project_id": project_id,
            "project_name": request.name,
            "status": "planning",
            "timestamp": datetime.utcnow().isoformat()
        })

        # Start planning phase with Vertex AI in background
        background_tasks.add_task(
            run_planning_phase_with_ai,
            project_id,
            request.name,
            request.description,
            tenant_id,
            user_id
        )

        return {
            "id": project_id,
            "name": request.name,
            "description": request.description,
            "status": "planning",
            "created_at": project["created_at"].isoformat(),
            "message": "Project created. AI agents are planning your project. Connect to WebSocket for real-time updates."
        }

    except Exception as e:
        print(f"Error creating project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/project/list")
async def list_projects(tenant_id: Optional[str] = None):
    """Get all projects for tenant"""
    try:
        # TODO: Get tenant_id from JWT
        tenant_id = tenant_id or "mock-tenant-id"

        projects = await ProjectRepository.list_by_tenant(tenant_id)

        return {
            "projects": [
                {
                    "id": p["id"],
                    "name": p["name"],
                    "description": p["description"],
                    "status": p["status"],
                    "created_at": p["created_at"].isoformat(),
                    "updated_at": p["updated_at"].isoformat()
                }
                for p in projects
            ]
        }

    except Exception as e:
        print(f"Error listing projects: {e}")
        return {"projects": []}


@app.get("/api/project/{project_id}")
async def get_project(project_id: str):
    """Get project details"""
    try:
        project = await ProjectRepository.get_by_id(project_id)

        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get tasks
        tasks = await TaskRepository.list_by_project(project_id)

        # Get agent activities
        activities = await AgentActivityRepository.list_by_project(project_id, limit=50)

        return {
            "id": project["id"],
            "name": project["name"],
            "description": project["description"],
            "status": project["status"],
            "created_at": project["created_at"].isoformat(),
            "updated_at": project["updated_at"].isoformat(),
            "tasks": [
                {
                    "id": t["id"],
                    "title": t["title"],
                    "status": t["status"],
                    "priority": t["priority"],
                    "assigned_agent": t["assigned_agent"]
                }
                for t in tasks
            ],
            "recent_activities": [
                {
                    "agent_name": a["agent_name"],
                    "action": a["action"],
                    "status": a["status"],
                    "timestamp": a["timestamp"].isoformat()
                }
                for a in activities
            ]
        }

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error getting project: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")

    print(f"🚀 Velo API v2.0 starting on {host}:{port}")
    print(f"📝 Docs available at http://localhost:{port}/docs")
    print(f"🤖 Vertex AI Integration: Enabled")
    print(f"💾 Database Integration: Enabled")

    uvicorn.run("main_enhanced:app", host=host, port=port, reload=True)
