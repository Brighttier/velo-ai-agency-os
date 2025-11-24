#!/bin/bash

##############################################################################
# Velo - Firebase App Hosting + Cloud Run Deployment
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

PROJECT_ID="velo-479115"
REGION="us-central1"
BACKEND_SERVICE="velo-backend"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Velo Deployment (Firebase + Cloud Run)  ║${NC}"
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
    print_error "gcloud CLI is not installed. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi
print_success "gcloud CLI installed"

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    print_error "Firebase CLI is not installed."
    echo "Install: npm install -g firebase-tools"
    exit 1
fi
print_success "Firebase CLI installed"

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | head -n 1 > /dev/null 2>&1; then
    print_error "Not authenticated with gcloud"
    echo "Run: gcloud auth login"
    exit 1
fi
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
    "firestore.googleapis.com"
    "storage-api.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "Enabling $api..."
    gcloud services enable $api --quiet
done

print_success "All required APIs enabled"

##############################################################################
# Step 3: Create Artifact Registry Repository (for backend)
##############################################################################

print_step "Step 3: Setting up Artifact Registry"

if gcloud artifacts repositories describe velo-docker \
    --location=$REGION &> /dev/null; then
    print_warning "Artifact Registry repository already exists"
else
    gcloud artifacts repositories create velo-docker \
        --repository-format=docker \
        --location=$REGION \
        --description="Velo container images"
    print_success "Artifact Registry repository created"
fi

##############################################################################
# Step 4: Create Cloud SQL PostgreSQL Instance
##############################################################################

print_step "Step 4: Setting up Cloud SQL PostgreSQL"

SQL_INSTANCE="velo-db"

if gcloud sql instances describe $SQL_INSTANCE &> /dev/null; then
    print_warning "Cloud SQL instance already exists"
else
    gcloud sql instances create $SQL_INSTANCE \
        --database-version=POSTGRES_15 \
        --tier=db-f1-micro \
        --region=$REGION \
        --root-password=$(openssl rand -base64 32)

    print_success "Cloud SQL instance created"
fi

# Create database
gcloud sql databases create velo --instance=$SQL_INSTANCE 2>/dev/null || print_warning "Database already exists"

print_success "Database configured"

##############################################################################
# Step 5: Build and Deploy Backend to Cloud Run
##############################################################################

print_step "Step 5: Building and Deploying Backend to Cloud Run"

cd backend

# Create production Dockerfile if not exists
if [ ! -f "Dockerfile.prod" ]; then
    cat > Dockerfile.prod <<'EOF'
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
CMD ["uvicorn", "main_enhanced:app", "--host", "0.0.0.0", "--port", "8000"]
EOF
    print_success "Created backend Dockerfile"
fi

# Build and push
BACKEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/velo-docker/$BACKEND_SERVICE:latest"

# Temporarily rename Dockerfile for gcloud builds
if [ -f "Dockerfile" ]; then
    mv Dockerfile Dockerfile.backup
fi
cp Dockerfile.prod Dockerfile

gcloud builds submit \
    --tag $BACKEND_IMAGE \
    --timeout=20m

# Restore original Dockerfile
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
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID,CLOUD_SQL_CONNECTION_NAME=$PROJECT_ID:$REGION:$SQL_INSTANCE,DB_NAME=velo,DB_USER=postgres" \
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
# Step 6: Configure Firebase Secrets
##############################################################################

print_step "Step 6: Configuring Firebase Secrets"

