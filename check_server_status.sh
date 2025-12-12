#!/bin/bash

# Check Relay Server Status Script

echo "=========================================="
echo "Relay Server Status Check"
echo "=========================================="
echo ""

PROJECT_ID="hackathon-my-optum"

echo "Checking for relay-server instances..."
echo ""

# List all instances named relay-server
gcloud compute instances list \
    --project=$PROJECT_ID \
    --filter="name:relay-server" \
    --format="table(name,zone,machineType,networkInterfaces[0].accessConfigs[0].natIP:label=EXTERNAL_IP,status)"

echo ""
echo "=========================================="
echo "Server Details"
echo "=========================================="

# Get the zone and IP
ZONE=$(gcloud compute instances list \
    --project=$PROJECT_ID \
    --filter="name:relay-server" \
    --format="value(zone)" | head -n 1)

EXTERNAL_IP=$(gcloud compute instances list \
    --project=$PROJECT_ID \
    --filter="name:relay-server" \
    --format="value(networkInterfaces[0].accessConfigs[0].natIP)" | head -n 1)

if [ -n "$EXTERNAL_IP" ]; then
    echo ""
    echo "✓ Relay server is deployed!"
    echo ""
    echo "Zone: $ZONE"
    echo "External IP: $EXTERNAL_IP"
    echo ""
    echo "WebSocket URL: ws://$EXTERNAL_IP:8765"
    echo ""
    echo "=========================================="
    echo "GCP Console Links"
    echo "=========================================="
    echo ""
    echo "View in Console:"
    echo "https://console.cloud.google.com/compute/instances?project=$PROJECT_ID"
    echo ""
    echo "VM Details:"
    echo "https://console.cloud.google.com/compute/instancesDetail/zones/$ZONE/instances/relay-server?project=$PROJECT_ID"
    echo ""
    echo "=========================================="
    echo "Next Steps"
    echo "=========================================="
    echo ""
    echo "1. Update your code with this URL:"
    echo "   ws://$EXTERNAL_IP:8765"
    echo ""
    echo "2. Test connection:"
    echo "   wscat -c ws://$EXTERNAL_IP:8765"
    echo ""
    echo "3. Check server logs:"
    echo "   gcloud compute ssh relay-server --zone=$ZONE --project=$PROJECT_ID --command='sudo journalctl -u relay-server -f'"
    echo ""
    echo "4. View firewall rules:"
    echo "   gcloud compute firewall-rules list --project=$PROJECT_ID --filter='name~websocket'"
    echo ""
else
    echo "❌ No relay-server instance found"
    echo ""
    echo "Deploy one with:"
    echo "  ./deploy_gcp.sh"
fi

echo ""
