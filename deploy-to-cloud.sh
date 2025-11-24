#!/bin/bash

##############################################################################
# Velo - Complete Deployment Script for Google Cloud Platform
# Project: velo-479115
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
FRONTEND_SERVICE="velo-frontend"
BACKEND_SERVICE="velo-backend"

echo -e "${BLUE}╔════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Velo Deployment to Google Cloud         ║${NC}"
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
    "vpcaccess.googleapis.com"
    "firebase.googleapis.com"
    "firestore.googleapis.com"
    "storage-api.googleapis.com"
)

for api in "${APIS[@]}"; do
    echo "Enabling $api..."
    gcloud services enable $api --quiet
done

print_success "All required APIs enabled"

##############################################################################
# Step 3: Create Artifact Registry Repository
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
# Step 4: Build and Push Frontend Container
##############################################################################

print_step "Step 4: Building and Pushing Frontend Container"

cd frontend

# Create production Dockerfile if it doesn't exist
cat > Dockerfile.prod <<'EOF'
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

COPY package*.json ./
RUN npm ci

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Set environment variables for build
ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_FIREBASE_API_KEY
ARG NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
ARG NEXT_PUBLIC_FIREBASE_PROJECT_ID
ARG NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
ARG NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
ARG NEXT_PUBLIC_FIREBASE_APP_ID
ARG NEXT_PUBLIC_WS_URL

ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_FIREBASE_API_KEY=$NEXT_PUBLIC_FIREBASE_API_KEY
ENV NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN
ENV NEXT_PUBLIC_FIREBASE_PROJECT_ID=$NEXT_PUBLIC_FIREBASE_PROJECT_ID
ENV NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=$NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET
ENV NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID
ENV NEXT_PUBLIC_FIREBASE_APP_ID=$NEXT_PUBLIC_FIREBASE_APP_ID
ENV NEXT_PUBLIC_WS_URL=$NEXT_PUBLIC_WS_URL

RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

RUN mkdir .next
RUN chown nextjs:nodejs .next

COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000

CMD ["node", "server.js"]
EOF

print_success "Created production Dockerfile"

# Build and push
FRONTEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/velo-docker/$FRONTEND_SERVICE:latest"

gcloud builds submit \
    --tag $FRONTEND_IMAGE \
    --timeout=20m \
    --machine-type=e2-highcpu-8 \
    --dockerfile=Dockerfile.prod

print_success "Frontend container built and pushed"

cd ..

##############################################################################
# Step 5: Build and Push Backend Container
##############################################################################

print_step "Step 5: Building and Pushing Backend Container"

cd backend

# Create production Dockerfile
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
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
EOF

print_success "Created backend Dockerfile"

# Build and push
BACKEND_IMAGE="$REGION-docker.pkg.dev/$PROJECT_ID/velo-docker/$BACKEND_SERVICE:latest"

gcloud builds submit \
    --tag $BACKEND_IMAGE \
    --timeout=20m \
    --dockerfile=Dockerfile.prod

print_success "Backend container built and pushed"

cd ..

##############################################################################
# Step 6: Create Cloud SQL PostgreSQL Instance
##############################################################################

print_step "Step 6: Setting up Cloud SQL PostgreSQL"

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
gcloud sql databases create velo --instance=$SQL_INSTANCE || print_warning "Database already exists"

print_success "Database configured"

##############################################################################
# Step 7: Deploy Backend to Cloud Run
##############################################################################

print_step "Step 7: Deploying Backend to Cloud Run"

gcloud run deploy $BACKEND_SERVICE \
    --image $BACKEND_IMAGE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$PROJECT_ID" \
    --set-env-vars="API_HOST=0.0.0.0" \
    --set-env-vars="API_PORT=8000" \
    --memory=1Gi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10 \
    --timeout=300

BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
    --region $REGION \
    --format='value(status.url)')

print_success "Backend deployed to: $BACKEND_URL"

##############################################################################
# Step 8: Deploy Frontend to Cloud Run
##############################################################################

print_step "Step 8: Deploying Frontend to Cloud Run"

# Get Firebase config
FIREBASE_API_KEY=$(grep NEXT_PUBLIC_FIREBASE_API_KEY frontend/.env.local | cut -d '=' -f2)
FIREBASE_AUTH_DOMAIN=$(grep NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN frontend/.env.local | cut -d '=' -f2)
FIREBASE_STORAGE_BUCKET=$(grep NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET frontend/.env.local | cut -d '=' -f2)
FIREBASE_SENDER_ID=$(grep NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID frontend/.env.local | cut -d '=' -f2)
FIREBASE_APP_ID=$(grep NEXT_PUBLIC_FIREBASE_APP_ID frontend/.env.local | cut -d '=' -f2)

gcloud run deploy $FRONTEND_SERVICE \
    --image $FRONTEND_IMAGE \
    --platform managed \
    --region $REGION \
    --allow-unauthenticated \
    --set-env-vars="NEXT_PUBLIC_API_URL=$BACKEND_URL" \
    --set-env-vars="NEXT_PUBLIC_FIREBASE_API_KEY=$FIREBASE_API_KEY" \
    --set-env-vars="NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=$FIREBASE_AUTH_DOMAIN" \
    --set-env-vars="NEXT_PUBLIC_FIREBASE_PROJECT_ID=$PROJECT_ID" \
    --set-env-vars="NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=$FIREBASE_STORAGE_BUCKET" \
    --set-env-vars="NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=$FIREBASE_SENDER_ID" \
    --set-env-vars="NEXT_PUBLIC_FIREBASE_APP_ID=$FIREBASE_APP_ID" \
    --set-env-vars="NEXT_PUBLIC_WS_URL=wss://${BACKEND_URL#https://}/ws" \
    --memory=512Mi \
    --cpu=1 \
    --min-instances=0 \
    --max-instances=10

FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE \
    --region $REGION \
    --format='value(status.url)')

print_success "Frontend deployed to: $FRONTEND_URL"

##############################################################################
# Step 9: Update Firebase Authorized Domains
##############################################################################

print_step "Step 9: Updating Firebase Configuration"

print_warning "MANUAL STEP REQUIRED:"
echo "1. Go to: https://console.firebase.google.com/project/$PROJECT_ID/authentication/settings"
echo "2. Add these domains to 'Authorized domains':"
echo "   - ${FRONTEND_URL#https://}"
echo "   - ${BACKEND_URL#https://}"

##############################################################################
# Deployment Complete
##############################################################################

echo ""
echo -e "${GREEN}╔════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   🎉 Deployment Complete!                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}URLs:${NC}"
echo "  Frontend: $FRONTEND_URL"
echo "  Backend:  $BACKEND_URL"
echo "  API Docs: $BACKEND_URL/docs"
echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Add Firebase authorized domains (see above)"
echo "2. Visit $FRONTEND_URL to test your app"
echo "3. Configure custom domain (optional)"
echo "4. Set up Cloud CDN for better performance"
echo "5. Configure backup schedule for Cloud SQL"
echo ""
echo -e "${BLUE}Useful Commands:${NC}"
echo "  View logs (Frontend): gcloud run logs read --service=$FRONTEND_SERVICE --region=$REGION"
echo "  View logs (Backend):  gcloud run logs read --service=$BACKEND_SERVICE --region=$REGION"
echo "  Update frontend:      gcloud run deploy $FRONTEND_SERVICE --image $FRONTEND_IMAGE --region=$REGION"
echo "  Update backend:       gcloud run deploy $BACKEND_SERVICE --image $BACKEND_IMAGE --region=$REGION"
echo ""
