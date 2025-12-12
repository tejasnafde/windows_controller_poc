#!/bin/bash

# Quick GCP Setup Helper
# This script helps you prepare for GCP deployment

echo "=========================================="
echo "GCP Deployment - Pre-flight Check"
echo "=========================================="
echo ""

# Check gcloud installation
echo "1. Checking gcloud CLI..."
if command -v gcloud &> /dev/null; then
    echo "   ✓ gcloud is installed"
    gcloud --version | head -n 1
else
    echo "   ❌ gcloud is NOT installed"
    echo ""
    echo "   Install from: https://cloud.google.com/sdk/docs/install"
    echo ""
    echo "   Quick install (macOS):"
    echo "   curl https://sdk.cloud.google.com | bash"
    echo "   exec -l $SHELL"
    echo ""
    exit 1
fi

echo ""

# Check authentication
echo "2. Checking GCP authentication..."
if gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    if [ -n "$ACTIVE_ACCOUNT" ]; then
        echo "   ✓ Authenticated as: $ACTIVE_ACCOUNT"
    else
        echo "   ❌ Not authenticated"
        echo ""
        echo "   Run: gcloud auth login"
        echo ""
        exit 1
    fi
else
    echo "   ❌ Not authenticated"
    echo ""
    echo "   Run: gcloud auth login"
    echo ""
    exit 1
fi

echo ""

# Check project
echo "3. Checking GCP project..."
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ -n "$CURRENT_PROJECT" ]; then
    echo "   ✓ Current project: $CURRENT_PROJECT"
else
    echo "   ⚠️  No project set"
    echo ""
    echo "   List your projects:"
    echo "   gcloud projects list"
    echo ""
    echo "   Set a project:"
    echo "   gcloud config set project YOUR_PROJECT_ID"
    echo ""
fi

echo ""

# Check required files
echo "4. Checking required files..."
REQUIRED_FILES=("relay_server.py" "requirements.txt")
ALL_FOUND=true

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "   ✓ $file"
    else
        echo "   ❌ $file NOT FOUND"
        ALL_FOUND=false
    fi
done

if [ "$ALL_FOUND" = false ]; then
    echo ""
    echo "   Make sure you're in the project directory!"
    exit 1
fi

echo ""
echo "=========================================="
echo "✓ Pre-flight check complete!"
echo "=========================================="
echo ""

if [ -n "$CURRENT_PROJECT" ]; then
    echo "Ready to deploy! Next steps:"
    echo ""
    echo "1. Review the deployment guide:"
    echo "   cat GCP_DEPLOYMENT.md"
    echo ""
    echo "2. Deploy using automated script:"
    echo "   export GCP_PROJECT_ID=\"$CURRENT_PROJECT\""
    echo "   ./deploy_gcp.sh"
    echo ""
    echo "Or follow the manual steps in GCP_DEPLOYMENT.md"
else
    echo "Before deploying:"
    echo ""
    echo "1. Set your GCP project:"
    echo "   gcloud config set project YOUR_PROJECT_ID"
    echo ""
    echo "2. Then run this script again to verify"
fi

echo ""
