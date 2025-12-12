# 🚀 Quick Start - GCP Deployment

## ✅ Pre-flight Check Complete!

Your environment is ready:
- ✓ gcloud CLI installed
- ✓ Authenticated as: vinay@geoiq.io
- ✓ Project: prj-geoiq-decisioniq-in-prod
- ✓ Required files present

---

## 🎯 Deploy Now (Choose One Method)

### Method 1: Automated Deployment (Recommended) ⭐

```bash
# Set your project ID
export GCP_PROJECT_ID="prj-geoiq-decisioniq-in-prod"

# Run deployment script
./deploy_gcp.sh
```

**This will:**
1. Create a VM instance (e2-micro - free tier)
2. Configure firewall for WebSocket
3. Install Python and dependencies
4. Set up auto-restart service
5. Start the relay server
6. Give you the WebSocket URL

**Time:** ~5 minutes

---

### Method 2: Manual Deployment (Step-by-Step)

Follow the detailed guide in `GCP_DEPLOYMENT.md`

```bash
# View the guide
cat GCP_DEPLOYMENT.md

# Or open in editor
open GCP_DEPLOYMENT.md
```

---

## 📝 What Happens During Deployment

```
┌─────────────────────────────────────────┐
│ 1. Create VM Instance                   │
│    - Machine: e2-micro (free tier)      │
│    - OS: Ubuntu 22.04                   │
│    - Zone: us-central1-a                │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 2. Configure Firewall                   │
│    - Allow TCP port 8765                │
│    - From: 0.0.0.0/0 (anywhere)         │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 3. Install Dependencies                 │
│    - Python 3                           │
│    - websockets library                 │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 4. Setup Systemd Service                │
│    - Auto-start on boot                 │
│    - Auto-restart on failure            │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ 5. Start Relay Server                   │
│    - Listen on 0.0.0.0:8765             │
│    - Ready for connections              │
└─────────────────────────────────────────┘
              ↓
┌─────────────────────────────────────────┐
│ ✓ Deployment Complete!                  │
│   WebSocket URL: ws://YOUR_IP:8765      │
└─────────────────────────────────────────┘
```

---

## 🎬 After Deployment

### 1. Get Your WebSocket URL

The deployment script will show:
```
Your relay server is running at:
  WebSocket URL: ws://34.123.45.67:8765
```

**Save this URL!** You'll need it for your clients and controllers.

### 2. Update Your Code

Update the `SERVER_URL` in these files:

**brain_example.py** (line 20):
```python
SERVER_URL = 'ws://34.123.45.67:8765'  # Replace with your IP
```

**example_websocket.py** (line 21):
```python
SERVER_URL = 'ws://34.123.45.67:8765'  # Replace with your IP
```

**windows_client_websocket.py** (line 30):
```python
DEFAULT_SERVER_URL = 'ws://34.123.45.67:8765'  # Replace with your IP
```

### 3. Test the Connection

```bash
# Install wscat (WebSocket test client)
npm install -g wscat

# Test connection
wscat -c ws://YOUR_IP:8765

# You should see: Connected
```

### 4. Start Windows Client

```bash
python windows_client_websocket.py
# Click "Connect to Server" in the GUI
```

### 5. Run Controller

```bash
python brain_example.py
# Should connect and execute automation
```

---

## 🔧 Management Commands

### View Server Logs
```bash
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo journalctl -u relay-server -f'
```

### Restart Server
```bash
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo systemctl restart relay-server'
```

### Check Server Status
```bash
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo systemctl status relay-server'
```

### SSH into Server
```bash
gcloud compute ssh relay-server --zone=us-central1-a
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

## 💰 Cost

**Free Tier (First Year):**
- e2-micro instance: **FREE** ✅
- 30 GB disk: **FREE** ✅
- 1 GB network: **FREE** ✅

**After Free Tier:**
- ~$7-10/month

---

## 🆘 Troubleshooting

### Can't connect to server?

1. **Check firewall:**
   ```bash
   gcloud compute firewall-rules list | grep websocket
   ```

2. **Check if server is running:**
   ```bash
   gcloud compute ssh relay-server --zone=us-central1-a \
       --command='sudo systemctl status relay-server'
   ```

3. **View error logs:**
   ```bash
   gcloud compute ssh relay-server --zone=us-central1-a \
       --command='sudo journalctl -u relay-server -n 50'
   ```

### Server keeps crashing?

Check logs for errors:
```bash
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo journalctl -u relay-server -f'
```

---

## 🗑️ Delete Everything (Cleanup)

```bash
# Delete VM
gcloud compute instances delete relay-server --zone=us-central1-a

# Delete firewall rule
gcloud compute firewall-rules delete allow-websocket-8765
```

---

## 📚 Documentation

- **GCP_DEPLOYMENT.md** - Complete deployment guide
- **deploy_gcp.sh** - Automated deployment script
- **check_gcp_setup.sh** - Pre-flight check script

---

## ✅ Deployment Checklist

- [ ] Run pre-flight check: `./check_gcp_setup.sh`
- [ ] Deploy server: `./deploy_gcp.sh`
- [ ] Save WebSocket URL
- [ ] Update code with new URL
- [ ] Test with wscat
- [ ] Test with Windows client
- [ ] Test with controller
- [ ] Build standalone .exe: `python build_executable.py`

---

**Ready to deploy? Run:**

```bash
export GCP_PROJECT_ID="prj-geoiq-decisioniq-in-prod"
./deploy_gcp.sh
```

Good luck! 🚀
