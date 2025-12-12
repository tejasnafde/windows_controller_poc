# 🚀 Complete Deployment Checklist

## ✅ Step 1: Relay Server (GCP) - IN PROGRESS

### Current Status
- ✅ Deployment script created and updated
- ✅ Zone changed to Asia (Mumbai) for better performance
- ⏳ Ready to deploy

### Deploy Now
```bash
# Make sure project ID is set
export GCP_PROJECT_ID="hackathon-my-optum"

# Run deployment
./deploy_gcp.sh
```

**What this does:**
- Creates VM in `asia-south1-a` (Mumbai)
- Installs relay server
- Opens firewall port 8765
- Auto-starts on boot
- Gives you WebSocket URL: `ws://YOUR_IP:8765`

**Time:** ~5 minutes

---

## 📋 Step 2: Update Code with Server URL

After relay server is deployed, you'll get an IP address like: `34.93.xxx.xxx`

### Files to Update

**1. brain_example.py** (Line 20)
```python
SERVER_URL = 'ws://34.93.xxx.xxx:8765'  # Replace with your actual IP
```

**2. example_websocket.py** (Line 21)
```python
SERVER_URL = 'ws://34.93.xxx.xxx:8765'  # Replace with your actual IP
```

**3. windows_client_websocket.py** (Line 30)
```python
DEFAULT_SERVER_URL = 'ws://34.93.xxx.xxx:8765'  # Replace with your actual IP
```

---

## 🖥️ Step 3: Deploy Windows Client

You have **2 options** for deploying the Windows client:

### Option A: Python Script (For Testing)

**On Windows machine:**
```bash
# Install dependencies
pip install -r requirements.txt

# Run client
python windows_client_websocket.py --server ws://YOUR_IP:8765
```

**Pros:**
- ✅ Quick for testing
- ✅ Easy to update code

**Cons:**
- ❌ Requires Python installed
- ❌ Not user-friendly for non-technical users

---

### Option B: Standalone .exe (For Production) ⭐ RECOMMENDED

**Build the executable:**

```bash
# On Windows (or Mac for testing)
python build_executable.py
```

This creates: `dist/MyOptum_Installer.exe`

**What's included:**
- ✅ Python runtime (no Python installation needed)
- ✅ All dependencies (pyautogui, opencv, etc.)
- ✅ Template images (for element detection)
- ✅ GUI interface
- ✅ Single file - easy to distribute

**Distribution:**

1. **Upload to cloud storage:**
   - Google Drive
   - Dropbox
   - OneDrive
   - Company file server

2. **Share with users:**
   - Send download link
   - Users download and run
   - No installation required!

3. **User experience:**
   ```
   1. Double-click MyOptum_Installer.exe
   2. GUI opens automatically
   3. Enter server URL: ws://YOUR_IP:8765
   4. Click "Connect to Server"
   5. Done! Ready to receive commands
   ```

**File size:** ~50-100 MB (includes everything)

---

## 🎮 Step 4: Deploy Controller

The controller is what **sends commands** to Windows clients.

### Option A: Run Locally (Development/Testing)

```bash
# Run the example brain
python brain_example.py
```

This will:
1. Connect to relay server
2. List available Windows clients
3. Execute automation sequence
4. Save screenshots

---

### Option B: Deploy to Cloud (Production/Automation)

For **scheduled automation** or **always-on** controller:

#### **GCP Cloud Functions** (Serverless)

Create a Cloud Function that runs on schedule:

```python
# main.py
from action_executor import ActionExecutorContext
from instruction_schema import Action

def run_automation(request):
    """Cloud Function entry point"""
    import asyncio
    
    async def execute():
        server_url = 'ws://YOUR_IP:8765'
        
        async with ActionExecutorContext(server_url) as executor:
            clients = await executor.list_clients()
            
            if clients:
                actions = [
                    Action("chart1_e200", screenshot=True, delay=1.0),
                    Action("chart1_e400", screenshot=True, delay=1.0),
                ]
                
                results = await executor.execute_sequence(clients[0], actions)
                return {'status': 'success', 'results': len(results)}
            
            return {'status': 'no_clients'}
    
    result = asyncio.run(execute())
    return result
```

**Deploy:**
```bash
gcloud functions deploy run-automation \
    --runtime python311 \
    --trigger-http \
    --entry-point run_automation
```

