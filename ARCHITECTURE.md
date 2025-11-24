# Velo - AI Agency OS
## Complete Architecture Documentation

**Version:** 2.0.0
**Last Updated:** 2025-11-24
**Status:** Production Ready

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [System Architecture](#system-architecture)
3. [Technology Stack](#technology-stack)
4. [Component Architecture](#component-architecture)
5. [Data Flow & Workflows](#data-flow--workflows)
6. [AI Agent System](#ai-agent-system)
7. [Database Schema](#database-schema)
8. [API Architecture](#api-architecture)
9. [Deployment Architecture](#deployment-architecture)
10. [Security & Multi-tenancy](#security--multi-tenancy)

---

## Executive Summary

**Velo** is an AI-powered Agency Operating System that automates end-to-end software development using 51 specialized AI agents. It transforms project requirements into fully functional applications through an intelligent multi-agent system powered by Google Vertex AI (Gemini 1.5 Pro).

### Key Capabilities

- **Autonomous Software Development**: From PRD to deployment with minimal human intervention
- **51 Specialized AI Agents**: Organized into 9 divisions (Engineering, Design, Marketing, etc.)
- **Real-time Collaboration**: WebSocket-based live updates and streaming responses
- **Multi-tenant SaaS**: Enterprise-grade isolation with Row Level Security
- **Integrated Project Management**: Synchronized with Plane.so for task tracking
- **Artifact Management**: Version-controlled deliverables with collaboration features

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                 │
├─────────────────────────────────────────────────────────────────────┤
│  Next.js 15 Frontend (Firebase App Hosting)                         │
│  - React 18 + TypeScript                                            │
│  - Tailwind CSS + shadcn/ui                                         │
│  - Real-time WebSocket Connection                                   │
│  - Firebase Authentication                                           │
└──────────────────────┬──────────────────────────────────────────────┘
                       │
                       │ HTTPS / WSS
                       │
┌──────────────────────▼──────────────────────────────────────────────┐
│                      APPLICATION LAYER                               │
├─────────────────────────────────────────────────────────────────────┤
│  FastAPI Backend (Cloud Run)                                        │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  API Endpoints          WebSocket Manager                    │   │
│  │  - Projects             - Real-time updates                  │   │
│  │  - Tasks                - Agent activity streaming           │   │
│  │  - Artifacts            - Connection pooling                 │   │
│  │  - Tenants              - Broadcast to clients               │   │
│  └─────────────────────────────────────────────────────────────┘   │
│  ┌─────────────────────────────────────────────────────────────┐   │
│  │  Background Task Processor                                   │   │
│  │  - Planning Phase Execution                                  │   │
│  │  - Agent Orchestration                                       │   │
│  │  - Artifact Generation                                       │   │
│  └─────────────────────────────────────────────────────────────┘   │
└──────────────────────┬──────────────────┬───────────────────────────┘
                       │                  │
                ┌──────▼──────┐    ┌─────▼──────┐
                │             │    │            │
┌───────────────▼────────┐   │    │   ┌────────▼──────────────┐
│  AI/ML LAYER           │   │    │   │  DATA LAYER           │
├────────────────────────┤   │    │   ├───────────────────────┤
│  Google Vertex AI      │   │    │   │  Cloud SQL PostgreSQL │
│  ┌──────────────────┐  │   │    │   │  ┌─────────────────┐  │
│  │ Gemini 1.5 Pro   │  │   │    │   │  │ Multi-tenant DB │  │
│  │ - PRD Generation │  │   │    │   │  │ - Row Level     │  │
│  │ - Task Breakdown │  │   │    │   │  │   Security      │  │
│  │ - Code Gen       │  │   │    │   │  │ - Connection    │  │
│  └──────────────────┘  │   │    │   │  │   Pooling       │  │
│  ┌──────────────────┐  │   │    │   │  └─────────────────┘  │
│  │ Gemini 1.5 Flash │  │   │    │   └───────────────────────┘
│  │ - Quick tasks    │  │   │    │
│  │ - Summaries      │  │   │    │   ┌───────────────────────┐
│  └──────────────────┘  │   │    │   │  STORAGE LAYER        │
│  ┌──────────────────┐  │   │    │   ├───────────────────────┤
│  │ LangGraph        │  │   │    │   │  Google Cloud Storage │
│  │ - Workflow State │  │   │    │   │  - Artifact Storage   │
│  │ - Agent Chain    │  │   │    │   │  - Version Control    │
│  └──────────────────┘  │   │    │   │  - CDN Distribution   │
└────────────────────────┘   │    │   └───────────────────────┘
                             │    │
                    ┌────────▼────▼────────┐
                    │  AUTH LAYER          │
                    ├──────────────────────┤
                    │  Firebase Auth       │
                    │  - Email/Password    │
                    │  - OAuth Providers   │
                    │  - JWT Tokens        │
                    │  - Custom Claims     │
                    └──────────────────────┘
```

---

## Technology Stack

### Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Next.js** | 15.x | React framework with SSR/SSG |
| **React** | 18.x | UI library |
| **TypeScript** | 5.x | Type safety |
| **Tailwind CSS** | 3.x | Utility-first CSS |
| **shadcn/ui** | Latest | Component library |
| **Firebase SDK** | 10.x | Authentication client |
| **Socket.IO Client** | 4.x | WebSocket connection |

### Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.11 | Programming language |
| **FastAPI** | 0.114+ | Modern async web framework |
| **Uvicorn** | 0.30+ | ASGI server |
| **asyncpg** | Latest | Async PostgreSQL driver |
| **SQLAlchemy** | 2.0+ | ORM (optional, primarily using raw SQL) |
| **Pydantic** | 2.8+ | Data validation |
| **python-dotenv** | 1.0+ | Environment management |

### AI/ML

| Technology | Version | Purpose |
|------------|---------|---------|
| **Vertex AI** | Latest | Google's AI platform |
| **Gemini 1.5 Pro** | Latest | Primary LLM for complex tasks |
| **Gemini 1.5 Flash** | Latest | Fast LLM for quick tasks |
| **LangGraph** | 0.2.16 | Agent workflow orchestration |
| **LangChain** | 0.2.14 | LLM framework |
| **langchain-google-vertexai** | 1.0.10 | Vertex AI integration |

### Infrastructure

| Service | Purpose |
|---------|---------|
| **Firebase App Hosting** | Next.js frontend hosting |
| **Cloud Run** | Serverless container platform (backend) |
| **Cloud SQL (PostgreSQL)** | Managed relational database |
| **Cloud Storage** | Object storage for artifacts |
| **Cloud Build** | CI/CD pipeline |
| **Artifact Registry** | Container image storage |
| **Secret Manager** | Secure credential storage |

---

## Component Architecture

### Frontend Components

```
frontend/
├── app/                          # Next.js App Router
│   ├── (auth)/                   # Authentication routes
│   │   ├── login/
│   │   ├── signup/
│   │   └── onboarding/
│   ├── (dashboard)/              # Main app routes
│   │   ├── projects/
│   │   │   ├── [id]/            # Project detail
│   │   │   └── new/             # Create project
│   │   ├── tasks/
│   │   ├── artifacts/
│   │   └── settings/
│   └── api/                      # API routes (if needed)
├── components/
│   ├── ui/                       # shadcn/ui components
│   ├── layout/                   # Layout components
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── Footer.tsx
│   ├── projects/                 # Project-specific
│   │   ├── ProjectCard.tsx
│   │   ├── ProjectForm.tsx
│   │   └── ProjectDetail.tsx
│   ├── agents/                   # Agent visualization
│   │   ├── AgentActivity.tsx
│   │   ├── AgentList.tsx
│   │   └── AgentDivision.tsx
│   └── artifacts/                # Artifact components
│       ├── ArtifactViewer.tsx
│       ├── ArtifactVersion.tsx
│       └── ArtifactComment.tsx
├── lib/
│   ├── firebase.ts               # Firebase config
│   ├── api.ts                    # API client
│   ├── websocket.ts              # WebSocket manager
│   └── utils.ts                  # Utilities
└── hooks/
    ├── useAuth.ts                # Authentication hook
    ├── useProject.ts             # Project data hook
    ├── useWebSocket.ts           # WebSocket hook
    └── useArtifacts.ts           # Artifacts hook
```

### Backend Architecture

```
backend/
├── main_enhanced.py              # FastAPI application
├── agents/                       # AI Agent System
│   ├── base_agent.py            # Base agent class
│   ├── engineering/             # Engineering agents (7)
│   │   ├── neuron.py            # Full-stack developer
│   │   ├── pixel.py             # Frontend specialist
│   │   ├── atlas.py             # Backend architect
│   │   ├── nova.py              # API designer
│   │   ├── blitz.py             # Performance optimizer
│   │   ├── sage.py              # Database expert
│   │   └── forge.py             # DevOps engineer
│   ├── design/                  # Design agents (6)
│   │   ├── aurora.py            # UX/UI lead
│   │   ├── canvas.py            # Visual designer
│   │   ├── echo.py              # Interaction designer
│   │   ├── compass.py           # Information architect
│   │   ├── spark.py             # Brand designer
│   │   └── ember.py             # Animation specialist
│   ├── marketing/               # Marketing agents (8)
│   │   ├── phoenix.py           # Growth strategist
│   │   ├── quill.py             # Content writer
│   │   ├── chirp.py             # Social media manager
│   │   ├── pulse.py             # Email marketing
│   │   ├── nexus.py             # SEO specialist
│   │   ├── prism.py             # Analytics expert
│   │   ├── rocket.py            # Launch coordinator
│   │   └── rhythm.py            # Community manager
│   ├── product/                 # Product agents (3)
│   │   ├── horizon.py           # Product strategist
│   │   ├── synthesis.py         # Feature designer
│   │   └── sprint.py            # Agile coach
│   ├── project_management/      # PM agents (5)
│   │   ├── oracle.py            # PRD generator
│   │   ├── maestro.py           # Technical PM
│   │   ├── shepherd.py          # Scrum master
│   │   ├── clockwork.py         # Timeline optimizer
│   │   └── prism_lab.py         # Resource allocator
│   ├── testing/                 # QA agents (7)
│   │   ├── sherlock.py          # Bug detective
│   │   ├── verdict.py           # Test architect
│   │   ├── flow.py              # E2E test specialist
│   │   ├── postman.py           # API tester
│   │   ├── benchmark.py         # Performance tester
│   │   ├── forge_tester.py      # Load tester
│   │   └── gatekeeper.py        # Security auditor
│   ├── support/                 # Support agents (6)
│   │   ├── beacon.py            # Customer success
│   │   ├── shield.py            # Security specialist
│   │   ├── ledger.py            # Compliance officer
│   │   ├── insight.py           # Data analyst
│   │   ├── summit.py            # Training specialist
│   │   └── sentinel.py          # Monitor & alerts
│   ├── spatial_computing/       # Spatial agents (6)
│   │   ├── vision.py            # visionOS developer
│   │   ├── immerse.py           # VR specialist
│   │   ├── gesture.py           # Interaction designer
│   │   ├── hologram.py          # 3D modeler
│   │   ├── titanium.py          # ARKit expert
│   │   └── terminal.py          # RealityKit developer
│   └── specialized/             # Specialized agents (3)
│       ├── conductor.py         # Orchestra conductor
│       ├── prism_analytics.py   # Analytics engine
│       └── index.py             # Knowledge indexer
├── integrations/
│   ├── vertex_ai.py             # Vertex AI client
│   ├── plane.py                 # Plane.so integration
│   └── storage.py               # GCS client
├── database/
│   ├── connection.py            # Connection pooling
│   ├── repositories.py          # Repository pattern
│   └── schema.sql               # Database schema
└── workflows/
    ├── planning_phase.py        # Planning workflow
    ├── development_phase.py     # Development workflow
    └── testing_phase.py         # Testing workflow
```

---

## Data Flow & Workflows

### 1. Project Creation Flow

```
┌─────────────┐
│   User      │
│  Creates    │
│  Project    │
└──────┬──────┘
       │
       │ 1. POST /api/project/create
       │    { name, description }
       ▼
┌──────────────────────────────────────┐
│  FastAPI Backend                     │
│  ┌────────────────────────────────┐  │
│  │ 1. Validate request            │  │
│  │ 2. Create project in DB        │  │
│  │ 3. Return project ID           │  │
│  │ 4. Start background task       │  │
│  └────────────┬───────────────────┘  │
└───────────────┼──────────────────────┘
                │
                │ 5. Background: Planning Phase
                ▼
    ┌───────────────────────────┐
    │  Planning Phase Workflow  │
    │  ┌─────────────────────┐  │
    │  │ Step 1: Oracle      │  │
    │  │ Generate PRD        │  │
    │  │ • User requirements │  │
    │  │ • Technical specs   │  │
    │  │ • Success criteria  │  │
    │  └──────────┬──────────┘  │
    │             │              │
    │             ▼              │
    │  ┌─────────────────────┐  │
    │  │ Step 2: Neuron      │  │
    │  │ Break down tasks    │  │
    │  │ • Parse PRD         │  │
    │  │ • Create task list  │  │
    │  │ • Assign agents     │  │
    │  └──────────┬──────────┘  │
    │             │              │
    │             ▼              │
    │  ┌─────────────────────┐  │
    │  │ Step 3: Database    │  │
    │  │ Store tasks         │  │
    │  │ • Insert tasks      │  │
    │  │ • Update project    │  │
    │  │ • Create artifacts  │  │
    │  └──────────┬──────────┘  │
    └─────────────┼──────────────┘
                  │
                  │ 6. Broadcast updates via WebSocket
                  ▼
        ┌─────────────────────┐
        │  WebSocket Manager  │
        │  • Agent activity   │
        │  • Task progress    │
        │  • Project status   │
        └──────────┬──────────┘
                   │
                   │ 7. Real-time updates
                   ▼
            ┌──────────────┐
            │  Frontend    │
            │  • Update UI │
            │  • Show      │
            │    progress  │
            └──────────────┘
```

### 2. Agent Execution Flow

```
┌──────────────────────────────────────────────────────┐
│  Agent Orchestration (Conductor)                     │
└──────────────────┬───────────────────────────────────┘
                   │
                   │ 1. Get next task from queue
                   ▼
        ┌──────────────────────┐
        │  Task Assignment     │
        │  • Priority          │
        │  • Agent match       │
        │  • Dependencies      │
        └──────────┬───────────┘
                   │
                   │ 2. Delegate to specific agent
                   ▼
     ┌─────────────────────────────────┐
     │  Agent Execution                │
     │  ┌───────────────────────────┐  │
     │  │ 1. Load context           │  │
     │  │    • Project info         │  │
     │  │    • Previous artifacts   │  │
     │  │    • Task requirements    │  │
     │  └────────────┬──────────────┘  │
     │               │                 │
     │               ▼                 │
     │  ┌───────────────────────────┐  │
     │  │ 2. Execute with Vertex AI │  │
     │  │    • Build prompt         │  │
     │  │    • Call Gemini API      │  │
     │  │    • Process response     │  │
     │  └────────────┬──────────────┘  │
     │               │                 │
     │               ▼                 │
     │  ┌───────────────────────────┐  │
     │  │ 3. Generate artifact      │  │
     │  │    • Code files           │  │
     │  │    • Documentation        │  │
     │  │    • Diagrams             │  │
     │  └────────────┬──────────────┘  │
     │               │                 │
     │               ▼                 │
     │  ┌───────────────────────────┐  │
     │  │ 4. Store & log            │  │
     │  │    • Upload to GCS        │  │
     │  │    • Create DB record     │  │
     │  │    • Log activity         │  │
     │  └────────────┬──────────────┘  │
     └───────────────┼──────────────────┘
                     │
                     │ 5. Notify completion
                     ▼
          ┌──────────────────────┐
          │  Update Task Status  │
          │  • Mark completed    │
          │  • Trigger next task │
          │  • Broadcast update  │
          └──────────────────────┘
```

### 3. Real-time Update Flow

```
┌──────────────┐
│  Backend     │
│  Event       │
└──────┬───────┘
       │
       │ 1. Agent activity / Task update / Project status
       ▼
┌────────────────────────────────┐
│  WebSocket Manager             │
│  ┌──────────────────────────┐  │
│  │ Active Connections Pool  │  │
│  │ • Connection tracking    │  │
│  │ • Client management      │  │
│  └────────┬─────────────────┘  │
└───────────┼────────────────────┘
            │
            │ 2. Broadcast to all connected clients
            ▼
    ┌───────────────────────┐
    │  Message Formatting   │
    │  {                    │
    │    type: "event_type",│
    │    project_id: "...", │
    │    data: {...}        │
    │  }                    │
    └───────────┬───────────┘
                │
                │ 3. Send via WebSocket
                ▼
        ┌───────────────┐
        │  Frontend     │
        │  Listener     │
        └───────┬───────┘
                │
                │ 4. Handle message
                ▼
    ┌───────────────────────┐
    │  Update React State   │
    │  • Project data       │
    │  • Task list          │
    │  • Agent activities   │
    │  • UI refresh         │
    └───────────────────────┘
```

---

## AI Agent System

### Agent Organization

**51 Specialized AI Agents** organized into **9 Divisions**:

```
Velo AI Agency
│
├── Engineering (7 agents)
│   ├── Neuron        - Full-stack development lead
│   ├── Pixel         - Frontend specialist
│   ├── Atlas         - Backend architect
│   ├── Nova          - API designer
│   ├── Blitz         - Performance optimizer
│   ├── Sage          - Database expert
│   └── Forge         - DevOps engineer
│
├── Design (6 agents)
│   ├── Aurora        - UX/UI lead designer
│   ├── Canvas        - Visual designer
│   ├── Echo          - Interaction designer
│   ├── Compass       - Information architect
│   ├── Spark         - Brand designer
│   └── Ember         - Animation specialist
│
├── Marketing (8 agents)
│   ├── Phoenix       - Growth strategist
│   ├── Quill         - Content writer
│   ├── Chirp         - Social media manager
│   ├── Pulse         - Email marketing
│   ├── Nexus         - SEO specialist
│   ├── Prism         - Analytics expert
│   ├── Rocket        - Launch coordinator
│   └── Rhythm        - Community manager
│
├── Product (3 agents)
│   ├── Horizon       - Product strategist
│   ├── Synthesis     - Feature designer
│   └── Sprint        - Agile coach
│
├── Project Management (5 agents)
│   ├── Oracle        - PRD generator (leads planning)
│   ├── Maestro       - Technical project manager
│   ├── Shepherd      - Scrum master
│   ├── Clockwork     - Timeline optimizer
│   └── Prism Lab     - Resource allocator
│
├── Testing (7 agents)
│   ├── Sherlock      - Bug detective
│   ├── Verdict       - Test architect
│   ├── Flow          - E2E test specialist
│   ├── Postman       - API tester
│   ├── Benchmark     - Performance tester
│   ├── Forge Tester  - Load tester
│   └── Gatekeeper    - Security auditor
│
├── Support (6 agents)
│   ├── Beacon        - Customer success
│   ├── Shield        - Security specialist
│   ├── Ledger        - Compliance officer
│   ├── Insight       - Data analyst
│   ├── Summit        - Training specialist
│   └── Sentinel      - Monitoring & alerts
│
├── Spatial Computing (6 agents)
│   ├── Vision        - visionOS developer
│   ├── Immerse       - VR specialist
│   ├── Gesture       - Spatial interaction designer
│   ├── Hologram      - 3D modeler
│   ├── Titanium      - ARKit expert
│   └── Terminal      - RealityKit developer
│
└── Specialized (3 agents)
    ├── Conductor     - Orchestra conductor (coordinates all agents)
    ├── Prism Analytics - Advanced analytics engine
    └── Index         - Knowledge base indexer
```

### Agent Capabilities

Each agent has:

1. **Specialization**: Domain expertise (frontend, backend, design, etc.)
2. **Skills**: Specific technical capabilities
3. **Tools**: Access to Vertex AI, code generation, file operations
4. **Context Awareness**: Understanding of project state and history
5. **Collaboration**: Works with other agents through shared state

### Agent Communication

Agents communicate through:

- **Shared Database**: Common project/task state
- **Artifact Repository**: Shared files and documents
- **Message Queue**: Async task coordination
- **LangGraph State**: Workflow state management

---

## Database Schema

### Entity Relationship Diagram

```
┌─────────────────┐
│    Tenants      │
│─────────────────│
│ id (PK)         │
│ company_name    │
│ subdomain       │
│ plan_tier       │
│ settings        │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────┴────────┐
│     Users       │
│─────────────────│
│ id (PK)         │
│ tenant_id (FK)  │
│ firebase_uid    │
│ email           │
│ display_name    │
│ role            │
└────────┬────────┘
         │ 1
         │
         │ N
┌────────┴────────────┐
│     Projects        │
│─────────────────────│
│ id (PK)             │
│ tenant_id (FK)      │
│ user_id (FK)        │
│ name                │
│ description         │
│ plane_project_id    │
│ status              │
└────────┬────────────┘
         │ 1
         ├─────────────────────┐
         │ N                   │ N
┌────────┴────────┐   ┌────────┴────────────┐
│     Tasks       │   │    Artifacts        │
│─────────────────│   │─────────────────────│
│ id (PK)         │   │ id (PK)             │
│ project_id (FK) │   │ project_id (FK)     │
│ plane_issue_id  │   │ agent_name          │
│ title           │   │ agent_division      │
│ description     │   │ file_name           │
│ status          │   │ file_type           │
│ priority        │   │ gcs_path            │
│ assigned_agent  │   │ version             │
└─────────────────┘   └──────────┬──────────┘
                                 │ 1
                                 │
                      ┌──────────┴───────────┐
                      │                      │ N
              ┌───────┴──────────┐  ┌────────┴─────────────┐
              │ Artifact Versions│  │  Artifact Comments   │
              │──────────────────│  │──────────────────────│
              │ id (PK)          │  │ id (PK)              │
              │ artifact_id (FK) │  │ artifact_id (FK)     │
              │ version_number   │  │ user_id (FK)         │
              │ gcs_path         │  │ content              │
              │ created_by (FK)  │  │ line_number          │
              └──────────────────┘  └──────────────────────┘

┌─────────────────────┐
│  Agent Activities   │
│─────────────────────│
│ id (PK)             │
│ project_id (FK)     │
│ task_id (FK)        │
│ agent_name          │
│ agent_division      │
│ action              │
│ status              │
│ error_message       │
│ timestamp           │
│ duration_ms         │
└─────────────────────┘

┌─────────────────────┐
│    Usage Logs       │
│─────────────────────│
│ id (PK)             │
│ tenant_id (FK)      │
│ project_id (FK)     │
│ user_id (FK)        │
│ agent_name          │
│ action_type         │
│ tokens_used         │
│ cost_usd            │
│ timestamp           │
└─────────────────────┘
```

### Key Tables

#### Tenants
- **Purpose**: Multi-tenant isolation
- **RLS**: Enabled for data isolation
- **Key Fields**: subdomain (unique), plan_tier (free/pro/enterprise)

#### Users
- **Purpose**: User accounts linked to tenants
- **Auth**: Firebase UID mapping
- **RBAC**: role field (admin, member, viewer)

#### Projects
- **Purpose**: Software projects managed by Velo
- **Status**: planning → in_progress → completed → archived
- **Integration**: Links to Plane.so via plane_project_id

#### Artifacts
- **Purpose**: Generated deliverables (code, docs, diagrams)
- **Storage**: Files stored in GCS, metadata in DB
- **Versioning**: Full version history with artifact_versions

#### Tasks
- **Purpose**: Work items for agents
- **Sync**: Bidirectional sync with Plane.so
- **Assignment**: Assigned to specific agents

#### Agent Activities
- **Purpose**: Audit log of agent actions
- **Metrics**: Tracks duration, status, errors
- **Analytics**: Used for performance monitoring

---

## API Architecture

### RESTful Endpoints

#### Authentication
```
POST   /api/auth/register        - Register new user
POST   /api/auth/login           - Login (Firebase handled)
POST   /api/auth/refresh         - Refresh token
POST   /api/auth/logout          - Logout
```

#### Tenants
```
POST   /api/tenant/create        - Create new tenant
GET    /api/tenant/{id}          - Get tenant details
PATCH  /api/tenant/{id}          - Update tenant
GET    /api/tenant/members       - List team members
POST   /api/tenant/invite        - Invite team member
```

#### Projects
```
POST   /api/project/create       - Create new project (starts planning)
GET    /api/project/list         - List all projects
GET    /api/project/{id}         - Get project details
PATCH  /api/project/{id}         - Update project
DELETE /api/project/{id}         - Archive project
GET    /api/project/{id}/tasks   - Get project tasks
GET    /api/project/{id}/artifacts - Get project artifacts
GET    /api/project/{id}/activity  - Get agent activity log
```

#### Tasks
```
GET    /api/task/{id}            - Get task details
PATCH  /api/task/{id}            - Update task
POST   /api/task/{id}/assign     - Assign to agent
```

#### Artifacts
```
GET    /api/artifact/{id}        - Get artifact metadata
GET    /api/artifact/{id}/download - Download artifact file
GET    /api/artifact/{id}/versions - Get version history
POST   /api/artifact/{id}/comment  - Add comment
GET    /api/artifact/{id}/share    - Create shareable link
```

#### Agents
```
GET    /api/agents               - List all agents
GET    /api/agents/{name}        - Get agent details
GET    /api/agents/{name}/activity - Get agent activity history
```

### WebSocket Protocol

```
Connection: wss://api.velo.com/ws

# Client → Server Messages
{
  "type": "ping",
  "timestamp": "2025-11-24T12:00:00Z"
}

{
  "type": "subscribe",
  "project_id": "uuid"
}

# Server → Client Messages
{
  "type": "project_created",
  "project_id": "uuid",
  "project_name": "My Project",
  "status": "planning",
  "timestamp": "2025-11-24T12:00:00Z"
}

{
  "type": "agent_activity",
  "project_id": "uuid",
  "agent_name": "Oracle",
  "action": "Generating PRD",
  "status": "in_progress",
  "timestamp": "2025-11-24T12:00:01Z"
}

{
  "type": "task_created",
  "project_id": "uuid",
  "task_id": "uuid",
  "title": "Implement authentication",
  "assigned_agent": "Neuron",
  "timestamp": "2025-11-24T12:00:05Z"
}

{
  "type": "project_status",
  "project_id": "uuid",
  "status": "ready",
  "message": "Planning phase completed with 15 tasks",
  "timestamp": "2025-11-24T12:05:00Z"
}
```

---

## Deployment Architecture

### Production Environment

```
┌─────────────────────────────────────────────────────────────┐
│                    Google Cloud Platform                     │
│                    Project: velo-479115                      │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Firebase App Hosting                              │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │  Next.js Frontend                            │  │     │
│  │  │  • SSR/SSG rendering                         │  │     │
│  │  │  • CDN distribution                          │  │     │
│  │  │  • Auto-scaling                              │  │     │
│  │  │  • HTTPS/HTTP2                               │  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  └────────────────────────────────────────────────────┘     │
│                           │                                  │
│                           │ HTTPS                            │
│                           ▼                                  │
│  ┌────────────────────────────────────────────────────┐     │
│  │  Cloud Run (Backend)                               │     │
│  │  Region: us-central1                               │     │
│  │  ┌──────────────────────────────────────────────┐  │     │
│  │  │  FastAPI Container                           │  │     │
│  │  │  • Min instances: 0                          │  │     │
│  │  │  • Max instances: 10                         │  │     │
│  │  │  • Memory: 1Gi                               │  │     │
│  │  │  • CPU: 1                                    │  │     │
│  │  │  • Timeout: 300s                             │  │     │
│  │  └──────────────────────────────────────────────┘  │     │
│  └────────────────┬───────────────┬────────────────────┘     │
│                   │               │                          │
│                   │               │                          │
│       ┌───────────┴───┐   ┌───────┴──────────┐             │
│       │               │   │                  │             │
│  ┌────▼────────────┐  │   │  ┌───────────────▼──────┐      │
│  │  Cloud SQL      │  │   │  │  Vertex AI           │      │
│  │  PostgreSQL 15  │  │   │  │  us-central1         │      │
│  │  ┌────────────┐ │  │   │  │  ┌─────────────────┐ │      │
│  │  │ velo DB    │ │  │   │  │  │ Gemini 1.5 Pro  │ │      │
│  │  │ Tier: f1   │ │  │   │  │  │ Gemini 1.5 Flash│ │      │
│  │  │ Region: us │ │  │   │  │  │ LangGraph       │ │      │
│  │  │  -central1 │ │  │   │  │  └─────────────────┘ │      │
│  │  └────────────┘ │  │   │  └──────────────────────┘      │
│  └─────────────────┘  │   │                                 │
│                       │   │  ┌──────────────────────────┐   │
│  ┌────────────────────┘   │  │  Cloud Storage           │   │
│  │                        │  │  • Artifacts bucket      │   │
│  │  ┌─────────────────────▼──▼──• Version control       │   │
│  │  │  Secret Manager           │  • CDN enabled        │   │
│  │  │  • Firebase API keys      │  └──────────────────────┘   │
│  │  │  • DB credentials         │                         │
│  │  │  • Service account keys   │                         │
│  │  └───────────────────────────┘                         │
│  │                                                         │
│  │  ┌──────────────────────────────────────────────┐      │
│  │  │  Artifact Registry                           │      │
│  │  │  • Docker images                             │      │
│  │  │  • velo-docker repository                    │      │
│  │  └──────────────────────────────────────────────┘      │
│  │                                                         │
│  │  ┌──────────────────────────────────────────────┐      │
│  │  │  Cloud Build                                 │      │
│  │  │  • CI/CD pipelines                           │      │
│  │  │  • Automatic builds                          │      │
│  │  └──────────────────────────────────────────────┘      │
│  │                                                         │
│  └─────────────────────────────────────────────────────────┘
│                                                             │
│  ┌──────────────────────────────────────────────────┐      │
│  │  Firebase Services                               │      │
│  │  • Authentication (Email/Password, OAuth)        │      │
│  │  • Firestore (optional, currently using Cloud SQL) │   │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

### Deployment Workflow

```
┌──────────────┐
│  Developer   │
│  git push    │
└──────┬───────┘
       │
       │ 1. Push to repository
       ▼
┌──────────────────────────┐
│  Cloud Build Trigger     │
│  • Detect changes        │
│  • Start build pipeline  │
└──────────┬───────────────┘
           │
           │ 2. Build Docker images
           ▼
    ┌──────────────────────────┐
    │  Build Steps             │
    │  ┌────────────────────┐  │
    │  │ 1. Backend Build   │  │
    │  │   • pip install    │  │
    │  │   • Run tests      │  │
    │  │   • Build image    │  │
    │  └────────┬───────────┘  │
    │           │              │
    │           ▼              │
    │  ┌────────────────────┐  │
    │  │ 2. Push to         │  │
    │  │    Artifact Reg    │  │
    │  └────────┬───────────┘  │
    └───────────┼──────────────┘
                │
                │ 3. Deploy
                ▼
       ┌─────────────────────┐
       │  Cloud Run Deploy   │
       │  • Rolling update   │
       │  • Health checks    │
       │  • Route traffic    │
       └─────────────────────┘

    Frontend Deployment:

┌──────────────┐
│  Developer   │
│  git push    │
└──────┬───────┘
       │
       │ 1. Push to repository
       ▼
┌─────────────────────────────┐
│  Firebase App Hosting       │
│  • Automatic detection      │
│  • Build Next.js app        │
│  • Deploy to CDN            │
│  • Update routing           │
└─────────────────────────────┘
```

---

## Security & Multi-tenancy

### Authentication & Authorization

```
┌──────────────────┐
│  User Request    │
└────────┬─────────┘
         │
         │ 1. Include Firebase JWT in Authorization header
         ▼
┌─────────────────────────────┐
│  Firebase Auth Middleware   │
│  • Verify JWT token         │
│  • Decode user claims       │
│  • Extract tenant_id        │
└────────┬────────────────────┘
         │
         │ 2. Valid token
         ▼
┌─────────────────────────────┐
│  Tenant Middleware          │
│  • Load tenant context      │
│  • Check plan limits        │
│  • Verify permissions       │
└────────┬────────────────────┘
         │
         │ 3. Authorized request
         ▼
┌─────────────────────────────┐
│  Route Handler              │
│  • tenant_id in context     │
│  • user_id in context       │
│  • role in context          │
└─────────────────────────────┘
```

### Multi-tenant Data Isolation

#### Row Level Security (RLS)

```sql
-- Example RLS policy for projects table
CREATE POLICY tenant_isolation_policy ON projects
  USING (tenant_id = current_setting('app.current_tenant_id')::uuid);

-- Set tenant context at connection level
SET app.current_tenant_id = '<tenant_uuid>';
```

#### Application-level Isolation

```python
# All database queries automatically filtered by tenant_id
async def list_projects(tenant_id: str):
    query = """
        SELECT * FROM projects
        WHERE tenant_id = $1
        ORDER BY created_at DESC
    """
    return await db.fetch(query, tenant_id)
```

### Security Best Practices

1. **Authentication**: Firebase Authentication with JWT tokens
2. **Authorization**: Role-based access control (RBAC)
3. **Data Isolation**: Row Level Security + app-level filtering
4. **Secrets Management**: Google Secret Manager
5. **API Rate Limiting**: Per-tenant quotas
6. **HTTPS Only**: All communication encrypted
7. **SQL Injection Prevention**: Parameterized queries
8. **CORS**: Strict origin validation
9. **Input Validation**: Pydantic models
10. **Audit Logging**: All actions logged in agent_activities

---

## Monitoring & Observability

### Metrics

- **Application Metrics**: Request latency, error rates, throughput
- **Agent Metrics**: Task completion time, success rate, token usage
- **Database Metrics**: Connection pool, query performance
- **Infrastructure Metrics**: CPU, memory, network

### Logging

```python
# Structured logging with context
logger.info(
    "Agent activity",
    extra={
        "project_id": project_id,
        "agent_name": "Oracle",
        "action": "Generate PRD",
        "duration_ms": 1234,
        "status": "completed"
    }
)
```

### Tracing

- **Cloud Trace**: Distributed tracing across services
- **Request IDs**: Track requests through the system
- **Performance Profiling**: Identify bottlenecks

---

## Scalability

### Horizontal Scaling

- **Frontend**: Firebase App Hosting (automatic CDN)
- **Backend**: Cloud Run (auto-scaling 0-10 instances)
- **Database**: Cloud SQL (vertical scaling, read replicas)
- **Storage**: Cloud Storage (unlimited, CDN-backed)

### Performance Optimization

1. **Connection Pooling**: asyncpg pool (2-10 connections)
2. **Caching**: Redis for session/query caching (future)
3. **Database Indexing**: Strategic indexes on hot paths
4. **CDN**: Global distribution for frontend assets
5. **Async Processing**: Background tasks for long operations
6. **WebSocket Multiplexing**: Single connection per client

---

## Cost Optimization

### Free Tier Resources

- **Firebase App Hosting**: Generous free tier
- **Cloud Run**: Pay-per-use, scales to zero
- **Cloud SQL**: f1-micro tier for development
- **Vertex AI**: Pay-per-token usage
- **Cloud Storage**: First 5GB free

### Cost Monitoring

- **Usage Logs**: Track token usage and API calls
- **Billing Alerts**: Automated alerts at thresholds
- **Per-tenant Tracking**: Attribution for billing

---

## Development Workflow

### Local Development

```bash
# Backend
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python3 main_enhanced.py

# Frontend
cd frontend
npm install
npm run dev
```

### Environment Variables

```bash
# Backend (.env)
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json
GOOGLE_CLOUD_PROJECT=velo-479115
API_PORT=8000
API_HOST=0.0.0.0
DB_HOST=localhost
DB_PORT=5432
DB_NAME=velo
DB_USER=postgres
DB_PASSWORD=

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_FIREBASE_API_KEY=...
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=velo-479115.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=velo-479115
```

---

## Future Enhancements

### Planned Features

1. **Enhanced Agent Collaboration**: Multi-agent conversations
2. **Code Review Automation**: PR review by agents
3. **Deployment Automation**: One-click deploy to various platforms
4. **Custom Agent Training**: Fine-tune agents on company codebase
5. **Visual Workflow Builder**: Drag-and-drop agent workflows
6. **Mobile App**: iOS/Android native apps
7. **Marketplace**: Share and monetize custom agents
8. **Enterprise SSO**: SAML/OIDC integration
9. **Advanced Analytics**: Project insights and predictions
10. **Real-time Collaboration**: Multi-user editing

---

## Appendix

### Glossary

- **Agent**: AI-powered specialist that performs specific tasks
- **Artifact**: Generated file or document (code, docs, diagrams)
- **Division**: Group of related agents (Engineering, Design, etc.)
- **LangGraph**: Framework for orchestrating AI agent workflows
- **Tenant**: Multi-tenant organization (company using Velo)
- **Vertex AI**: Google's AI/ML platform
- **WebSocket**: Real-time bidirectional communication protocol

### References

- [Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Firebase App Hosting](https://firebase.google.com/docs/app-hosting)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [Next.js Documentation](https://nextjs.org/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

---

**Document Version**: 2.0.0
**Last Updated**: 2025-11-24
**Maintained By**: Velo Engineering Team
