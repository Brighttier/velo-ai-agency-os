# Velo - The AI Agency OS

A high-velocity SaaS platform where users command 51 specialized AI Agents to plan, build, test, and deploy software—fully automated.

**Project**: velo-479115 (Google Cloud Platform)

## 🚀 Quick Start

### Prerequisites
- Node.js 20+
- npm 10+
- Python 3.11+
- Google Cloud Account with billing enabled
- Firebase Account
- gcloud CLI installed and authenticated

### Installation

```bash
# Clone the repository
cd velo-monorepo

# Install frontend dependencies
cd frontend
npm install

# Install backend dependencies
cd ../backend
pip3 install fastapi uvicorn python-dotenv pydantic firebase-admin
```

### Firebase Setup

**Automated Setup (Recommended):**
```bash
# From the project root
./setup-firebase.sh
```

This script will:
- Enable required Google Cloud APIs
- Create service account (velo-backend@velo-479115.iam.gserviceaccount.com)
- Grant necessary permissions
- Generate service account key
- Create backend/.env file

**Manual Setup:**
See [FIREBASE_SETUP.md](../FIREBASE_SETUP.md) for detailed instructions.

**Get Firebase Web App Config:**
```bash
./get-firebase-config.sh
```

Then update `frontend/.env.local` with your Firebase credentials:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=velo-479115.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=velo-479115
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=velo-479115.firebasestorage.app
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

