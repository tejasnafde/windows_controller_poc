# GCP Deployment Guide - Windows Controller Relay Server

Complete guide to deploy your relay server on Google Cloud Platform.

## 📋 Prerequisites

1. **Google Cloud Account**
   - Sign up at [cloud.google.com](https://cloud.google.com)
   - Free tier includes $300 credit for 90 days
   - e2-micro instance is free tier eligible (1 per month)

2. **gcloud CLI Installed**
   ```bash
   # Check if installed
   gcloud --version
   
   # If not installed, download from:
   # https://cloud.google.com/sdk/docs/install
   ```

3. **GCP Project Created**
   - Go to [console.cloud.google.com](https://console.cloud.google.com)
   - Create a new project or use existing one
   - Note your PROJECT_ID

## 🚀 Quick Deploy (Automated)

### Option 1: Using Deployment Script (Recommended)

```bash
# 1. Set your GCP project ID
export GCP_PROJECT_ID="your-project-id"

# 2. Make script executable
chmod +x deploy_gcp.sh

# 3. Run deployment script
./deploy_gcp.sh
```

The script will:
- ✅ Create a VM instance (e2-micro)
- ✅ Configure firewall rules
- ✅ Install Python and dependencies
- ✅ Set up systemd service for auto-restart
- ✅ Start the relay server
- ✅ Display your WebSocket URL

**That's it!** Your server will be running at `ws://YOUR_EXTERNAL_IP:8765`

---

## 🔧 Manual Deployment (Step-by-Step)

If you prefer manual control, follow these steps:

### Step 1: Authenticate with GCP

```bash
# Login to GCP
gcloud auth login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Verify
gcloud config list
```

### Step 2: Create VM Instance

```bash
# Create e2-micro instance (free tier eligible)
gcloud compute instances create relay-server \
    --zone=us-central1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=10GB \
    --tags=websocket-server
```

**Alternative zones** (choose one close to your users):
- `us-central1-a` (Iowa, USA)
- `us-east1-b` (South Carolina, USA)
- `europe-west1-b` (Belgium, Europe)
- `asia-south1-a` (Mumbai, India)

### Step 3: Configure Firewall

```bash
# Allow WebSocket connections on port 8765
gcloud compute firewall-rules create allow-websocket \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:8765 \
    --source-ranges=0.0.0.0/0 \
    --target-tags=websocket-server
```

### Step 4: Get VM External IP

```bash
# Get external IP address
gcloud compute instances describe relay-server \
    --zone=us-central1-a \
    --format='get(networkInterfaces[0].accessConfigs[0].natIP)'

# Save this IP - you'll need it!
# Example: 34.123.45.67
```

### Step 5: Copy Files to VM

```bash
# Copy relay server and requirements
gcloud compute scp relay_server.py requirements.txt relay-server:~/ \
    --zone=us-central1-a
```

### Step 6: SSH into VM and Setup

```bash
# SSH into the VM
gcloud compute ssh relay-server --zone=us-central1-a
```

Now you're inside the VM. Run these commands:

```bash
# Update system
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and pip
sudo apt-get install -y python3-pip

# Install Python dependencies
pip3 install -r requirements.txt

# Test the server (Ctrl+C to stop)
python3 relay_server.py --host 0.0.0.0 --port 8765
```

### Step 7: Create Systemd Service (Auto-Start)

Create a service file so the server starts automatically:

```bash
# Create service file
sudo nano /etc/systemd/system/relay-server.service
```

Paste this content:

```ini
[Unit]
Description=Windows Controller Relay Server
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/relay_server.py --host 0.0.0.0 --port 8765
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Replace `YOUR_USERNAME`** with your actual username (run `whoami` to check).

Save and exit (Ctrl+X, then Y, then Enter).

### Step 8: Start the Service

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable relay-server

# Start the service
sudo systemctl start relay-server

# Check status
sudo systemctl status relay-server
```

You should see: `Active: active (running)`

### Step 9: Verify Server is Running

```bash
# Check if port is listening
sudo netstat -tlnp | grep 8765

# View logs
sudo journalctl -u relay-server -f
```

Press Ctrl+C to stop viewing logs.

### Step 10: Exit VM

```bash
exit
```

---

## 🌐 Configure Static IP (Optional but Recommended)

By default, your VM gets a dynamic IP that may change if you stop/start the VM. To get a static IP:

```bash
# Reserve a static IP
gcloud compute addresses create relay-server-ip \
    --region=us-central1

# Get the static IP
gcloud compute addresses describe relay-server-ip \
    --region=us-central1 \
    --format='get(address)'

# Assign to your VM
gcloud compute instances delete-access-config relay-server \
    --zone=us-central1-a \
    --access-config-name="external-nat"

gcloud compute instances add-access-config relay-server \
    --zone=us-central1-a \
    --access-config-name="external-nat" \
    --address=STATIC_IP_ADDRESS
```

---

## 🔒 Add SSL/TLS (WSS) with Nginx (Optional)

For production, use secure WebSocket (wss://) with a domain name:

### 1. Get a Domain Name
- Buy from Namecheap, GoDaddy, or Google Domains
- Point A record to your VM's external IP

### 2. Install Nginx and Certbot

```bash
# SSH into VM
gcloud compute ssh relay-server --zone=us-central1-a

# Install Nginx
sudo apt-get install -y nginx certbot python3-certbot-nginx

# Create Nginx config
sudo nano /etc/nginx/sites-available/relay
```

Paste this configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8765;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# Enable site
sudo ln -s /etc/nginx/sites-available/relay /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Allow HTTPS in firewall
gcloud compute firewall-rules create allow-https \
    --direction=INGRESS \
    --priority=1000 \
    --network=default \
    --action=ALLOW \
    --rules=tcp:443 \
    --source-ranges=0.0.0.0/0
```

Now use: `wss://your-domain.com`

---

## 📊 Monitoring and Management

### Check Server Status

```bash
# SSH into VM
gcloud compute ssh relay-server --zone=us-central1-a

# Check service status
sudo systemctl status relay-server

# View live logs
sudo journalctl -u relay-server -f

# View last 100 lines
sudo journalctl -u relay-server -n 100
```

### Restart Server

```bash
# Restart service
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo systemctl restart relay-server'
```

### Stop Server

```bash
# Stop service
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo systemctl stop relay-server'
```

### Update Server Code

```bash
# Copy new version
gcloud compute scp relay_server.py relay-server:~/ \
    --zone=us-central1-a

# Restart service
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo systemctl restart relay-server'
```

---

## 💰 Cost Estimate

### Free Tier (First Year)
- **e2-micro instance**: FREE (1 instance per month)
- **30 GB standard persistent disk**: FREE
- **1 GB network egress**: FREE
- **Static IP (if used)**: FREE while attached to running VM

### After Free Tier
- **e2-micro**: ~$7-10/month
- **Static IP**: $0 (while attached), $3/month (if not attached)
- **Network egress**: $0.12/GB after 1GB

**Total**: ~$0-10/month depending on usage

---

## 🧪 Testing Your Deployment

### 1. Test from Command Line

```bash
# Install wscat (WebSocket client)
npm install -g wscat

# Test connection
wscat -c ws://YOUR_EXTERNAL_IP:8765

# You should see connection established
# Type messages to test
```

### 2. Test with Windows Client

```bash
# Update server URL in windows_client_websocket.py
# Line 30: DEFAULT_SERVER_URL = 'ws://YOUR_EXTERNAL_IP:8765'

# Run client
python windows_client_websocket.py
```

### 3. Test with Controller

```bash
# Update server URL in brain_example.py
# Line 20: SERVER_URL = 'ws://YOUR_EXTERNAL_IP:8765'

# Run controller
python brain_example.py
```

---

## 🔧 Troubleshooting

### Issue: Can't connect to server

**Check firewall:**
```bash
gcloud compute firewall-rules list | grep websocket
```

**Check if server is running:**
```bash
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo systemctl status relay-server'
```

**Check if port is listening:**
```bash
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo netstat -tlnp | grep 8765'
```

### Issue: Server keeps crashing

**View error logs:**
```bash
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo journalctl -u relay-server -n 50'
```

### Issue: Out of memory

**Upgrade to e2-small:**
```bash
# Stop VM
gcloud compute instances stop relay-server --zone=us-central1-a

# Change machine type
gcloud compute instances set-machine-type relay-server \
    --machine-type=e2-small \
    --zone=us-central1-a

# Start VM
gcloud compute instances start relay-server --zone=us-central1-a
```

---

## 🗑️ Cleanup (Delete Everything)

```bash
# Stop and delete VM
gcloud compute instances delete relay-server --zone=us-central1-a

# Delete firewall rule
gcloud compute firewall-rules delete allow-websocket

# Delete static IP (if created)
gcloud compute addresses delete relay-server-ip --region=us-central1
```

---

## 📝 Quick Reference

### Your Server Details
```
WebSocket URL: ws://YOUR_EXTERNAL_IP:8765
Zone: us-central1-a
Instance: relay-server
Machine Type: e2-micro
```

### Common Commands
```bash
# SSH
gcloud compute ssh relay-server --zone=us-central1-a

# View logs
gcloud compute ssh relay-server --zone=us-central1-a --command='sudo journalctl -u relay-server -f'

# Restart
gcloud compute ssh relay-server --zone=us-central1-a --command='sudo systemctl restart relay-server'

# Update code
gcloud compute scp relay_server.py relay-server:~/ --zone=us-central1-a
```

---

## ✅ Next Steps

After deployment:

1. ✅ Save your WebSocket URL: `ws://YOUR_EXTERNAL_IP:8765`
2. ✅ Update all code files with new URL
3. ✅ Test with Windows client
4. ✅ Test with controller
5. ✅ Build standalone .exe: `python build_executable.py`
6. ✅ Distribute to users

---

**Need help?** Check the logs or open an issue on GitHub.
