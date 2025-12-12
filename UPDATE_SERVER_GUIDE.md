# 🔄 How to Update Relay Server Code

## Quick Reference

When you make changes to your relay server code, here's how to deploy the updates to GCP.

---

## 📝 **What Can You Update?**

1. **relay_server.py** - The main server code
2. **requirements.txt** - Python dependencies
3. **Configuration** - Port, host, etc.

---

## 🚀 **Update Methods**

### **Method 1: Quick Update (Code Only)** ⭐ Most Common

Use this when you only changed `relay_server.py`:

```bash
./update_server.sh
```

**What it does:**
1. ✅ Uploads `relay_server.py` to GCP
2. ✅ Restarts the relay-server service
3. ✅ Shows service status

**Time:** ~10 seconds

---

### **Method 2: Full Update (Code + Dependencies)**

Use this when you changed `relay_server.py` AND `requirements.txt`:

```bash
./update_server_full.sh
```

**What it does:**
1. ✅ Uploads `relay_server.py` and `requirements.txt`
2. ✅ Reinstalls Python dependencies
3. ✅ Restarts the relay-server service
4. ✅ Shows service status

**Time:** ~30 seconds

---

### **Method 3: Manual Update (Step-by-Step)**

If you prefer manual control:

#### **Step 1: Upload File**
```bash
gcloud compute scp relay_server.py relay-server:~/ \
    --zone=us-central1-a \
    --project=hackathon-my-optum
```

#### **Step 2: Restart Service**
```bash
gcloud compute ssh relay-server \
    --zone=us-central1-a \
    --project=hackathon-my-optum \
    --command='sudo systemctl restart relay-server'
```

#### **Step 3: Check Status**
```bash
gcloud compute ssh relay-server \
    --zone=us-central1-a \
    --project=hackathon-my-optum \
    --command='sudo systemctl status relay-server'
```

---

## 🔍 **Verify Update**

### **1. Check Service Status**
```bash
gcloud compute ssh relay-server \
    --zone=us-central1-a \
    --project=hackathon-my-optum \
    --command='sudo systemctl status relay-server'
```

### **2. View Live Logs**
```bash
gcloud compute ssh relay-server \
    --zone=us-central1-a \
    --project=hackathon-my-optum \
    --command='sudo journalctl -u relay-server -f'
```

Press `Ctrl+C` to stop viewing logs.

### **3. Test Connection**
```bash
wscat -c ws://34.63.226.183:8765
```

---

## 📊 **Complete Update Workflow**

```
┌─────────────────────────────────────┐
│ 1. Edit relay_server.py locally    │
│    (Make your code changes)         │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 2. Test locally (optional)          │
│    python relay_server.py           │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 3. Deploy to GCP                    │
│    ./update_server.sh               │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│ 4. Verify deployment                │
│    - Check logs                     │
│    - Test connection                │
└─────────────────────────────────────┘
```

---

## 🛠️ **Common Update Scenarios**

### **Scenario 1: Fixed a Bug**
```bash
# Edit relay_server.py
nano relay_server.py

# Deploy update
./update_server.sh

# Check logs for errors
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo journalctl -u relay-server -n 50'
```

---

### **Scenario 2: Added New Feature**
```bash
# Edit code
nano relay_server.py

# Test locally first
python relay_server.py

# Deploy to GCP
./update_server.sh

# Test with client
python windows_client_websocket.py
```

---

### **Scenario 3: Updated Dependencies**
```bash
# Edit requirements.txt
nano requirements.txt

# Full update (includes dependency install)
./update_server_full.sh
```

---

### **Scenario 4: Changed Port or Configuration**

If you change the port number:

```bash
# 1. Update relay_server.py
# 2. Update firewall rule
gcloud compute firewall-rules update allow-websocket-8765 \
    --allow=tcp:NEW_PORT \
    --project=hackathon-my-optum

# 3. Deploy update
./update_server.sh
```

---

## 🔄 **Rollback (Undo Update)**

If something goes wrong, you can rollback:

### **Option 1: Restore Previous Version**
```bash
# SSH into server
gcloud compute ssh relay-server --zone=us-central1-a

# If you have a backup
cp relay_server.py.backup relay_server.py

# Restart service
sudo systemctl restart relay-server
```

### **Option 2: Redeploy from Git**
```bash
# SSH into server
gcloud compute ssh relay-server --zone=us-central1-a

# Pull from git (if using version control)
cd ~/windows_controller_poc
git pull
sudo systemctl restart relay-server
```

---

## 📋 **Update Checklist**

Before updating:
- [ ] Test changes locally
- [ ] Commit to version control (git)
- [ ] Backup current version (optional)

During update:
- [ ] Run update script
- [ ] Check service status
- [ ] View logs for errors

After update:
- [ ] Test WebSocket connection
- [ ] Test with Windows client
- [ ] Monitor logs for issues

---

## 🚨 **Troubleshooting Updates**

### **Issue: Service won't start after update**

**Check logs:**
```bash
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo journalctl -u relay-server -n 100'
```

**Common causes:**
- Syntax error in code
- Missing dependency
- Port already in use

**Fix:**
```bash
# SSH into server
gcloud compute ssh relay-server --zone=us-central1-a

# Test manually
python3 relay_server.py

# Fix errors, then restart service
sudo systemctl restart relay-server
```

---

### **Issue: Update script fails**

**Check if VM is running:**
```bash
gcloud compute instances list --project=hackathon-my-optum
```

**Check SSH access:**
```bash
gcloud compute ssh relay-server --zone=us-central1-a
```

---

## 💡 **Best Practices**

1. **Test Locally First**
   ```bash
   python relay_server.py --host 0.0.0.0 --port 8765
   ```

2. **Use Version Control**
   ```bash
   git commit -m "Updated relay server logic"
   git push
   ```

3. **Monitor Logs After Update**
   ```bash
   gcloud compute ssh relay-server --zone=us-central1-a \
       --command='sudo journalctl -u relay-server -f'
   ```

4. **Keep Backups**
   ```bash
   # Before updating, backup current version
   gcloud compute ssh relay-server --zone=us-central1-a \
       --command='cp relay_server.py relay_server.py.backup'
   ```

---

## 📚 **Quick Command Reference**

```bash
# Update code only
./update_server.sh

# Update code + dependencies
./update_server_full.sh

# Check status
./check_server_status.sh

# View logs
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo journalctl -u relay-server -f'

# Restart service
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo systemctl restart relay-server'

# Stop service
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo systemctl stop relay-server'

# Start service
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo systemctl start relay-server'
```

---

## ✅ **Example: Complete Update Flow**

```bash
# 1. Make changes to code
nano relay_server.py

# 2. Test locally (optional)
python relay_server.py

# 3. Deploy to GCP
./update_server.sh

# 4. Check it's working
./check_server_status.sh

# 5. View logs
gcloud compute ssh relay-server --zone=us-central1-a \
    --command='sudo journalctl -u relay-server -f'

# 6. Test with client
python windows_client_websocket.py
```

---

**That's it!** Updating your relay server is now as simple as running `./update_server.sh` 🚀
