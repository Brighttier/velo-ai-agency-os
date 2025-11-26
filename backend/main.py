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

# Gemini AI integration (replaces Vertex AI)
from integrations.gemini_ai import get_gemini_client

# Plane.so integration
from tools.plane_client import PlaneClient

# Load environment variables
load_dotenv()

# Helper function to get agents for project type
def get_agents_for_project_type(project_type: str) -> List[Dict[str, str]]:
    """
    Get appropriate agent workflow based on project type

    Returns list of agents with their roles for the project
    """
    if project_type == 'marketing':
        return [
            {"agent": "Nexus", "role": "Strategy & Planning"},
            {"agent": "Rhythm", "role": "TikTok Content"},
            {"agent": "Prism", "role": "Instagram Content"},
            {"agent": "Quill", "role": "Copywriting"},
            {"agent": "Rocket", "role": "Growth & Optimization"},
        ]
    elif project_type == 'design':
        return [
            {"agent": "Oracle", "role": "Requirements & Planning"},
            {"agent": "Aurora", "role": "UI/UX Design"},
            {"agent": "Pixel", "role": "Frontend Implementation"},
            {"agent": "Sherlock", "role": "Design QA"},
        ]
    elif project_type == 'business':
        return [
            {"agent": "Oracle", "role": "Strategy & Analysis"},
            {"agent": "Neuron", "role": "Data Analysis"},
            {"agent": "Quill", "role": "Documentation"},
        ]
    elif project_type == 'content':
        return [
            {"agent": "Oracle", "role": "Content Planning"},
            {"agent": "Quill", "role": "Content Creation"},
            {"agent": "Rocket", "role": "Distribution Strategy"},
        ]
    else:  # software (default)
        return [
            {"agent": "Oracle", "role": "Requirements & Planning"},
            {"agent": "Neuron", "role": "Architecture"},
            {"agent": "Atlas", "role": "Implementation"},
            {"agent": "Judge", "role": "Code Review"},
            {"agent": "Forge", "role": "Deployment"},
        ]

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
    # Step 1: Detect project type
    gemini_client = get_gemini_client()
    try:
        project_type = await gemini_client.detect_project_type(project_name, description)
        print(f"🎯 Detected project type: {project_type}")
    except Exception as e:
        print(f"⚠️ Project type detection failed: {e}")
        project_type = 'software'  # Default fallback

    # Store project type in database
    db.update_project(project_id, {"project_type": project_type})

    # Get appropriate agents for this project type
    agents_workflow = get_agents_for_project_type(project_type)

    # Dynamic steps based on project type
    steps = [
        {"agent": "Oracle", "action": "Analyzing project requirements", "duration": 2},
        {"agent": "Oracle", "action": f"Generating comprehensive {project_type.title()} PRD", "duration": 3},
        {"agent": agents_workflow[1]["agent"] if len(agents_workflow) > 1 else "Neuron", "action": "Breaking down into actionable tasks", "duration": 2},
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

            # Generate PRD using Gemini AI
            try:
                gemini_client = get_gemini_client()
                prd_content = await gemini_client.generate_prd(
                    project_name=project_name,
                    project_description=description,
                    user_requirements=description
                )
            except Exception as e:
                error_msg = f"Gemini AI PRD generation failed: {str(e)}"
                print(f"⚠️ {error_msg}")

                # Broadcast error to frontend
                await manager.broadcast({
                    "type": "ai_generation_warning",
                    "project_id": project_id,
                    "message": "AI generation unavailable. Using basic template. Please configure GEMINI_API_KEY for full features.",
                    "details": str(e)[:200],  # Truncate long errors
                    "timestamp": datetime.utcnow().isoformat()
                })

                # Context-aware fallback template
                prd_content = f"""# Product Requirements Document: {project_name}

## Project Overview
{description}

## Project Objectives
This document outlines the requirements and plan for: {project_name}

## Key Deliverables
- Research and planning phase
- Strategy development
- Implementation and execution
- Testing and quality assurance
- Launch and deployment

## Success Criteria
- All requirements met according to project scope
- Quality standards achieved
- Timeline and budget maintained

## Next Steps
1. Detailed requirements gathering
2. Resource allocation
3. Timeline establishment
4. Stakeholder approval

---
*Note: This is a basic template. AI-powered PRD generation is currently unavailable.*
*Generated by Oracle AI Agent (Template Mode)*
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

        # If this is the task breakdown step, create tasks
        if "Breaking down" in step["action"]:
            # Generate task breakdown using Gemini AI
            try:
                gemini_client = get_gemini_client()
                # Get the PRD content from the artifact we just created
                artifacts_list = db.list_artifacts(project_id)
                prd_artifact = next((a for a in artifacts_list if a.get("file_type") == "prd"), None)
                prd_text = prd_artifact.get("content", description) if prd_artifact else description

                sample_tasks = await gemini_client.generate_task_breakdown(
                    prd_content=prd_text,
                    project_name=project_name
                )
            except Exception as e:
                error_msg = f"Gemini AI task breakdown failed: {str(e)}"
                print(f"⚠️ {error_msg}")

                # Broadcast error to frontend
                await manager.broadcast({
                    "type": "ai_generation_warning",
                    "project_id": project_id,
                    "message": "AI task generation unavailable. Using basic task templates.",
                    "details": str(e)[:200],
                    "timestamp": datetime.utcnow().isoformat()
                })

                # Context-aware fallback tasks based on project type
                if project_type == 'marketing':
                    sample_tasks = [
                        {
                            "title": f"Campaign Strategy for {project_name}",
                            "description": f"Develop comprehensive marketing strategy for: {description}",
                            "assigned_agent": "Nexus",
                            "priority": "high",
                            "dependencies": [],
                            "estimated_hours": 8
                        },
                        {
                            "title": f"TikTok Content Creation",
                            "description": f"Create viral TikTok content strategy and scripts",
                            "assigned_agent": "Rhythm",
                            "priority": "high",
                            "dependencies": [f"Campaign Strategy for {project_name}"],
                            "estimated_hours": 12
                        },
                        {
                            "title": f"Instagram Content Creation",
                            "description": f"Develop Instagram visual content and posting schedule",
                            "assigned_agent": "Prism",
                            "priority": "high",
                            "dependencies": [f"Campaign Strategy for {project_name}"],
                            "estimated_hours": 10
                        },
                        {
                            "title": f"Copywriting and Captions",
                            "description": f"Write compelling copy and captions for all platforms",
                            "assigned_agent": "Quill",
                            "priority": "medium",
                            "dependencies": ["TikTok Content Creation", "Instagram Content Creation"],
                            "estimated_hours": 8
                        },
                        {
                            "title": f"Growth & Optimization",
                            "description": f"Implement growth tactics and A/B testing",
                            "assigned_agent": "Rocket",
                            "priority": "medium",
                            "dependencies": ["Copywriting and Captions"],
                            "estimated_hours": 6
                        }
                    ]
                else:  # software (default)
                    sample_tasks = [
                        {
                            "title": f"Research and Planning for {project_name}",
                            "description": f"Conduct thorough research and create detailed plan for: {description}",
                            "assigned_agent": agents_workflow[0]["agent"],
                            "priority": "high",
                            "dependencies": [],
                            "estimated_hours": 8
                        },
                        {
                            "title": f"Strategy Development",
                            "description": f"Develop comprehensive strategy and approach for implementing: {project_name}",
                            "assigned_agent": agents_workflow[1]["agent"] if len(agents_workflow) > 1 else "Neuron",
                            "priority": "high",
                            "dependencies": [f"Research and Planning for {project_name}"],
                            "estimated_hours": 12
                        },
                        {
                            "title": f"Core Implementation",
                            "description": f"Execute main implementation work for: {description}",
                            "assigned_agent": agents_workflow[2]["agent"] if len(agents_workflow) > 2 else "Atlas",
                            "priority": "high",
                            "dependencies": ["Strategy Development"],
                            "estimated_hours": 16
                        },
                        {
                            "title": f"Quality Assurance",
                            "description": f"Review, test and validate all deliverables for {project_name}",
                            "assigned_agent": agents_workflow[3]["agent"] if len(agents_workflow) > 3 else "Judge",
                            "priority": "medium",
                            "dependencies": ["Core Implementation"],
                            "estimated_hours": 8
                        }
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

    # Get project type for context-aware content generation
    project = db.get_project(project_id)
    project_type = project.get("project_type", "software") if project else "software"
    project_name = project.get("name", "Project") if project else "Project"

    # Generate content output using Gemini AI (project-aware)
    try:
        gemini_client = get_gemini_client()
        code_output = await gemini_client.generate_content_for_task(
            task_title=task_title,
            task_description=task.get("description", ""),
            agent_name=agent_name.lower(),
            project_type=project_type,
            project_context=f"{project_name}: {project.get('description', '')}" if project else "",
            context={
                "project_id": project_id,
                "task_id": task_id
            }
        )
    except Exception as e:
        error_msg = f"Gemini AI content generation failed: {str(e)}"
        print(f"⚠️ {error_msg}")

        # Broadcast error to frontend
        await manager.broadcast({
            "type": "ai_generation_warning",
            "project_id": project_id,
            "task_id": task_id,
            "message": f"AI {project_type} content generation unavailable. Using template output.",
            "details": str(e)[:200],
            "timestamp": datetime.utcnow().isoformat()
        })

        # Context-aware fallback template
        code_output = f"""// Generated by {agent_name}
// Task: {task_title}
// Description: {task.get("description", "No description provided")}

/**
 * Implementation placeholder for: {task_title}
 *
 * This is a template output because AI generation is currently unavailable.
 * Please enable Vertex AI API for full code generation capabilities.
 *
 * Next steps:
 * 1. Review the task requirements
 * 2. Implement the functionality described above
 * 3. Add comprehensive error handling
 * 4. Write unit tests
 * 5. Document the implementation
 */

// TODO: Implement {task_title}
function implement() {{
  // Add your implementation here
  console.log('Task: {task_title}')

  return {{
    status: 'pending_implementation',
    message: 'Template generated - requires manual implementation'
  }}
}}

// TODO: Add unit tests
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

@app.delete("/api/project/{project_id}")
async def delete_project(project_id: str):
    """
    Delete project and all its related data (tasks, artifacts, etc.)
    """
    project = db.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Delete all related tasks
    tasks_list = db.list_tasks(project_id)
    for task in tasks_list:
        db.delete_task(task["id"])

    # Delete all related artifacts
    artifacts_list = db.list_artifacts(project_id)
    for artifact in artifacts_list:
        db.delete_artifact(artifact["id"])

    # Delete the project itself
    db.delete_project(project_id)

    # Broadcast deletion
    await manager.broadcast({
        "type": "project_deleted",
        "project_id": project_id,
        "timestamp": datetime.utcnow().isoformat()
    })

    return {
        "message": "Project and all related data deleted successfully",
        "project_id": project_id
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

# ==============================================================================
# PLANE.SO INTEGRATION ENDPOINTS
# ==============================================================================

# Initialize Plane client (async context manager)
plane_client = None
PLANE_WORKSPACE_SLUG = os.getenv("PLANE_WORKSPACE_SLUG", "velo")

async def get_plane_client() -> PlaneClient:
    """Get or create Plane client"""
    global plane_client
    if plane_client is None:
        try:
            plane_client = PlaneClient()
        except ValueError as e:
            print(f"⚠️  WARNING: Plane client not configured: {e}")
            return None
    return plane_client

# Plane Projects
@app.get("/api/plane/projects")
async def plane_list_projects():
    """List all Plane projects"""
    client = await get_plane_client()
    if not client:
        raise HTTPException(status_code=503, detail="Plane integration not configured")

    projects = await client.list_projects(PLANE_WORKSPACE_SLUG)
    return {"projects": projects}

@app.get("/api/plane/projects/{project_id}")
async def plane_get_project(project_id: str):
    """Get Plane project details"""
    project = plane_client.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@app.post("/api/plane/projects")
async def plane_create_project(request: Dict[str, Any]):
    """Create new Plane project"""
    name = request.get("name")
    description = request.get("description", "")
    identifier = request.get("identifier")

    if not name:
        raise HTTPException(status_code=400, detail="Project name is required")

    project = plane_client.create_project(name, description, identifier)
    if not project:
        raise HTTPException(status_code=500, detail="Failed to create project")

    return project

@app.patch("/api/plane/projects/{project_id}")
async def plane_update_project(project_id: str, updates: Dict[str, Any]):
    """Update Plane project"""
    project = plane_client.update_project(project_id, updates)
    if not project:
        raise HTTPException(status_code=500, detail="Failed to update project")
    return project

# Plane Issues
@app.get("/api/plane/projects/{project_id}/issues")
async def plane_list_issues(project_id: str, state: str = None, priority: str = None):
    """List issues in Plane project"""
    filters = {}
    if state:
        filters["state"] = state
    if priority:
        filters["priority"] = priority

    issues = plane_client.list_issues(project_id, filters)
    return {"issues": issues}

@app.get("/api/plane/projects/{project_id}/issues/{issue_id}")
async def plane_get_issue(project_id: str, issue_id: str):
    """Get Plane issue details"""
    issue = plane_client.get_issue(project_id, issue_id)
    if not issue:
        raise HTTPException(status_code=404, detail="Issue not found")
    return issue

@app.post("/api/plane/projects/{project_id}/issues")
async def plane_create_issue(project_id: str, request: Dict[str, Any]):
    """Create new Plane issue"""
    title = request.get("title")
    if not title:
        raise HTTPException(status_code=400, detail="Issue title is required")

    issue = plane_client.create_issue(
        project_id=project_id,
        title=title,
        description=request.get("description", ""),
        priority=request.get("priority", "medium"),
        assignee_id=request.get("assignee_id"),
        state_id=request.get("state_id"),
        labels=request.get("labels"),
        start_date=request.get("start_date"),
        target_date=request.get("target_date")
    )

    if not issue:
        raise HTTPException(status_code=500, detail="Failed to create issue")

    return issue

@app.patch("/api/plane/projects/{project_id}/issues/{issue_id}")
async def plane_update_issue(project_id: str, issue_id: str, updates: Dict[str, Any]):
    """Update Plane issue"""
    issue = plane_client.update_issue(project_id, issue_id, updates)
    if not issue:
        raise HTTPException(status_code=500, detail="Failed to update issue")
    return issue

@app.delete("/api/plane/projects/{project_id}/issues/{issue_id}")
async def plane_delete_issue(project_id: str, issue_id: str):
    """Delete Plane issue"""
    success = plane_client.delete_issue(project_id, issue_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete issue")
    return {"message": "Issue deleted successfully"}

# Plane Cycles
@app.get("/api/plane/projects/{project_id}/cycles")
async def plane_list_cycles(project_id: str):
    """List cycles in Plane project"""
    cycles = plane_client.list_cycles(project_id)
    return {"cycles": cycles}

@app.post("/api/plane/projects/{project_id}/cycles")
async def plane_create_cycle(project_id: str, request: Dict[str, Any]):
    """Create new Plane cycle"""
    name = request.get("name")
    start_date = request.get("start_date")
    end_date = request.get("end_date")

    if not all([name, start_date, end_date]):
        raise HTTPException(status_code=400, detail="Name, start_date, and end_date are required")

    cycle = plane_client.create_cycle(
        project_id=project_id,
        name=name,
        start_date=start_date,
        end_date=end_date,
        description=request.get("description", "")
    )

    if not cycle:
        raise HTTPException(status_code=500, detail="Failed to create cycle")

    return cycle

@app.post("/api/plane/projects/{project_id}/cycles/{cycle_id}/issues")
async def plane_add_issue_to_cycle(project_id: str, cycle_id: str, request: Dict[str, Any]):
    """Add issue to cycle"""
    issue_id = request.get("issue_id")
    if not issue_id:
        raise HTTPException(status_code=400, detail="issue_id is required")

    success = plane_client.add_issue_to_cycle(project_id, cycle_id, issue_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add issue to cycle")

    return {"message": "Issue added to cycle successfully"}

# Plane Modules
@app.get("/api/plane/projects/{project_id}/modules")
async def plane_list_modules(project_id: str):
    """List modules in Plane project"""
    modules = plane_client.list_modules(project_id)
    return {"modules": modules}

@app.post("/api/plane/projects/{project_id}/modules")
async def plane_create_module(project_id: str, request: Dict[str, Any]):
    """Create new Plane module"""
    name = request.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Module name is required")

    module = plane_client.create_module(
        project_id=project_id,
        name=name,
        description=request.get("description", ""),
        start_date=request.get("start_date"),
        target_date=request.get("target_date")
    )

    if not module:
        raise HTTPException(status_code=500, detail="Failed to create module")

    return module

@app.post("/api/plane/projects/{project_id}/modules/{module_id}/issues")
async def plane_add_issue_to_module(project_id: str, module_id: str, request: Dict[str, Any]):
    """Add issue to module"""
    issue_id = request.get("issue_id")
    if not issue_id:
        raise HTTPException(status_code=400, detail="issue_id is required")

    success = plane_client.add_issue_to_module(project_id, module_id, issue_id)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to add issue to module")

    return {"message": "Issue added to module successfully"}

# Plane Pages
@app.get("/api/plane/projects/{project_id}/pages")
async def plane_list_pages(project_id: str):
    """List pages in Plane project"""
    pages = plane_client.list_pages(project_id)
    return {"pages": pages}

@app.post("/api/plane/projects/{project_id}/pages")
async def plane_create_page(project_id: str, request: Dict[str, Any]):
    """Create new Plane page"""
    name = request.get("name")
    if not name:
        raise HTTPException(status_code=400, detail="Page name is required")

    page = plane_client.create_page(
        project_id=project_id,
        name=name,
        description=request.get("description", "")
    )

    if not page:
        raise HTTPException(status_code=500, detail="Failed to create page")

    return page

# Plane States & Labels
@app.get("/api/plane/projects/{project_id}/states")
async def plane_list_states(project_id: str):
    """List workflow states in Plane project"""
    states = plane_client.list_states(project_id)
    return {"states": states}

@app.get("/api/plane/projects/{project_id}/labels")
async def plane_list_labels(project_id: str):
    """List labels in Plane project"""
    labels = plane_client.list_labels(project_id)
    return {"labels": labels}

# Plane Webhooks
@app.post("/api/plane/webhooks")
async def plane_webhook_handler(request: Dict[str, Any]):
    """Handle Plane webhooks"""
    from fastapi import Request as FastAPIRequest
    import json

    # Get raw request body and signature
    # Note: This is a simplified version - in production, you'd get headers from the actual request
    signature = request.get("signature", "")
    payload = json.dumps(request.get("payload", {}))

    # Verify signature
    if not plane_client.verify_webhook_signature(payload, signature):
        raise HTTPException(status_code=401, detail="Invalid webhook signature")

    event_type = request.get("event")
    action = request.get("action")
    data = request.get("data", {})

    # Broadcast webhook event to connected clients
    await manager.broadcast({
        "type": "plane_webhook",
        "event": event_type,
        "action": action,
        "data": data,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Log webhook event
    print(f"📨 Plane Webhook: {event_type}.{action}")

    return {"status": "received"}

async def check_gemini_ai_health():
    """Check if Gemini AI is properly configured and accessible"""
    try:
        gemini_client = get_gemini_client()
        # Try a simple test generation with minimal tokens
        test_result = await gemini_client.generate_content(
            prompt="Say 'OK'",
            temperature=0.1,
            max_tokens=10
        )
        print("✅ Gemini AI is properly configured and accessible")
        print(f"   Test response: {test_result}")
        return True
    except Exception as e:
        print("⚠️  WARNING: Gemini AI is not available")
        print(f"   Error: {str(e)[:150]}")
        print("   → AI-powered content generation will use fallback templates")
        print("   → Get API key: https://aistudio.google.com/app/apikey")
        print("   → Set environment variable: export GEMINI_API_KEY='your-key-here'")
        return False

@app.on_event("startup")
async def startup_event():
    """Run startup tasks"""
    print("🔍 Checking Gemini AI configuration...")
    await check_gemini_ai_health()
    print("✅ Velo backend initialized")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("API_PORT", 8000))
    host = os.getenv("API_HOST", "0.0.0.0")

    print(f"🚀 Velo API starting on {host}:{port}")
    print(f"📝 Docs available at http://localhost:{port}/docs")

    uvicorn.run("main:app", host=host, port=port, reload=True)
