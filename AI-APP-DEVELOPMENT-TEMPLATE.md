# AI Application Development Master Template
## Complete Guide for Building Production-Ready AI Applications

> **Based on**: Velo - The AI Agency OS Production Deployment
> **Last Updated**: November 2025
> **Team**: Bright Tier Solutions

---

## Table of Contents

1. [Project Initialization](#1-project-initialization)
2. [Architecture Planning](#2-architecture-planning)
3. [Backend Development](#3-backend-development)
4. [Frontend Development](#4-frontend-development)
5. [AI Agent Development](#5-ai-agent-development)
6. [Database Design](#6-database-design)
7. [Deployment Strategy](#7-deployment-strategy)
8. [Testing & Quality Assurance](#8-testing--quality-assurance)
9. [Best Practices Checklist](#9-best-practices-checklist)
10. [Common Pitfalls & Solutions](#10-common-pitfalls--solutions)

---

## 1. Project Initialization

### 1.1 Project Structure

```
project-name/
├── .github/                    # GitHub Actions workflows
│   └── workflows/
│       ├── backend-ci.yml
│       └── frontend-ci.yml
├── backend/                    # Python FastAPI backend
│   ├── agents/                # AI agents organized by division
│   │   ├── __init__.py
│   │   ├── base_agent.py
│   │   ├── division_1/
│   │   ├── division_2/
│   │   └── ...
│   ├── database/              # Database layer
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   ├── repositories.py
│   │   └── schema.sql
│   ├── integrations/          # External service integrations
│   │   ├── __init__.py
│   │   ├── vertex_ai.py
│   │   ├── firebase_client.py
│   │   └── storage_manager.py
│   ├── graph/                 # LangGraph workflows
│   │   ├── __init__.py
│   │   ├── state.py
│   │   └── workflow.py
│   ├── tools/                 # Utility tools
│   ├── scripts/               # Automation scripts
│   ├── tests/                 # Backend tests
│   ├── .env.example
│   ├── Dockerfile
│   ├── Dockerfile.prod
│   ├── requirements.txt
│   └── main.py
├── frontend/                  # Next.js frontend
│   ├── app/                   # Next.js 14+ App Router
│   │   ├── (auth)/
│   │   ├── (dashboard)/
│   │   ├── api/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/            # React components
│   │   ├── ui/               # shadcn/ui components
│   │   ├── features/         # Feature-specific components
│   │   └── shared/           # Shared components
│   ├── lib/                   # Utilities & configs
│   │   ├── firebase.ts
│   │   ├── api-client.ts
│   │   └── utils.ts
│   ├── hooks/                 # Custom React hooks
│   ├── types/                 # TypeScript types
│   ├── public/                # Static assets
│   ├── .env.local.example
│   ├── apphosting.yaml        # Firebase App Hosting config
│   ├── next.config.ts
│   ├── package.json
│   └── tsconfig.json
├── infrastructure/            # Infrastructure as code
│   ├── docker-compose.yml
│   ├── terraform/
│   └── kubernetes/
├── database/                  # Database migrations
│   └── migrations/
├── docs/                      # Documentation
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
├── .firebaserc
├── firebase.json
├── deploy-firebase.sh         # Firebase deployment script
├── deploy-to-cloud.sh         # Cloud Run deployment script
├── .gitignore
├── ARCHITECTURE.md
└── README.md
```

### 1.2 Initialize Project

```bash
# Create project directory
mkdir -p project-name && cd project-name

# Initialize git
git init
git branch -M main

# Create .gitignore
cat > .gitignore << 'EOF'
# Environment variables and secrets
.env
.env.*
!.env.example
*.env
service-account.json
firebase-service-account.json

# Dependencies
node_modules/
__pycache__/
*.pyc
venv/
env/

# Build outputs
.next/
dist/
build/

# IDE
.vscode/
.idea/

# OS
.DS_Store

# Logs
*.log

# Database
*.db
*.sqlite

# Firebase
.firebase/
EOF

# Create README template
cat > README.md << 'EOF'
# Project Name

## Overview
Brief description of your AI application

## Tech Stack
- **Backend**: Python FastAPI + Google Vertex AI + LangGraph
- **Frontend**: Next.js 14 + TypeScript + Tailwind CSS + shadcn/ui
- **Database**: PostgreSQL (Cloud SQL)
- **AI/ML**: Google Vertex AI (Gemini 1.5 Pro/Flash)
- **Hosting**: Firebase App Hosting (Frontend) + Cloud Run (Backend)
- **Authentication**: Firebase Auth

## Quick Start
[Instructions here]

## Architecture
See [ARCHITECTURE.md](./ARCHITECTURE.md)

## Deployment
See [docs/DEPLOYMENT.md](./docs/DEPLOYMENT.md)
EOF
```

---

## 2. Architecture Planning

### 2.1 Create ARCHITECTURE.md

**Key sections to include:**

1. **System Overview Diagram** (ASCII or Mermaid)
2. **Technology Stack Details**
3. **AI Agent Architecture**
   - Agent divisions and specializations
   - Agent communication patterns
   - LangGraph workflow design
4. **Database Schema** (ERD)
5. **API Architecture** (REST + WebSocket)
6. **Data Flow Diagrams**
7. **Security & Authentication**
8. **Deployment Architecture**

### 2.2 AI Agent Planning Template

```markdown
## AI Agents Structure

### Agent Divisions

1. **[Division Name]** (e.g., Engineering, Design, Data Science)
   - Agent 1: [Name] - [Specialization]
   - Agent 2: [Name] - [Specialization]
   - ...

### Agent Base Class

```python
class BaseAgent:
    def __init__(self, agent_id, name, specialization):
        self.agent_id = agent_id
        self.name = name
        self.specialization = specialization

    async def execute(self, task: Dict) -> Dict:
        """Execute agent task with Vertex AI"""
        pass
```

### LangGraph Workflow

```python
# Define state
class AgentState(TypedDict):
    messages: List[Dict]
    current_agent: str
    task_status: str
    artifacts: List[Dict]
```
```

---

## 3. Backend Development

### 3.1 Setup Backend Environment

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Create requirements.txt
cat > requirements.txt << 'EOF'
# Firebase and Google Cloud
firebase-functions==0.4.0
firebase-admin==6.5.0
google-cloud-aiplatform>=1.50.0
google-cloud-storage>=2.14.0
cloud-sql-python-connector[asyncpg]

# Genkit for Firebase
genkit==0.4.0

# LangGraph and LangChain
langgraph>=0.2.0
langchain>=0.2.0
langchain-google-vertexai>=1.0.0

# Database
asyncpg
psycopg2-binary==2.9.9
sqlalchemy==2.0.31

# API and Web
fastapi>=0.110.0
uvicorn>=0.30.0
pydantic>=2.7.0
httpx>=0.28.1
websockets>=12.0

# Utilities
python-dotenv==1.0.1
pyyaml==6.0.2
tenacity==8.5.0
EOF

# Install dependencies
pip install -r requirements.txt
```

### 3.2 Environment Configuration

```bash
# Create .env.example
cat > .env.example << 'EOF'
# Firebase Configuration
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_SERVICE_ACCOUNT_PATH=./service-account.json

# Google Cloud
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=./service-account.json

# Database (Local Development)
DB_HOST=localhost
DB_PORT=5432
DB_NAME=your_db_name
DB_USER=postgres
DB_PASSWORD=your_password

# Database (Production - Cloud SQL)
CLOUD_SQL_CONNECTION_NAME=project-id:region:instance-name

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# Vertex AI Configuration
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_MODEL=gemini-1.5-pro

# External Services
PLANE_API_URL=https://api.plane.so
PLANE_API_KEY=your-plane-api-key
EOF
```

### 3.3 FastAPI Main Application Template

```python
# backend/main.py
"""
Main FastAPI Application
"""

import os
import uvicorn
from datetime import datetime
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

# Load environment variables
load_dotenv()

# Import custom modules
from database.connection import get_db, init_db_pool, close_db_pool
from integrations.vertex_ai import get_vertex_client

# Initialize FastAPI
app = FastAPI(
    title="Your AI App API",
    description="AI-powered application with multi-agent system",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        # Add production URLs
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic Models
class ProjectCreateRequest(BaseModel):
    name: str
    description: str

# WebSocket Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:
                pass

manager = ConnectionManager()

# Startup and shutdown events
@app.on_event("startup")
async def startup():
    """Initialize services on startup"""
    print("🚀 Starting application...")
    await init_db_pool()
    print("✅ Application started")

@app.on_event("shutdown")
async def shutdown():
    """Cleanup on shutdown"""
    await close_db_pool()
    print("👋 Application shutdown")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# API Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to Your AI App API",
        "docs": "/docs"
    }

# WebSocket endpoint
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            await manager.broadcast(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# Run application
if __name__ == "__main__":
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
```

### 3.4 Database Connection Template

```python
# backend/database/connection.py
"""
Database Connection Manager
Handles PostgreSQL connections (local and Cloud SQL)
"""

import os
from typing import Optional
import asyncpg
from asyncpg import Pool

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "database": os.getenv("DB_NAME", "app_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

CLOUD_SQL_CONNECTION_NAME = os.getenv("CLOUD_SQL_CONNECTION_NAME")

_pool: Optional[Pool] = None

async def init_db_pool() -> Pool:
    """Initialize database connection pool"""
    global _pool

    if _pool is not None:
        return _pool

    # Check if running on Cloud Run with Cloud SQL
    if CLOUD_SQL_CONNECTION_NAME:
        host = f"/cloudsql/{CLOUD_SQL_CONNECTION_NAME}"
        _pool = await asyncpg.create_pool(
            host=host,
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            min_size=2,
            max_size=10,
        )
    else:
        _pool = await asyncpg.create_pool(
            **DB_CONFIG,
            min_size=2,
            max_size=10,
        )

    print(f"✅ Database pool initialized: {DB_CONFIG['database']}")
    return _pool

async def close_db_pool():
    """Close database connection pool"""
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None

def get_pool() -> Pool:
    """Get current database pool"""
    if _pool is None:
        raise RuntimeError("Database pool not initialized")
    return _pool

class Database:
    """Database operations wrapper"""

    async def execute(self, query: str, *args) -> str:
        pool = get_pool()
        async with pool.acquire() as conn:
            return await conn.execute(query, *args)

    async def fetch(self, query: str, *args) -> list:
        pool = get_pool()
        async with pool.acquire() as conn:
            return await conn.fetch(query, *args)

    async def fetchrow(self, query: str, *args):
        pool = get_pool()
        async with pool.acquire() as conn:
            row = await conn.fetchrow(query, *args)
            return dict(row) if row else None

_db: Optional[Database] = None

def get_db() -> Database:
    """Get database instance"""
    global _db
    if _db is None:
        _db = Database()
    return _db
```

### 3.5 Vertex AI Integration Template

```python
# backend/integrations/vertex_ai.py
"""
Google Vertex AI Integration
"""

import os
from typing import Dict, Any, List, Optional
import vertexai
from vertexai.generative_models import GenerativeModel, ChatSession

class VertexAIClient:
    """Vertex AI Client for Gemini models"""

    def __init__(self):
        self.project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
        self.location = os.getenv("VERTEX_AI_LOCATION", "us-central1")
        self.model_name = os.getenv("VERTEX_AI_MODEL", "gemini-1.5-pro")

        # Initialize Vertex AI
        vertexai.init(project=self.project_id, location=self.location)

        # Initialize model
        self.model = GenerativeModel(self.model_name)
        self.chat: Optional[ChatSession] = None

    async def generate_text(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 2048
    ) -> str:
        """Generate text using Vertex AI"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": temperature,
                    "max_output_tokens": max_tokens,
                }
            )
            return response.text
        except Exception as e:
            print(f"Error generating text: {e}")
            raise

    def start_chat(self) -> ChatSession:
        """Start a new chat session"""
        self.chat = self.model.start_chat()
        return self.chat

    async def send_message(self, message: str) -> str:
        """Send message in chat session"""
        if self.chat is None:
            self.start_chat()

        response = self.chat.send_message(message)
        return response.text

# Singleton instance
_vertex_client: Optional[VertexAIClient] = None

def get_vertex_client() -> VertexAIClient:
    """Get Vertex AI client instance"""
    global _vertex_client
    if _vertex_client is None:
        _vertex_client = VertexAIClient()
    return _vertex_client
```

### 3.6 Base Agent Template

```python
# backend/agents/base_agent.py
"""
Base Agent Class for all AI agents
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from datetime import datetime
import uuid

class BaseAgent(ABC):
    """Base class for all AI agents"""

    def __init__(
        self,
        agent_id: str,
        name: str,
        specialization: str,
        division: str
    ):
        self.agent_id = agent_id
        self.name = name
        self.specialization = specialization
        self.division = division
        self.created_at = datetime.utcnow()

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent task

        Args:
            task: Task dictionary with requirements

        Returns:
            Result dictionary with agent output
        """
        pass

    async def log_activity(
        self,
        action: str,
        status: str,
        metadata: Optional[Dict] = None
    ):
        """Log agent activity to database"""
        # Implementation here
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "specialization": self.specialization,
            "division": self.division,
            "created_at": self.created_at.isoformat()
        }
```

### 3.7 Dockerfile Templates

```dockerfile
# backend/Dockerfile (Development)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

```dockerfile
# backend/Dockerfile.prod (Production)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port (Cloud Run uses PORT env var, defaults to 8080)
EXPOSE 8080

# Run the application
# Use PORT environment variable provided by Cloud Run
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
```

---

## 4. Frontend Development

### 4.1 Setup Next.js Frontend

```bash
# Create Next.js app with TypeScript
npx create-next-app@latest frontend --typescript --tailwind --app --src-dir

cd frontend

# Install additional dependencies
npm install \
  @radix-ui/react-dialog \
  @radix-ui/react-dropdown-menu \
  @radix-ui/react-select \
  @radix-ui/react-toast \
  class-variance-authority \
  clsx \
  tailwind-merge \
  lucide-react \
  firebase \
  axios \
  zustand \
  react-hot-toast \
  date-fns

# Install dev dependencies
npm install -D @types/node
```

### 4.2 Frontend Environment Configuration

```bash
# frontend/.env.local.example
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id

NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### 4.3 Firebase Configuration

```typescript
// frontend/lib/firebase.ts
import { initializeApp, getApps } from 'firebase/app';
import { getAuth } from 'firebase/auth';
import { getFirestore } from 'firebase/firestore';
import { getStorage } from 'firebase/storage';

const firebaseConfig = {
  apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY,
  authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID,
  storageBucket: process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.NEXT_PUBLIC_FIREBASE_APP_ID,
};

// Initialize Firebase
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

export const auth = getAuth(app);
export const db = getFirestore(app);
export const storage = getStorage(app);

export default app;
```

### 4.4 API Client Template

```typescript
// frontend/lib/api-client.ts
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { auth } from './firebase';

class APIClient {
  private client: AxiosInstance;
  private wsConnection: WebSocket | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor for adding auth token
    this.client.interceptors.request.use(
      async (config) => {
        const user = auth.currentUser;
        if (user) {
          const token = await user.getIdToken();
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor for error handling
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          auth.signOut();
        }
        return Promise.reject(error);
      }
    );
  }

  // HTTP Methods
  async get<T>(url: string): Promise<T> {
    const response: AxiosResponse<T> = await this.client.get(url);
    return response.data;
  }

  async post<T>(url: string, data: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.post(url, data);
    return response.data;
  }

  async put<T>(url: string, data: any): Promise<T> {
    const response: AxiosResponse<T> = await this.client.put(url, data);
    return response.data;
  }

  async delete<T>(url: string): Promise<T> {
    const response: AxiosResponse<T> = await this.client.delete(url);
    return response.data;
  }

  // WebSocket connection
  connectWebSocket(onMessage: (data: any) => void) {
    if (this.wsConnection) {
      return;
    }

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL!;
    this.wsConnection = new WebSocket(wsUrl);

    this.wsConnection.onopen = () => {
      console.log('WebSocket connected');
    };

    this.wsConnection.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onMessage(data);
    };

    this.wsConnection.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    this.wsConnection.onclose = () => {
      console.log('WebSocket disconnected');
      this.wsConnection = null;
    };
  }

  disconnectWebSocket() {
    if (this.wsConnection) {
      this.wsConnection.close();
      this.wsConnection = null;
    }
  }
}

export const apiClient = new APIClient();
```

### 4.5 Firebase App Hosting Configuration

```yaml
# frontend/apphosting.yaml
runConfig:
  concurrency: 100
  cpu: 1
  maxInstances: 10
  minInstances: 0
  memory: 512Mi
  timeoutSeconds: 60

env:
  - variable: NODE_ENV
    value: production
  - variable: NEXT_PUBLIC_FIREBASE_PROJECT_ID
    value: your-project-id
  - variable: NEXT_PUBLIC_FIREBASE_API_KEY
    secret: FIREBASE_API_KEY
  - variable: NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
    value: your-project.firebaseapp.com
  - variable: NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
    value: your-project.appspot.com
  - variable: NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
    secret: FIREBASE_MESSAGING_SENDER_ID
  - variable: NEXT_PUBLIC_FIREBASE_APP_ID
    secret: FIREBASE_APP_ID
  - variable: NEXT_PUBLIC_API_URL
    value: https://your-backend.run.app
  - variable: NEXT_PUBLIC_WS_URL
    value: wss://your-backend.run.app/ws
```

---

## 5. AI Agent Development

### 5.1 Agent Development Workflow

1. **Plan Agent Divisions**
   - Identify required agent specializations
   - Group agents by functional domains
   - Define agent responsibilities

2. **Create Agent Structure**

```python
# backend/agents/[division]/[agent_name].py
from agents.base_agent import BaseAgent
from integrations.vertex_ai import get_vertex_client
from typing import Dict, Any

class AgentName(BaseAgent):
    """Agent description and purpose"""

    def __init__(self):
        super().__init__(
            agent_id="agent-id",
            name="Agent Name",
            specialization="What this agent does",
            division="Division Name"
        )
        self.vertex = get_vertex_client()

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute agent-specific task

        Args:
            task: Task dictionary containing:
                - task_id: Unique task identifier
                - description: Task description
                - requirements: Task requirements
                - context: Additional context

        Returns:
            Result dictionary containing:
                - status: "success" or "failed"
                - output: Agent output
                - artifacts: List of created artifacts
        """
        try:
            # Log activity start
            await self.log_activity(
                action=f"Executing task: {task.get('task_id')}",
                status="started"
            )

            # Build prompt for Vertex AI
            prompt = self._build_prompt(task)

            # Call Vertex AI
            response = await self.vertex.generate_text(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2048
            )

            # Process response
            result = self._process_response(response, task)

            # Log activity completion
            await self.log_activity(
                action=f"Completed task: {task.get('task_id')}",
                status="completed",
                metadata=result
            )

            return {
                "status": "success",
                "output": result,
                "agent": self.to_dict()
            }

        except Exception as e:
            # Log error
            await self.log_activity(
                action=f"Failed task: {task.get('task_id')}",
                status="failed",
                metadata={"error": str(e)}
            )

            return {
                "status": "failed",
                "error": str(e),
                "agent": self.to_dict()
            }

    def _build_prompt(self, task: Dict[str, Any]) -> str:
        """Build prompt for Vertex AI based on task"""
        return f"""
        You are {self.name}, a specialized AI agent for {self.specialization}.

        Task: {task.get('description')}
        Requirements: {task.get('requirements', 'None specified')}
        Context: {task.get('context', 'None provided')}

        Please provide a detailed response for this task.
        """

    def _process_response(
        self,
        response: str,
        task: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process Vertex AI response"""
        return {
            "content": response,
            "task_id": task.get('task_id'),
            "timestamp": datetime.utcnow().isoformat()
        }
```

### 5.2 LangGraph Workflow Template

```python
# backend/graph/workflow.py
"""
LangGraph Workflow for Multi-Agent Orchestration
"""

from typing import TypedDict, List, Dict, Any
from langgraph.graph import StateGraph, END
from agents.base_agent import BaseAgent

# Define state
class AgentState(TypedDict):
    """State for agent workflow"""
    messages: List[Dict[str, Any]]
    current_agent: str
    task_status: str
    artifacts: List[Dict[str, Any]]
    context: Dict[str, Any]

# Define workflow
def create_agent_workflow(agents: List[BaseAgent]):
    """Create LangGraph workflow for agent orchestration"""

    workflow = StateGraph(AgentState)

    # Define nodes (agent functions)
    async def agent_node(state: AgentState, agent: BaseAgent):
        """Execute single agent"""
        task = {
            "task_id": state.get("task_id"),
            "description": state.get("description"),
            "context": state.get("context"),
        }

        result = await agent.execute(task)

        return {
            **state,
            "messages": state["messages"] + [result],
            "current_agent": agent.name,
            "artifacts": state["artifacts"] + result.get("artifacts", [])
        }

    # Add nodes for each agent
    for agent in agents:
        workflow.add_node(
            agent.name,
            lambda state: agent_node(state, agent)
        )

    # Define routing logic
    def should_continue(state: AgentState) -> str:
        """Determine next agent or end workflow"""
        if state["task_status"] == "completed":
            return END
        # Add custom routing logic here
        return "next_agent_name"

    # Add edges
    workflow.add_conditional_edges(
        "agent_1",
        should_continue,
        {
            "next": "agent_2",
            END: END
        }
    )

    # Set entry point
    workflow.set_entry_point("agent_1")

    return workflow.compile()
```

### 5.3 Agent Registry Pattern

```python
# backend/agents/registry.py
"""
Agent Registry for managing all agents
"""

from typing import Dict, List, Optional
from agents.base_agent import BaseAgent

class AgentRegistry:
    """Registry for all AI agents"""

    def __init__(self):
        self.agents: Dict[str, BaseAgent] = {}
        self.agents_by_division: Dict[str, List[BaseAgent]] = {}

    def register(self, agent: BaseAgent):
        """Register an agent"""
        self.agents[agent.agent_id] = agent

        if agent.division not in self.agents_by_division:
            self.agents_by_division[agent.division] = []
        self.agents_by_division[agent.division].append(agent)

    def get_agent(self, agent_id: str) -> Optional[BaseAgent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)

    def get_agents_by_division(self, division: str) -> List[BaseAgent]:
        """Get all agents in a division"""
        return self.agents_by_division.get(division, [])

    def get_all_agents(self) -> List[BaseAgent]:
        """Get all registered agents"""
        return list(self.agents.values())

# Singleton instance
_registry: Optional[AgentRegistry] = None

def get_agent_registry() -> AgentRegistry:
    """Get agent registry instance"""
    global _registry
    if _registry is None:
        _registry = AgentRegistry()
    return _registry
```

---

## 6. Database Design

### 6.1 Database Schema Template

```sql
-- database/schema.sql
-- PostgreSQL schema for multi-tenant SaaS architecture

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tenants (Companies)
CREATE TABLE tenants (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(255) NOT NULL,
    subdomain VARCHAR(100) UNIQUE NOT NULL,
    plan_tier VARCHAR(50) NOT NULL DEFAULT 'free',
    settings JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT plan_tier_check CHECK (plan_tier IN ('free', 'pro', 'enterprise'))
);

CREATE INDEX idx_tenants_subdomain ON tenants(subdomain);

-- Users (with tenant association)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    firebase_uid VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    role VARCHAR(50) NOT NULL DEFAULT 'member',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_login_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT role_check CHECK (role IN ('admin', 'member', 'viewer')),
    UNIQUE(tenant_id, email)
);

CREATE INDEX idx_users_tenant_id ON users(tenant_id);
CREATE INDEX idx_users_firebase_uid ON users(firebase_uid);

-- Projects
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tenant_id UUID NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT status_check CHECK (status IN ('active', 'completed', 'archived'))
);

CREATE INDEX idx_projects_tenant_id ON projects(tenant_id);
CREATE INDEX idx_projects_user_id ON projects(user_id);

-- Tasks
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',
    assigned_agent VARCHAR(100),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP WITH TIME ZONE,

    CONSTRAINT status_check CHECK (status IN ('pending', 'in_progress', 'completed', 'failed')),
    CONSTRAINT priority_check CHECK (priority IN ('low', 'medium', 'high', 'urgent'))
);

CREATE INDEX idx_tasks_project_id ON tasks(project_id);
CREATE INDEX idx_tasks_status ON tasks(status);

-- Agent Activity Logs
CREATE TABLE agent_activities (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    task_id UUID REFERENCES tasks(id) ON DELETE SET NULL,
    agent_name VARCHAR(100) NOT NULL,
    agent_division VARCHAR(50) NOT NULL,
    action VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    duration_ms INTEGER,

    CONSTRAINT activity_status_check CHECK (status IN ('started', 'in_progress', 'completed', 'failed'))
);

CREATE INDEX idx_agent_activities_project_id ON agent_activities(project_id);
CREATE INDEX idx_agent_activities_timestamp ON agent_activities(timestamp DESC);

-- Functions for automatic timestamp updates
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Apply update triggers
CREATE TRIGGER update_tenants_updated_at BEFORE UPDATE ON tenants
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_projects_updated_at BEFORE UPDATE ON projects
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tasks_updated_at BEFORE UPDATE ON tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Row Level Security (RLS) for multi-tenant isolation
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_activities ENABLE ROW LEVEL SECURITY;
```

### 6.2 Repository Pattern

```python
# backend/database/repositories.py
"""
Repository pattern for database operations
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
from database.connection import get_db

class BaseRepository:
    """Base repository with common operations"""

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.db = get_db()

    async def create(self, data: Dict[str, Any]) -> Dict:
        """Create new record"""
        columns = ", ".join(data.keys())
        placeholders = ", ".join([f"${i+1}" for i in range(len(data))])
        values = list(data.values())

        query = f"""
            INSERT INTO {self.table_name} ({columns})
            VALUES ({placeholders})
            RETURNING *
        """

        return await self.db.fetchrow(query, *values)

    async def get_by_id(self, id: str) -> Optional[Dict]:
        """Get record by ID"""
        query = f"SELECT * FROM {self.table_name} WHERE id = $1"
        return await self.db.fetchrow(query, id)

    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict]:
        """Update record"""
        set_clause = ", ".join([f"{k} = ${i+2}" for i, k in enumerate(data.keys())])
        values = [id] + list(data.values())

        query = f"""
            UPDATE {self.table_name}
            SET {set_clause}
            WHERE id = $1
            RETURNING *
        """

        return await self.db.fetchrow(query, *values)

    async def delete(self, id: str) -> bool:
        """Delete record"""
        query = f"DELETE FROM {self.table_name} WHERE id = $1"
        result = await self.db.execute(query, id)
        return result == "DELETE 1"

class ProjectRepository(BaseRepository):
    """Repository for projects"""

    def __init__(self):
        super().__init__("projects")

    async def get_by_tenant(self, tenant_id: str) -> List[Dict]:
        """Get all projects for a tenant"""
        query = """
            SELECT * FROM projects
            WHERE tenant_id = $1
            ORDER BY created_at DESC
        """
        return await self.db.fetch(query, tenant_id)

class TaskRepository(BaseRepository):
    """Repository for tasks"""

    def __init__(self):
        super().__init__("tasks")

    async def get_by_project(self, project_id: str) -> List[Dict]:
        """Get all tasks for a project"""
        query = """
            SELECT * FROM tasks
            WHERE project_id = $1
            ORDER BY created_at DESC
        """
        return await self.db.fetch(query, project_id)
```

---

## 7. Deployment Strategy

### 7.1 Firebase Deployment Script

```bash
#!/bin/bash
# deploy-firebase.sh

##############################################################################
# Firebase App Hosting + Cloud Run Deployment
# Frontend: Firebase App Hosting (Next.js optimized)
# Backend: Google Cloud Run (Python FastAPI)
##############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ID="your-project-id"
REGION="us-central1"
BACKEND_SERVICE="your-backend-service"
SQL_INSTANCE="your-db-instance"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Deployment (Firebase + Cloud Run)       ║${NC}"
echo -e "${BLUE}║   Project: $PROJECT_ID              ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════════╝${NC}"
echo ""

# Function to print step headers
print_step() {
    echo ""
    echo -e "${BLUE}▶ $1${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

# Function to print success
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to print error
print_error() {
    echo -e "${RED}✗ $1${NC}"
}

##############################################################################
# Step 1: Verify Prerequisites
##############################################################################

print_step "Step 1: Verifying Prerequisites"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    print_error "gcloud CLI is not installed"
    exit 1
fi
print_success "gcloud CLI installed"

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    print_error "Firebase CLI is not installed"
    exit 1
fi
print_success "Firebase CLI installed"

# Check authentication
ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1)
print_success "Authenticated as: $ACCOUNT"

# Set project
gcloud config set project $PROJECT_ID --quiet
print_success "Project set to: $PROJECT_ID"

##############################################################################
# Step 2: Enable Required APIs
##############################################################################

print_step "Step 2: Enabling Required Google Cloud APIs"

APIS=(
    "run.googleapis.com"
    "cloudbuild.googleapis.com"
    "artifactregistry.googleapis.com"
    "sqladmin.googleapis.com"
    "secretmanager.googleapis.com"
    "firebase.googleapis.com"
    "firebasehosting.googleapis.com"
)

for api in "${APIS[@]}"; do
    gcloud services enable $api --quiet
done

print_success "All required APIs enabled"

##############################################################################
# Step 3: Build and Deploy Backend to Cloud Run
##############################################################################

print_step "Step 3: Building and Deploying Backend to Cloud Run"

cd backend

# Build Docker image
BACKEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/containers/$BACKEND_SERVICE:latest"

# Create Artifact Registry repository if needed
gcloud artifacts repositories create containers \
    --repository-format=docker \
    --location=$REGION \
    2>/dev/null || print_warning "Repository already exists"

# Temporarily rename Dockerfile for build
if [ -f "Dockerfile" ]; then
    mv Dockerfile Dockerfile.backup
fi
cp Dockerfile.prod Dockerfile

# Build and push
gcloud builds submit \
    --tag $BACKEND_IMAGE \
    --timeout=20m

# Restore Dockerfile
rm Dockerfile
if [ -f "Dockerfile.backup" ]; then
    mv Dockerfile.backup Dockerfile
fi

print_success "Backend container built"

# Deploy to Cloud Run
gcloud run deploy $BACKEND_SERVICE \
    --image $BACKEND_IMAGE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$SQL_INSTANCE" \
    --add-cloudsql-instances="$PROJECT_ID:$REGION:$SQL_INSTANCE" \
    --memory=2Gi \
    --cpu=2 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300 \
    --port=8080

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
    --region $REGION \
    --format='value(status.url)')

print_success "Backend deployed to: $BACKEND_URL"

cd ..

##############################################################################
# Step 4: Update Frontend Configuration
##############################################################################

print_step "Step 4: Updating Frontend Configuration"

cd frontend

# Update apphosting.yaml with actual backend URL
cat > apphosting.yaml <<EOF
runConfig:
  concurrency: 100
  cpu: 1
  maxInstances: 10
  minInstances: 0
  memory: 512Mi
  timeoutSeconds: 60

env:
  - variable: NODE_ENV
    value: production
  - variable: NEXT_PUBLIC_API_URL
    value: $BACKEND_URL
  - variable: NEXT_PUBLIC_WS_URL
    value: wss://${BACKEND_URL#https://}/ws
EOF

print_success "Frontend configuration updated"

cd ..

##############################################################################
# Deployment Summary
##############################################################################

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   🎉 Deployment Complete!                 ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Backend (Cloud Run):${NC}"
echo "  API URL:  $BACKEND_URL"
echo "  API Docs: $BACKEND_URL/docs"
echo ""
echo -e "${BLUE}Frontend (Firebase App Hosting):${NC}"
echo "  Deploy: firebase deploy --only hosting"
echo "  Or connect via Firebase Console"
echo ""
```

### 7.2 Make Scripts Executable

```bash
chmod +x deploy-firebase.sh
```

---

## 8. Testing & Quality Assurance

### 8.1 Backend Testing Setup

```python
# backend/tests/test_agents.py
import pytest
from agents.base_agent import BaseAgent

@pytest.mark.asyncio
async def test_agent_execution():
    """Test agent execution"""
    # Test implementation
    pass

@pytest.mark.asyncio
async def test_agent_error_handling():
    """Test agent error handling"""
    # Test implementation
    pass
```

### 8.2 Frontend Testing Setup

```typescript
// frontend/__tests__/components/Button.test.tsx
import { render, screen } from '@testing-library/react';
import Button from '@/components/ui/Button';

describe('Button', () => {
  it('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });
});
```

---

## 9. Best Practices Checklist

### 9.1 Code Quality

- [ ] **Type Safety**
  - Use TypeScript for frontend
  - Use Pydantic for backend data validation
  - Define clear interfaces and types

- [ ] **Error Handling**
  - Implement try-catch blocks in all async operations
  - Log errors comprehensively
  - Provide user-friendly error messages

- [ ] **Code Organization**
  - Follow single responsibility principle
  - Use consistent naming conventions
  - Keep files under 300 lines

- [ ] **Documentation**
  - Add docstrings to all functions
  - Document API endpoints
  - Create architecture diagrams

### 9.2 Security

- [ ] **Authentication**
  - Implement Firebase Authentication
  - Use JWT tokens for API calls
  - Validate tokens on backend

- [ ] **Authorization**
  - Implement role-based access control (RBAC)
  - Use Row Level Security (RLS) in database
  - Validate permissions on all operations

- [ ] **Data Protection**
  - Never commit secrets to git
  - Use environment variables
  - Encrypt sensitive data in database

- [ ] **API Security**
  - Implement rate limiting
  - Validate all inputs
  - Use HTTPS only in production

### 9.3 Performance

- [ ] **Database**
  - Use connection pooling
  - Add indexes on frequently queried columns
  - Optimize N+1 queries

- [ ] **API**
  - Implement caching where appropriate
  - Use pagination for list endpoints
  - Optimize payload sizes

- [ ] **Frontend**
  - Implement code splitting
  - Optimize images
  - Use React.memo for expensive components
  - Implement loading states

### 9.4 AI/ML Specific

- [ ] **Prompt Engineering**
  - Version control prompts
  - Test prompts with various inputs
  - Implement prompt templates

- [ ] **Model Management**
  - Abstract model calls behind interface
  - Implement retry logic with exponential backoff
  - Monitor token usage and costs

- [ ] **Agent Orchestration**
  - Log all agent activities
  - Implement timeout handling
  - Track agent performance metrics

---

## 10. Common Pitfalls & Solutions

### 10.1 Deployment Issues

**Issue**: Container fails to start in Cloud Run
```
Solution:
- Ensure CMD uses shell form for environment variable expansion
- Use PORT environment variable provided by Cloud Run
- Check logs: gcloud run logs read --service=SERVICE_NAME
```

**Issue**: Database connection fails
```
Solution:
- Verify Cloud SQL instance is running
- Check connection name format: PROJECT:REGION:INSTANCE
- Ensure Cloud SQL Admin API is enabled
- Verify IAM permissions
```

### 10.2 Dependency Conflicts

**Issue**: Package version conflicts
```
Solution:
- Use version ranges (>=) instead of exact versions (==)
- Test in virtual environment before deployment
- Pin only critical dependencies
- Use pip-compile for lock files
```

### 10.3 Firebase Authentication

**Issue**: CORS errors with Firebase Auth
```
Solution:
- Add domain to Firebase authorized domains
- Configure CORS in FastAPI middleware
- Use proper credentials in requests
```

### 10.4 Vertex AI Integration

**Issue**: Quota exceeded errors
```
Solution:
- Implement exponential backoff retry logic
- Use rate limiting on API endpoints
- Monitor quota usage in Cloud Console
- Request quota increase if needed
```

### 10.5 WebSocket Connection

**Issue**: WebSocket disconnects frequently
```
Solution:
- Implement reconnection logic
- Send heartbeat/ping messages
- Handle connection state properly
- Use connection pooling
```

---

## Appendix A: Environment Variables Reference

### Backend Environment Variables

```bash
# Firebase
FIREBASE_PROJECT_ID=
FIREBASE_SERVICE_ACCOUNT_PATH=

# Google Cloud
GOOGLE_CLOUD_PROJECT=
GOOGLE_APPLICATION_CREDENTIALS=

# Database
DB_HOST=
DB_PORT=
DB_NAME=
DB_USER=
DB_PASSWORD=
CLOUD_SQL_CONNECTION_NAME=

# API
API_HOST=
API_PORT=

# Vertex AI
VERTEX_AI_LOCATION=
VERTEX_AI_MODEL=
```

### Frontend Environment Variables

```bash
# Firebase
NEXT_PUBLIC_FIREBASE_API_KEY=
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=
NEXT_PUBLIC_FIREBASE_PROJECT_ID=
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=
NEXT_PUBLIC_FIREBASE_APP_ID=

# API
NEXT_PUBLIC_API_URL=
NEXT_PUBLIC_WS_URL=
```

---

## Appendix B: Useful Commands

### Development

```bash
# Backend
cd backend
source venv/bin/activate
python main.py

# Frontend
cd frontend
npm run dev

# Database
psql -h localhost -U postgres -d database_name
```

### Deployment

```bash
# Deploy backend
gcloud run deploy SERVICE --image IMAGE_URL

# Deploy frontend
firebase deploy --only hosting

# View logs
gcloud run logs read --service=SERVICE_NAME
```

### Database

```bash
# Connect to Cloud SQL
gcloud sql connect INSTANCE_NAME --user=postgres

# Create migration
python scripts/create_migration.py

# Run migrations
python scripts/run_migrations.py
```

---

## Appendix C: Resources

### Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)
- [Google Vertex AI Documentation](https://cloud.google.com/vertex-ai/docs)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
- [Firebase Documentation](https://firebase.google.com/docs)

### Tools
- [VS Code](https://code.visualstudio.com/)
- [Postman](https://www.postman.com/) (API testing)
- [pgAdmin](https://www.pgadmin.org/) (PostgreSQL GUI)

---

## Template Version

**Version**: 1.0
**Last Updated**: November 2025
**Maintained By**: Bright Tier Solutions
**Based On**: Velo - The AI Agency OS

---

## Support

For questions or issues with this template:
1. Review the documentation thoroughly
2. Check common pitfalls section
3. Consult the architecture documentation
4. Contact the development team lead

---

**End of Master Template**