**Enable Email/Password Authentication:**
1. Go to [Firebase Console](https://console.firebase.google.com/project/velo-479115/authentication)
2. Click "Get started"
3. Enable "Email/Password" sign-in method

### Development

**Terminal 1 - Backend:**
```bash
cd backend
python3 main.py
```
Backend runs on http://localhost:8000
API docs available at http://localhost:8000/docs

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```
Frontend runs on http://localhost:3000

### First Time Setup

1. **Run Firebase setup script:**
   ```bash
   ./setup-firebase.sh
   ```

2. **Get Firebase web config and update frontend/.env.local**

3. **Enable Email/Password auth in Firebase Console**

4. **Start both servers** (backend and frontend)

5. **Create your account:**
   - Visit http://localhost:3000
   - You'll be redirected to /login
   - Click "Sign up"
   - Enter company name, email, and password
   - This creates both Firebase user and tenant account

6. **Create your first project:**
   - Click "New Project" button
   - Enter project name and description
   - Watch AI agents work in real-time via WebSocket updates

## 🏗️ Architecture

### Monorepo Structure
```
velo-monorepo/
├── frontend/                # Next.js 16 App
│   ├── app/                # App Router pages
│   ├── components/         # React components
│   ├── lib/               # Utilities and API client
│   ├── hooks/             # Custom React hooks (useWebSocket)
│   └── contexts/          # React Context (AuthContext)
├── backend/               # Python FastAPI + LangGraph
│   ├── agents/           # AI agent definitions
│   ├── database/         # Database schema and migrations
│   ├── graph/            # LangGraph workflow definitions
│   ├── integrations/     # External service integrations
│   ├── scripts/          # Utility scripts
│   └── main.py           # FastAPI application entry point
├── database/             # PostgreSQL schema
└── deploy-to-cloud.sh   # Automated deployment script
```

### Technology Stack
- **Frontend**: Next.js 16, React 19, TypeScript, Tailwind CSS v4, Shadcn UI
- **Backend**: Python 3.11, FastAPI, Firebase Genkit, LangGraph
- **AI**: Google Vertex AI (Gemini 1.5 Pro/Flash)
- **Database**: Cloud SQL (PostgreSQL 15)
- **Storage**: Google Cloud Storage
- **Auth**: Firebase Authentication
- **Real-time**: WebSocket (FastAPI WebSocket support)
- **Deployment**: Google Cloud Run
- **PM Tool**: Plane.so (Community Edition)

### System Flow

1. **User submits project prompt** → Frontend (New Project Modal)
2. **Frontend sends to backend** → POST /api/project/create
3. **Backend starts planning phase** → Background task
4. **AI agents work in parallel** → LangGraph workflows
5. **Real-time updates** → WebSocket broadcasts to frontend
6. **Agents complete tasks**:
   - Oracle generates PRD
   - Neuron creates tasks
   - Atlas syncs to Plane
   - Engineering agents write code
   - Testing agents run tests
   - Forge deploys to staging
7. **User reviews artifacts** → Confluence-style portal
8. **Export or deploy** → Download ZIP or deploy to production

## 🤖 The 51 AI Agents

### Engineering Division
- **Pixel** - Frontend Developer
- **Atlas** - Backend Architect
- **Nova** - Mobile App Builder
- **Neuron** - AI Engineer
- **Forge** - DevOps Automator
- **Blitz** - Rapid Prototyper
- **Sage** - Senior Developer

### Design Division
- **Aurora** - UI Designer
- **Echo** - UX Researcher
- **Compass** - UX Architect
- **Ember** - Brand Guardian
- **Canvas** - Visual Storyteller
- **Spark** - Whimsy Injector

### Marketing Division
- **Rocket** - Growth Hacker
- **Quill** - Content Creator
- **Chirp** - Twitter Engager
- **Rhythm** - TikTok Strategist
- **Prism** - Instagram Curator
- **Pulse** - Reddit Community Builder
- **Phoenix** - App Store Optimizer
- **Nexus** - Social Media Strategist

### Product Division
- **Sprint** - Sprint Prioritizer
- **Horizon** - Trend Researcher
- **Synthesis** - Feedback Synthesizer

### Project Management Division
- **Maestro** - Studio Producer
- **Shepherd** - Project Shepherd
- **Clockwork** - Studio Operations
- **Prism Lab** - Experiment Tracker
- **Oracle** - Senior Project Manager

### Testing Division
- **Sherlock** - Evidence Collector
- **Gatekeeper** - Reality Checker
- **Verdict** - Test Results Analyzer
- **Benchmark** - Performance Benchmarker
- **Postman** - API Tester
- **Forge Tester** - Tool Evaluator
- **Flow** - Workflow Optimizer

### Support Division
- **Beacon** - Support Responder
- **Insight** - Analytics Reporter
- **Ledger** - Finance Tracker
- **Sentinel** - Infrastructure Maintainer
- **Shield** - Legal Compliance Checker
- **Summit** - Executive Summary Generator

### Spatial Computing Division
- **Hologram** - XR Interface Architect
- **Titanium** - macOS Spatial/Metal Engineer
- **Immerse** - XR Immersive Developer
- **Gesture** - XR Cockpit Interaction Specialist
- **Vision** - visionOS Spatial Engineer
- **Terminal** - Terminal Integration Specialist

### Specialized Division
- **Conductor** - Agents Orchestrator
- **Prism Analytics** - Data Analytics Reporter
- **Index** - LSP/Index Engineer

## 📦 Features

- ✨ 51 uniquely-named AI agents with distinct personalities
- 📊 Confluence-style artifact portal with rich viewing
- 🏢 Multi-tenant SaaS architecture
- 🔄 Complete automation from prompt to deployment
- 👀 Real-time visibility into agent work via WebSocket
- 📈 Usage tracking and analytics
- 🔐 Enterprise-grade security with Firebase Auth
- 💾 Version control for all artifacts
- 💬 Collaboration with comments and sharing
- 📥 Multiple export formats (ZIP, PDF, individual files)

## 🌟 Unique Selling Points

1. **Headless Complexity** - Users see simple interfaces; AI handles complex tools
2. **Parallel Processing** - Watch multiple agents work simultaneously
3. **Beautiful Artifacts** - Confluence-style documentation portal
4. **Complete Packages** - Delivery includes strategy, architecture, code, tests, docs
5. **Multi-Tenant Ready** - Built for Bright Tier Solutions + external clients

## 🚀 Production Deployment

### Prerequisites
- Google Cloud account with billing enabled
- gcloud CLI installed and authenticated
- Docker installed (for local testing)
- Domain name (optional, for custom domains)

### Automated Deployment

The project includes a comprehensive deployment script that handles everything:

```bash
# Make script executable
chmod +x deploy-to-cloud.sh

# Run deployment
./deploy-to-cloud.sh
```

This script will:
1. ✅ Verify prerequisites (gcloud CLI, authentication)
2. ✅ Enable required GCP APIs
3. ✅ Create Artifact Registry for Docker images
4. ✅ Build and push frontend container
5. ✅ Build and push backend container
6. ✅ Create Cloud SQL PostgreSQL instance
7. ✅ Deploy backend to Cloud Run
8. ✅ Deploy frontend to Cloud Run
9. ✅ Provide URLs and next steps

### Manual Deployment Steps

If you prefer manual deployment, see [deploy-to-cloud.sh](deploy-to-cloud.sh) for the complete sequence.

### Post-Deployment

After deployment completes:

1. **Add Firebase Authorized Domains:**
   - Go to [Firebase Console → Authentication → Settings](https://console.firebase.google.com/project/velo-479115/authentication/settings)
   - Add your Cloud Run URLs to authorized domains

2. **Configure Custom Domain (Optional):**
   ```bash
   gcloud run domain-mappings create \
     --service=velo-frontend \
     --domain=your-domain.com \
     --region=us-central1
   ```

3. **Set up Cloud CDN (Optional):**
   - Improves global performance
   - Reduces costs with caching

4. **Configure Cloud SQL Backups:**
   ```bash
   gcloud sql instances patch velo-db \
     --backup-start-time=03:00 \
     --enable-bin-log
   ```

### Monitoring

**View Logs:**
```bash
# Frontend logs
gcloud run logs read --service=velo-frontend --region=us-central1

# Backend logs
gcloud run logs read --service=velo-backend --region=us-central1
```

**Update Deployment:**
```bash
# Rebuild and redeploy frontend
cd frontend
gcloud builds submit --tag us-central1-docker.pkg.dev/velo-479115/velo-docker/velo-frontend:latest
gcloud run deploy velo-frontend \
  --image us-central1-docker.pkg.dev/velo-479115/velo-docker/velo-frontend:latest \
  --region us-central1

# Rebuild and redeploy backend
cd backend
gcloud builds submit --tag us-central1-docker.pkg.dev/velo-479115/velo-docker/velo-backend:latest
gcloud run deploy velo-backend \
  --image us-central1-docker.pkg.dev/velo-479115/velo-docker/velo-backend:latest \
  --region us-central1
```

## 🛠️ Development Commands

### Frontend
```bash
cd frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run start        # Start production server
npm run lint         # Run ESLint
npm run type-check   # Run TypeScript checks
```

### Backend
```bash
cd backend
python3 main.py      # Start development server
uvicorn main:app --reload  # Alternative with hot reload

# Testing
pytest               # Run tests
pytest --cov         # Run tests with coverage

# Code quality
black .              # Format code
flake8 .             # Lint code
mypy .               # Type checking
```

## 📚 API Documentation

Once the backend is running, visit:
- **Interactive API Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### Key Endpoints

**Authentication:**
- `POST /api/tenant/create` - Create tenant during signup

**Projects:**
- `POST /api/project/create` - Create new project (starts planning phase)
- `GET /api/project/{id}` - Get project details
- `GET /api/project/{id}/artifacts` - List project artifacts

**WebSocket:**
- `WS /ws` - Real-time updates for agent activities

## 🐛 Troubleshooting

### Frontend Issues

**"Firebase: Error (auth/invalid-api-key)"**
- Ensure `.env.local` exists in frontend directory
- Verify Firebase config values are correct
- Restart Next.js dev server after creating/updating `.env.local`

**"Module not found: firebase"**
```bash
cd frontend
npm install firebase
```

### Backend Issues

**"ModuleNotFoundError"**
```bash
cd backend
pip3 install -r requirements.txt
```

**"Port 8000 already in use"**
```bash
lsof -ti:8000 | xargs kill -9
python3 main.py
```

**"Firebase Admin SDK errors"**
- Verify `service-account.json` exists in backend directory
- Check `GOOGLE_APPLICATION_CREDENTIALS` in backend/.env
- Ensure service account has correct permissions

### Deployment Issues

**"Billing account not found"**
- Enable billing in Google Cloud Console
- Link billing account to project velo-479115

**"Insufficient permissions"**
```bash
gcloud auth application-default login
gcloud config set project velo-479115
```

## 📖 Additional Resources

- [Firebase Setup Guide](../FIREBASE_SETUP.md)
- [Google Cloud Console](https://console.cloud.google.com/welcome?project=velo-479115)
- [Firebase Console](https://console.firebase.google.com/project/velo-479115)
- [Cloud Run Documentation](https://cloud.google.com/run/docs)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Next.js Documentation](https://nextjs.org/docs)

## 📄 License

Proprietary - Bright Tier Solutions

## 🤝 Contributing

Internal project for Bright Tier Solutions team members.

---

Built with ❤️ by Bright Tier Solutions
