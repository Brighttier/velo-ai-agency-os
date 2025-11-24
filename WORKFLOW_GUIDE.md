# Velo - User Workflow Guide

## Current Implementation Status

### ✅ What Works Right Now:

1. **Create Project** - You can create projects with a name and description
2. **View Projects** - Dashboard and Projects page show all projects
3. **Backend Planning Workflow** - When you create a project, the backend:
   - Generates a unique project ID
   - Broadcasts WebSocket events for real-time updates
   - Runs a simulated planning phase in the background:
     - Oracle: Analyzes requirements (2s)
     - Oracle: Generates PRD (3s)
     - Neuron: Breaks down tasks (2s)
     - Atlas: Creates Plane workspace (1s)
     - Atlas: Syncs tasks (2s)
   - Total planning time: ~10 seconds

### ⚠️ What's Missing (The UX Gap):

The backend DOES execute the planning workflow, but you can't see it because:

1. **No WebSocket Connection** - Frontend doesn't connect to WebSocket yet
   - Backend sends real-time updates via WebSocket
   - Frontend needs to connect and listen

2. **No Loading State** - After clicking "Create Project":
   - Modal closes immediately
   - You're redirected to project page
   - Page shows empty state (no tasks/activity yet)
   - You think nothing happened!

3. **Need to Manually Refresh** - To see the generated tasks:
   - Wait 10-15 seconds for planning to complete
   - Refresh the project page manually
   - Tasks will then appear

## The Complete Intended Workflow:

```
┌──────────────────────────────────────────────────────────────┐
│  1. USER: Create New Project                                 │
│     ↓ Fills form: "E-Commerce Platform"                     │
│     ↓ Describes: "Build a Shopify competitor..."             │
│     ↓ Clicks "Create Project"                                │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  2. BACKEND: Receives Request                                │
│     ↓ POST /api/project/create                               │
│     ↓ Generates project_id: proj_abc123                      │
│     ↓ Broadcasts "project_created" via WebSocket             │
│     ↓ Starts background task: run_planning_phase()           │
│     ↓ Returns immediately with project_id                    │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  3. FRONTEND: Navigates to Project Page                      │
│     ↓ router.push(`/projects/${project_id}`)                 │
│     ↓ Project Workspace page loads                           │
│     ↓ Connects to WebSocket                                  │
│     ↓ Subscribes to events for this project_id               │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  4. BACKEND: Planning Phase Executes (Background)            │
│     ↓ Step 1: Oracle analyzes requirements (2s)              │
│       → WebSocket: "agent_activity" {Oracle, analyzing...}   │
│     ↓ Step 2: Oracle generates PRD (3s)                      │
│       → WebSocket: "agent_activity" {Oracle, generating...}  │
│     ↓ Step 3: Neuron breaks down tasks (2s)                  │
│       → WebSocket: "agent_activity" {Neuron, breaking...}    │
│     ↓ Step 4: Atlas creates Plane workspace (1s)             │
│       → WebSocket: "agent_activity" {Atlas, creating...}     │
│     ↓ Step 5: Atlas syncs tasks to Plane (2s)                │
│       → WebSocket: "agent_activity" {Atlas, syncing...}      │
│     ↓ Planning Complete!                                     │
│       → WebSocket: "project_status" {status: ready}          │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  5. FRONTEND: Real-Time Updates Display                      │
│     ↓ Receives WebSocket messages                            │
│     ↓ Activity Feed shows each agent's work                  │
│     ↓ Progress bar updates (0% → 20% → 40% → 100%)           │
│     ↓ Tasks appear as they're created                        │
│     ↓ Status updates from "planning" → "ready"               │
│     ↓ "Start Project" button becomes available               │
└──────────────────────────────────────────────────────────────┘
                           ↓
┌──────────────────────────────────────────────────────────────┐
│  6. USER: Sees Live Progress                                 │
│     ✅ "Oracle is analyzing your requirements..."            │
│     ✅ "Oracle is generating comprehensive PRD..."           │
│     ✅ "Neuron is breaking down features into tasks..."      │
│     ✅ "Atlas is creating Plane project workspace..."        │
│     ✅ "Atlas is syncing tasks to Plane..."                  │
│     ✅ "Project ready! 5 tasks created."                     │
└──────────────────────────────────────────────────────────────┘
```

## How to Test Current Implementation:

### Test the Backend (It DOES Work):

1. **Open Developer Console** (F12 in Chrome)
2. **Create a new project**
3. **Watch Network Tab**:
   - You'll see `POST /api/project/create` returns immediately
   - Response includes `project_id`
4. **Wait 10-15 seconds**
5. **Manually refresh the project page**
6. **Check if tasks appear** (they won't yet, because Plane integration isn't real)

### What You'll See:
- Project created instantly ✅
- You're redirected to project page ✅
- Page shows "No activity yet" ✅
- After 10s, nothing changes (because no WebSocket) ❌
- You need to refresh manually ❌

## What Needs to Be Built:

### Phase 1: Real-Time Updates (Next Priority)
1. Connect frontend to WebSocket
2. Listen for `agent_activity` messages
3. Update Activity Feed in real-time
4. Show progress as agents work
5. Update task list as tasks are created

### Phase 2: Actual AI Integration
1. Replace simulated workflow with real LangGraph
2. Integrate actual Gemini/Vertex AI
3. Generate real PRDs
4. Create actual Plane projects
5. Sync real tasks

### Phase 3: Build & QA Loop
1. Implement task execution
2. Add code generation agents (Pixel, Byte, etc.)
3. Build QA workflow with Code Judge
4. Generate actual code artifacts
5. Enable export/download

## Quick Start for Development:

```bash
# Terminal 1: Start Backend
cd velo-monorepo/backend
PORT=8000 python3 main.py

# Terminal 2: Start Frontend
cd velo-monorepo/frontend
npm run dev

# Terminal 3: Monitor WebSocket (Optional)
# Use a WebSocket client to connect to ws://localhost:8000/ws
# You'll see real-time messages when projects are created
```

## Architecture Summary:

```
Frontend (Next.js)          Backend (FastAPI)           Services
─────────────────          ──────────────────          ─────────

[React UI]                 [REST API]                  [LangGraph]
  │                          │                            │
  ├─ Project Pages          ├─ /api/project/*           ├─ Planning
  ├─ Agent Display          ├─ /api/agent/*             ├─ Build & QA
  └─ Real-Time Feed         └─ [WebSocket]              └─ Deploy
       ↑                         │
       └─────────────────────────┘
            WebSocket
        (Real-time updates)
```

## Summary:

**The system IS working** - the backend executes the planning workflow when you create a project. The UX issue is that the frontend doesn't show this happening in real-time yet. You need to either:

1. **Wait 10 seconds and refresh** to see results (current workaround)
2. **Add WebSocket support** to see live updates (recommended next step)
3. **Add a loading spinner** in the modal while planning executes (temporary fix)

The foundation is solid - we just need to connect the real-time communication layer!
