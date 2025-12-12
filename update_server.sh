#!/bin/bash

# Update Relay Server Script
# This script updates the relay server code on GCP and restarts the service

set -e  # Exit on error

echo "=========================================="
echo "Update Relay Server on GCP"
echo "=========================================="
echo ""

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-hackathon-my-optum}"
INSTANCE_NAME="${INSTANCE_NAME:-relay-server}"
ZONE="${ZONE:-us-central1-a}"

echo "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Instance: $INSTANCE_NAME"
echo "  Zone: $ZONE"
echo ""

# Check if instance exists
echo "Checking if instance exists..."
if ! gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --project=$PROJECT_ID &> /dev/null; then
    echo "❌ Error: Instance '$INSTANCE_NAME' not found in zone $ZONE"
    echo ""
    echo "Available instances:"
    gcloud compute instances list --project=$PROJECT_ID
    exit 1
fi

echo "✓ Instance found"
echo ""

# Check if relay_server.py exists locally
if [ ! -f "relay_server.py" ]; then
    echo "❌ Error: relay_server.py not found in current directory"
    echo "Make sure you're in the project directory"
    exit 1
fi

echo "✓ relay_server.py found"
echo ""

# Copy updated file to server
echo "Uploading relay_server.py to server..."
gcloud compute scp relay_server.py \
    $INSTANCE_NAME:~/ \
    --zone=$ZONE \
    --project=$PROJECT_ID

echo "✓ File uploaded"
echo ""

# Restart the service
echo "Restarting relay-server service..."
gcloud compute ssh $INSTANCE_NAME \
    --zone=$ZONE \
    --project=$PROJECT_ID \
    --command='sudo systemctl restart relay-server'

echo "✓ Service restarted"
echo ""

# Wait a moment for service to start
echo "Waiting for service to start..."
sleep 3

# Check service status
echo ""
echo "Checking service status..."
gcloud compute ssh $INSTANCE_NAME \
    --zone=$ZONE \
    --project=$PROJECT_ID \
    --command='sudo systemctl status relay-server --no-pager -l'

echo ""
echo "=========================================="
echo "✓ Update Complete!"
echo "=========================================="
echo ""
echo "Your relay server has been updated and restarted."
echo ""
echo "To view logs:"
echo "  gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --project=$PROJECT_ID --command='sudo journalctl -u relay-server -f'"
echo ""
