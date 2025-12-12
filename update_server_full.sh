#!/bin/bash

# Update Multiple Files on Relay Server
# Use this when you need to update relay_server.py AND requirements.txt

set -e

echo "=========================================="
echo "Update Server Files (Full Update)"
echo "=========================================="
echo ""

PROJECT_ID="${GCP_PROJECT_ID:-hackathon-my-optum}"
INSTANCE_NAME="${INSTANCE_NAME:-relay-server}"
ZONE="${ZONE:-us-central1-a}"

echo "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Instance: $INSTANCE_NAME"
echo "  Zone: $ZONE"
echo ""

# Files to update
FILES_TO_UPDATE=("relay_server.py" "requirements.txt")

echo "Checking files..."
for file in "${FILES_TO_UPDATE[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✓ $file"
    else
        echo "  ❌ $file NOT FOUND"
        exit 1
    fi
done

echo ""
echo "Uploading files to server..."

# Upload all files
gcloud compute scp \
    relay_server.py requirements.txt \
    $INSTANCE_NAME:~/ \
    --zone=$ZONE \
    --project=$PROJECT_ID

echo "✓ Files uploaded"
echo ""

# Update dependencies if requirements.txt changed
echo "Updating Python dependencies..."
gcloud compute ssh $INSTANCE_NAME \
    --zone=$ZONE \
    --project=$PROJECT_ID \
    --command='pip3 install -r requirements.txt --upgrade'

echo "✓ Dependencies updated"
echo ""

# Restart service
echo "Restarting relay-server service..."
gcloud compute ssh $INSTANCE_NAME \
    --zone=$ZONE \
    --project=$PROJECT_ID \
    --command='sudo systemctl restart relay-server'

echo "✓ Service restarted"
echo ""

# Wait and check status
sleep 3
echo "Checking service status..."
gcloud compute ssh $INSTANCE_NAME \
    --zone=$ZONE \
    --project=$PROJECT_ID \
    --command='sudo systemctl status relay-server --no-pager'

echo ""
echo "=========================================="
echo "✓ Full Update Complete!"
echo "=========================================="
echo ""