# Get Firebase config from .env.local
if [ -f "frontend/.env.local" ]; then
    FIREBASE_API_KEY=$(grep NEXT_PUBLIC_FIREBASE_API_KEY frontend/.env.local | cut -d '=' -f2)
    FIREBASE_SENDER_ID=$(grep NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID frontend/.env.local | cut -d '=' -f2)
    FIREBASE_APP_ID=$(grep NEXT_PUBLIC_FIREBASE_APP_ID frontend/.env.local | cut -d '=' -f2)

    # Store as Google Cloud secrets
    echo -n "$FIREBASE_API_KEY" | gcloud secrets create FIREBASE_API_KEY --data-file=- 2>/dev/null || \
        echo -n "$FIREBASE_API_KEY" | gcloud secrets versions add FIREBASE_API_KEY --data-file=-

    echo -n "$FIREBASE_SENDER_ID" | gcloud secrets create FIREBASE_MESSAGING_SENDER_ID --data-file=- 2>/dev/null || \
        echo -n "$FIREBASE_SENDER_ID" | gcloud secrets versions add FIREBASE_MESSAGING_SENDER_ID --data-file=-

    echo -n "$FIREBASE_APP_ID" | gcloud secrets create FIREBASE_APP_ID --data-file=- 2>/dev/null || \
        echo -n "$FIREBASE_APP_ID" | gcloud secrets versions add FIREBASE_APP_ID --data-file=-

    print_success "Firebase secrets configured"
else
    print_warning "frontend/.env.local not found - skipping secret configuration"
fi

##############################################################################
# Step 7: Update apphosting.yaml with Backend URL
##############################################################################

print_step "Step 7: Updating Frontend Configuration"

# Update apphosting.yaml with actual backend URL
cd frontend

# Create/update apphosting.yaml
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
  - variable: NEXT_PUBLIC_FIREBASE_PROJECT_ID
    value: $PROJECT_ID
  - variable: NEXT_PUBLIC_FIREBASE_API_KEY
    secret: FIREBASE_API_KEY
  - variable: NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
    value: $PROJECT_ID.firebaseapp.com
  - variable: NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
    value: $PROJECT_ID.appspot.com
  - variable: NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
    secret: FIREBASE_MESSAGING_SENDER_ID
  - variable: NEXT_PUBLIC_FIREBASE_APP_ID
    secret: FIREBASE_APP_ID
  - variable: NEXT_PUBLIC_API_URL
    value: $BACKEND_URL
  - variable: NEXT_PUBLIC_WS_URL
    value: wss://${BACKEND_URL#https://}/ws
EOF

print_success "Frontend configuration updated"

cd ..

##############################################################################
# Step 8: Deploy Frontend to Firebase App Hosting
##############################################################################

print_step "Step 8: Deploying Frontend to Firebase App Hosting"

print_warning "MANUAL STEP REQUIRED:"
echo ""
echo "Firebase App Hosting requires deployment through the Firebase Console or GitHub integration."
echo ""
echo "To complete the deployment:"
echo ""
echo "Option 1: Deploy via Firebase Console"
echo "  1. Go to: https://console.firebase.google.com/project/$PROJECT_ID/apphosting"
echo "  2. Click 'Get Started' or 'Create Backend'"
echo "  3. Connect your GitHub repository"
echo "  4. Select 'frontend' as the root directory"
echo "  5. Firebase will automatically detect Next.js and use apphosting.yaml"
echo ""
echo "Option 2: Deploy via Firebase CLI (Experimental)"
echo "  cd frontend"
echo "  firebase apphosting:backends:create"
echo ""

##############################################################################
# Deployment Summary
##############################################################################

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   🎉 Backend Deployment Complete!         ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}Backend (Cloud Run):${NC}"
echo "  API URL:  $BACKEND_URL"
echo "  API Docs: $BACKEND_URL/docs"
echo "  Health:   $BACKEND_URL/health"
echo ""
echo -e "${BLUE}Frontend (Firebase App Hosting):${NC}"
echo "  Status: Manual deployment required (see instructions above)"
echo "  Console: https://console.firebase.google.com/project/$PROJECT_ID/apphosting"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Complete Firebase App Hosting setup (see instructions above)"
echo "2. Add authorized domains in Firebase Console"
echo "3. Test the backend: curl $BACKEND_URL/health"
echo "4. Test the API docs: open $BACKEND_URL/docs"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View backend logs: gcloud run logs read --service=$BACKEND_SERVICE --region=$REGION"
echo "  Update backend:    ./deploy-firebase.sh (will rebuild and redeploy backend)"
echo ""
