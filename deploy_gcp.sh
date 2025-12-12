#!/bin/bash

# GCP Relay Server Deployment Script
# This script sets up the relay server on a GCP Compute Engine VM

set -e  # Exit on error

echo "=========================================="
echo "GCP Relay Server Deployment"
echo "=========================================="
echo ""

# Configuration
PROJECT_ID="${GCP_PROJECT_ID:-hackathon-my-optum}"
INSTANCE_NAME="${INSTANCE_NAME:-relay-server}"
ZONE="${ZONE:-us-central1-a}"
MACHINE_TYPE="${MACHINE_TYPE:-e2-micro}"
PORT="${PORT:-8765}"

echo "Configuration:"
echo "  Project ID: $PROJECT_ID"
echo "  Instance Name: $INSTANCE_NAME"
echo "  Zone: $ZONE"
echo "  Machine Type: $MACHINE_TYPE"
echo "  Port: $PORT"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ Error: gcloud CLI not found!"
    echo "Please install: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

echo "✓ gcloud CLI found"
echo ""

# Set project
echo "Setting GCP project..."
gcloud config set project $PROJECT_ID

# Create VM instance
echo ""
echo "Creating VM instance..."
gcloud compute instances create $INSTANCE_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=10GB \
    --boot-disk-type=pd-balanced \
    --tags=websocket-server \
    --scopes=https://www.googleapis.com/auth/cloud-platform

echo "✓ VM instance created"

# Create firewall rule
echo ""
echo "Creating firewall rule..."
gcloud compute firewall-rules create allow-websocket-$PORT \
    --project=$PROJECT_ID \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:$PORT \
    --source-ranges=0.0.0.0/0 \
    --target-tags=websocket-server \
    --description="Allow WebSocket connections on port $PORT"

echo "✓ Firewall rule created"

# Get external IP
echo ""
echo "Getting external IP..."
EXTERNAL_IP=$(gcloud compute instances describe $INSTANCE_NAME \
    --zone=$ZONE \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)')

echo "✓ External IP: $EXTERNAL_IP"

# Wait for VM to be ready
echo ""
echo "Waiting for VM to be ready (30 seconds)..."
sleep 30

# Copy files to VM
echo ""
echo "Copying project files to VM..."
gcloud compute scp --zone=$ZONE --recurse \
    relay_server.py \
    requirements.txt \
    $INSTANCE_NAME:~/

echo "✓ Files copied"

# Setup and start server
echo ""
echo "Setting up server on VM..."
gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command="
    set -e
    echo '=== Installing dependencies ==='
    sudo apt-get update
    sudo apt-get install -y python3-pip
    pip3 install -r requirements.txt
    
    echo ''
    echo '=== Creating systemd service ==='
    sudo tee /etc/systemd/system/relay-server.service > /dev/null <<EOF
[Unit]
Description=Windows Controller Relay Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER
ExecStart=/usr/bin/python3 /home/$USER/relay_server.py --host 0.0.0.0 --port $PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    echo ''
    echo '=== Starting relay server ==='
    sudo systemctl daemon-reload
    sudo systemctl enable relay-server
    sudo systemctl start relay-server
    
    echo ''
    echo '=== Checking service status ==='
    sudo systemctl status relay-server --no-pager
"

echo ""
echo "=========================================="
echo "✓ Deployment Complete!"
echo "=========================================="
echo ""
echo "Your relay server is running at:"
echo "  WebSocket URL: ws://$EXTERNAL_IP:$PORT"
echo ""
echo "Next steps:"
echo "  1. Update SERVER_URL in your code to: ws://$EXTERNAL_IP:$PORT"
echo "  2. Test connection: wscat -c ws://$EXTERNAL_IP:$PORT"
echo "  3. Start Windows client and controller"
echo ""
echo "Useful commands:"
echo "  SSH to VM:        gcloud compute ssh $INSTANCE_NAME --zone=$ZONE"
echo "  Check logs:       gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='sudo journalctl -u relay-server -f'"
echo "  Restart server:   gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='sudo systemctl restart relay-server'"
echo "  Stop server:      gcloud compute ssh $INSTANCE_NAME --zone=$ZONE --command='sudo systemctl stop relay-server'"
echo "  Delete VM:        gcloud compute instances delete $INSTANCE_NAME --zone=$ZONE"
echo ""
