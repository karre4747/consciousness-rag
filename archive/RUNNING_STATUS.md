# Evolve Consciousness Engine - Running Status ✅

**Status:** RUNNING 24/7  
**Last Updated:** December 21, 2025

---

## 🎯 What Is This?

This is the **Evolve Consciousness Engine** - a web portal/app that provides:
- **Document Upload Interface** - Upload and process consciousness, recovery, and spiritual content
- **Research Assistant** - Query your knowledge base with AI-powered answers
- **Content Management** - View and manage all uploaded documents
- **Spending Dashboard** - Track Claude API usage and costs

**You can call it:**
- **"The Evolve Portal"** (recommended)
- **"The Consciousness Engine"**
- **"The Evolve App"**

---

## 🌐 How to Access It

### **From Your Browser:**

**Main Portal:**
```
http://<YOUR_SERVER_IP>:8000
```

**API Status:**
```
http://<YOUR_SERVER_IP>:8000/api
```

**Health Check:**
```
http://<YOUR_SERVER_IP>:8000/health
```

### **If You Have a Domain:**

If you set up port forwarding or a domain name, you can access it via:
- `http://your-domain.com:8000` (if port forwarding is configured)
- Or set up nginx reverse proxy for `http://your-domain.com` (see below)

---

## ✅ Current Status

**Service:** `evolve.service` - **RUNNING** ✅  
**Port:** 8000  
**Status:** All services connected and healthy

**Database Stats:**
- **Total Vectors:** 30,831 chunks
- **Pinecone:** Connected ✅
- **OpenAI:** Connected ✅
- **Anthropic (Claude):** Connected ✅

---

## 🔧 Service Management

### **Check Status:**
```bash
systemctl status evolve
```

### **View Logs:**
```bash
# Real-time logs
journalctl -u evolve -f

# Last 50 lines
journalctl -u evolve -n 50
```

### **Restart Service:**
```bash
systemctl restart evolve
```

### **Stop Service:**
```bash
systemctl stop evolve
```

### **Start Service:**
```bash
systemctl start evolve
```

---

## 🚀 Automatic Startup

The service is **enabled to start automatically** on boot. It will:
- ✅ Start when the server boots
- ✅ Restart automatically if it crashes
- ✅ Run 24/7 without manual intervention

---

## 🔒 Port Forwarding / External Access

### **Current Setup:**
- Service is running on port **8000**
- Listening on **0.0.0.0:8000** (all interfaces)
- Firewall is inactive (no blocking)

### **To Access from Outside:**

**Option 1: Direct IP Access (Current)**
```
http://<YOUR_SERVER_IP>:8000
```

**Option 2: Set Up Port Forwarding**
If you're behind a router, configure port forwarding:
- External Port: 8000 (or any port you prefer)
- Internal IP: <YOUR_SERVER_IP>
- Internal Port: 8000

**Option 3: Use Nginx Reverse Proxy (Recommended for Production)**
Set up nginx to serve on port 80/443 with SSL:
```bash
# Install nginx if not already installed
apt install nginx

# Create config (see Deployment Guide for Nginx/Certbot setup)
# Then access via https://<YOUR_DOMAIN>
```

---

## 📊 Quick Health Check

Run this command to verify everything is working:

```bash
curl http://localhost:8000/health | python3 -m json.tool
```

You should see:
```json
{
    "status": "healthy",
    "pinecone": {
        "connected": true,
        "index": "evolve-consciousness",
        "total_vectors": 30831
    },
    "openai": {"connected": true},
    "anthropic": {"connected": true}
}
```

---

## 🐛 Troubleshooting

### **Service Won't Start:**
```bash
# Check logs for errors
journalctl -u evolve -n 100

# Check if port 8000 is already in use
ss -tlnp | grep :8000
```

### **Can't Access from Browser:**
1. Check if service is running: `systemctl status evolve`
2. Check if port is listening: `ss -tlnp | grep :8000`
3. Check firewall: `ufw status`
4. Try accessing from server: `curl http://localhost:8000/health`

### **Service Keeps Restarting:**
```bash
# Check for errors in logs
journalctl -u evolve -n 100 | grep -i error

# Verify that required API keys are configured in your environment
# (See internal setup guide for details on .env configuration)
```

---

## 📝 Service Configuration

**Service File:** `/etc/systemd/system/evolve.service`

**Key Settings:**
- **Working Directory:** `<PROJECT_ROOT>/backend`
- **Executable:** `<PYTHON_BIN> <PROJECT_ROOT>/backend/main.py`
- **Restart Policy:** Always restart on failure
- **Restart Delay:** 10 seconds

---

## 🎉 You're All Set!

Your **Evolve Consciousness Engine Portal** is now:
- ✅ Running 24/7
- ✅ Accessible at `https://<YOUR_DOMAIN>` (or `http://<YOUR_SERVER_IP>:8000` for testing)
- ✅ Will automatically restart on server reboot
- ✅ All services connected and healthy

**You can now:**
1. Open your browser and go to `https://<YOUR_DOMAIN>`
2. Upload documents through the web interface
3. Query your knowledge base using the Research Assistant
4. Manage your content library
5. Monitor spending and usage

**No more terminal commands needed - just use the web interface!** 🎊

---

*Last verified: December 21, 2025*