**Schedule with Cloud Scheduler:**
```bash
gcloud scheduler jobs create http automation-job \
    --schedule="0 9 * * *" \
    --uri="https://YOUR_FUNCTION_URL" \
    --http-method=GET
```

---

#### **GCP Compute Engine** (Always-On)

Run controller on a small VM:

```bash
# Create small VM
gcloud compute instances create controller-vm \
    --zone=asia-south1-a \
    --machine-type=e2-micro \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud

# SSH and setup
gcloud compute ssh controller-vm --zone=asia-south1-a

# Install dependencies
sudo apt update
sudo apt install python3-pip -y
pip3 install websockets

# Copy controller files
# (use gcloud compute scp)

# Run controller
python3 brain_example.py
```

---

## 📊 Complete Deployment Architecture

```
┌─────────────────────────────────────────────────────┐
│  GCP (Asia - Mumbai)                                │
│                                                     │
│  ┌───────────────────────────────────────────────┐ │
│  │  Relay Server VM                              │ │
│  │  IP: 34.93.xxx.xxx                            │ │
│  │  Port: 8765                                   │ │
│  │  Status: Running 24/7                         │ │
│  └───────────────────────────────────────────────┘ │
│                                                     │
└─────────────────────────────────────────────────────┘
                        ▲
                        │ WebSocket (ws://)
                        │
        ┌───────────────┴────────────────┐
        │                                │
┌───────▼──────────────┐      ┌─────────▼──────────┐
│  Windows Clients     │      │  Controller        │
│  (Target Machines)   │      │  (Your Machine)    │
│                      │      │                    │
│  • MyOptum_Installer │      │  • brain_example   │
│    .exe running      │      │  • Local Python    │
│  • Connected to      │      │  • Or Cloud Fn     │
│    relay server      │      │                    │
│  • Waiting for       │      │  Sends commands:   │
│    commands          │      │  • Click elements  │
│                      │      │  • Take screenshots│
│  Multiple clients    │      │  • Get data        │
│  can connect!        │      │                    │
└──────────────────────┘      └────────────────────┘
```

---

## 🎯 Deployment Order (Recommended)

### Phase 1: Infrastructure (Today)
1. ✅ Deploy relay server to GCP
2. ✅ Get WebSocket URL
3. ✅ Test with wscat

### Phase 2: Testing (Today)
4. ✅ Update code with server URL
5. ✅ Test Windows client (Python)
6. ✅ Test controller locally
7. ✅ Verify end-to-end flow

### Phase 3: Production (Next)
8. ✅ Build standalone .exe
9. ✅ Distribute to target machines
10. ✅ Set up monitoring
11. ✅ Add error handling

---

## 💡 Next Immediate Steps

### Right Now:
```bash
# 1. Deploy relay server
export GCP_PROJECT_ID="hackathon-my-optum"
./deploy_gcp.sh
```

### After Deployment:
```bash
# 2. Save the WebSocket URL shown
# Example: ws://34.93.xxx.xxx:8765

# 3. Test connection
wscat -c ws://34.93.xxx.xxx:8765

# 4. Update code files with URL
# (Use find & replace in your editor)

# 5. Test Windows client
python windows_client_websocket.py

# 6. Test controller
python brain_example.py
```

---

## 🔧 Optional: Advanced Deployments

### Add SSL/TLS (WSS)
- Get domain name
- Install Nginx + Let's Encrypt
- Use `wss://` instead of `ws://`

### Add Authentication
- API keys for clients
- Token-based auth
- Rate limiting

### Monitoring & Logging
- Cloud Logging
- Uptime monitoring
- Alert notifications

### Load Balancing
- Multiple relay servers
- Health checks
- Automatic failover

---

## 📝 Summary

**What you need to deploy:**

| Component | Where | Status | Priority |
|-----------|-------|--------|----------|
| **Relay Server** | GCP (Asia) | ⏳ Ready | 🔴 HIGH |
| **Windows Client** | Target PCs | ⏳ Pending | 🟡 MEDIUM |
| **Controller** | Your machine | ⏳ Pending | 🟢 LOW |

**Deploy relay server first**, then test with clients and controller.

---

## ✅ Ready to Deploy?

Run this now:
```bash
export GCP_PROJECT_ID="hackathon-my-optum"
./deploy_gcp.sh
```

Let me know when it's done and I'll help with the next steps! 🚀
