# Evolve Consciousness RAG - Deployment Checklist

**Target Environment:** DigitalOcean Droplet + Claude Desktop (Mac)
**Last Updated:** November 30, 2025

---

## Table of Contents

1. [Pre-Launch Checklist](#pre-launch-checklist)
2. [Server Deployment Steps](#server-deployment-steps)
3. [Configuration Verification](#configuration-verification)
4. [Security Considerations](#security-considerations)
5. [Backup Procedures](#backup-procedures)
6. [Monitoring Setup](#monitoring-setup)
7. [Launch Day Checklist](#launch-day-checklist)
8. [Post-Launch Monitoring](#post-launch-monitoring)

---

## Pre-Launch Checklist

### Development Environment

- [ ] All local tests pass (`python test_api.py`)
- [ ] Upload system working (single and batch)
- [ ] Query system returning quality results
- [ ] MCP server tested with Claude Desktop
- [ ] Documentation reviewed and updated
- [ ] All API keys verified and working
- [ ] Environment variables documented in `.env.example`
- [ ] Code pushed to GitHub repository

### Content Preparation

- [ ] Content library organized (beginner/intermediate/advanced)
- [ ] Test documents uploaded successfully
- [ ] Metadata tagging verified (manual spot-checks)
- [ ] Duplicate content identified and resolved
- [ ] Content sources documented
- [ ] Copyright/licensing verified for all materials

### Account Setup

- [ ] DigitalOcean account active
- [ ] Droplet created (Ubuntu 22.04, minimum 2GB RAM)
- [ ] Pinecone account active (index created)
- [ ] OpenAI account with billing configured
- [ ] Anthropic account with billing configured
- [ ] GitHub repository accessible from server
- [ ] Domain name configured (optional)
- [ ] SSL certificate obtained (if using domain)

### Cost Planning

- [ ] Monthly budget calculated
  - DigitalOcean: $12-24/month
  - Pinecone: Free tier or $70/month
  - OpenAI embeddings: ~$1-5/month
  - Claude API: $20-40/month (your cap)
- [ ] Spending caps configured
- [ ] Billing alerts set up for all services
- [ ] Cost monitoring dashboard planned

---

## Server Deployment Steps

### Step 1: Provision DigitalOcean Droplet

**Create Droplet:**

1. Log in to DigitalOcean
2. Create Droplet:
   - **Distribution:** Ubuntu 22.04 LTS
   - **Plan:** Basic - $12/month (2GB RAM, 1 CPU)
   - **Datacenter:** Choose closest to you
   - **Authentication:** SSH keys (recommended) or password
   - **Hostname:** evolve-consciousness-rag
3. Note your droplet IP address

**Initial Server Access:**

```bash
# SSH into your server
ssh root@YOUR_DROPLET_IP

# Update system
apt update && apt upgrade -y

# Reboot if kernel updated
reboot
```

Wait 1 minute, then reconnect:

```bash
ssh root@YOUR_DROPLET_IP
```

**Checklist:**
- [ ] Droplet created successfully
- [ ] SSH access working
- [ ] System updated
- [ ] IP address documented

---

### Step 2: Install Dependencies

```bash
# Install Python 3.11
apt install -y python3.11 python3.11-venv python3-pip

# Install Git
apt install -y git

# Install Nginx (optional, for reverse proxy)
apt install -y nginx

# Install UFW firewall
apt install -y ufw

# Verify installations
python3.11 --version
git --version
nginx -v
```

**Checklist:**
- [ ] Python 3.11 installed
- [ ] Git installed
- [ ] Nginx installed (if using)
- [ ] Firewall installed

---

### Step 3: Clone Repository

```bash
# Create application directory
mkdir -p /opt/apps
cd /opt/apps

# Clone repository
git clone https://github.com/YOUR_USERNAME/consciousness-RAG.git
cd consciousness-RAG/consciousness-rag/backend

# Verify files
ls -la
```

**Checklist:**
- [ ] Repository cloned successfully
- [ ] All files present
- [ ] `requirements.txt` exists
- [ ] `main.py` exists

---

### Step 4: Setup Python Environment

```bash
# Create virtual environment
python3.11 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt

# Verify installations
pip list
```

**Checklist:**
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] No installation errors
- [ ] All required packages present

---

### Step 5: Configure Environment Variables

```bash
# Create .env file
nano .env
```

Add your configuration:

```env
# API Keys
PINECONE_API_KEY=your_actual_pinecone_key
OPENAI_API_KEY=your_actual_openai_key
ANTHROPIC_API_KEY=your_actual_anthropic_key

# Pinecone Configuration
PINECONE_INDEX_NAME=evolve-consciousness
PINECONE_DIMENSION=1536

# Model Configuration
EMBEDDING_MODEL=text-embedding-3-large
CLAUDE_MODEL=claude-sonnet-4-5-20250929

# Application Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

Save and exit (`Ctrl+X`, `Y`, `Enter`)

**Security Check:**

```bash
# Verify .env is not world-readable
chmod 600 .env

# Verify ownership
chown root:root .env

# Confirm permissions
ls -la .env
# Should show: -rw------- 1 root root
```

**Checklist:**
- [ ] `.env` file created
- [ ] All API keys added
- [ ] File permissions secured (600)
- [ ] Configuration verified

---

### Step 6: Test Backend Locally on Server

```bash
# From /opt/apps/consciousness-RAG/consciousness-rag/backend
source venv/bin/activate
python main.py
```

**Expected output:**

```
INFO:     All services initialized successfully!
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Test from another terminal:**

```bash
curl http://localhost:8000/health
```

Stop server: `Ctrl+C`

**Checklist:**
- [ ] Server starts without errors
- [ ] All services connect (Pinecone, OpenAI, Anthropic)
- [ ] Health check returns "healthy"
- [ ] No permission errors

---

### Step 7: Create Systemd Service

Create service file for automatic startup:

```bash
nano /etc/systemd/system/evolve-rag.service
```

Add configuration:

```ini
[Unit]
Description=Evolve Consciousness RAG Backend
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/apps/consciousness-RAG/consciousness-rag/backend
Environment="PATH=/opt/apps/consciousness-RAG/consciousness-rag/backend/venv/bin"
ExecStart=/opt/apps/consciousness-RAG/consciousness-rag/backend/venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

Save and enable:

```bash
# Reload systemd
systemctl daemon-reload

# Enable service (start on boot)
systemctl enable evolve-rag

# Start service
systemctl start evolve-rag

# Check status
systemctl status evolve-rag
```

**Expected output:**
```
● evolve-rag.service - Evolve Consciousness RAG Backend
     Loaded: loaded
     Active: active (running)
```

**View logs:**

```bash
journalctl -u evolve-rag -f
```

**Checklist:**
- [ ] Service file created
- [ ] Service enabled
- [ ] Service started successfully
- [ ] Logs show no errors
- [ ] Service survives reboot test

---

### Step 8: Configure Firewall

```bash
# Enable firewall
ufw enable

# Allow SSH (IMPORTANT: Do this first!)
ufw allow 22/tcp

# Allow API port (if accessing directly)
ufw allow 8000/tcp

# Allow HTTP (if using Nginx)
ufw allow 80/tcp

# Allow HTTPS (if using SSL)
ufw allow 443/tcp

# Check status
ufw status
```

**Checklist:**
- [ ] SSH port allowed (22)
- [ ] API port allowed (8000)
- [ ] HTTP/HTTPS allowed (if using Nginx)
- [ ] Firewall enabled
- [ ] Can still SSH after enabling

---

### Step 9: Configure Nginx (Optional)

If you want to use a domain name or SSL:

```bash
nano /etc/nginx/sites-available/evolve-rag
```

Basic configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 120s;
    }
}
```

Enable site:

```bash
# Create symbolic link
ln -s /etc/nginx/sites-available/evolve-rag /etc/nginx/sites-enabled/

# Test configuration
nginx -t

# Reload Nginx
systemctl reload nginx
```

**Checklist:**
- [ ] Nginx configured
- [ ] Configuration test passes
- [ ] Site enabled
- [ ] Nginx reloaded
- [ ] Domain points to server IP

---

### Step 10: Setup SSL with Let's Encrypt (Optional)

```bash
# Install Certbot
apt install -y certbot python3-certbot-nginx

# Obtain certificate (replace your-domain.com)
certbot --nginx -d your-domain.com

# Follow prompts to configure SSL
# Choose option 2: Redirect HTTP to HTTPS
```

**Auto-renewal test:**

```bash
certbot renew --dry-run
```

**Checklist:**
- [ ] SSL certificate obtained
- [ ] HTTPS working
- [ ] HTTP redirects to HTTPS
- [ ] Auto-renewal configured

---

## Configuration Verification

### Backend Server Verification

```bash
# Check service status
systemctl status evolve-rag

# Test health endpoint
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "pinecone": {"connected": true, ...},
#   "openai": {"connected": true},
#   "anthropic": {"connected": true}
# }
```

**Checklist:**
- [ ] Service running
- [ ] Health check passes
- [ ] All services connected
- [ ] No errors in logs

---

### Database Verification

```bash
# Check Pinecone stats
curl http://localhost:8000/stats

# Upload test document
curl -X POST http://localhost:8000/upload \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Test deployment document",
    "title": "Deployment Test",
    "source": "deployment"
  }'

# Verify upload
curl http://localhost:8000/stats
# total_vectors should increase
```

**Checklist:**
- [ ] Pinecone connected
- [ ] Test upload succeeds
- [ ] Vector count increases
- [ ] Stats endpoint working

---

### Query System Verification

```bash
# Test query
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this about?",
    "top_k": 3
  }'

# Should return answer and sources
```

**Checklist:**
- [ ] Query executes successfully
- [ ] Returns relevant results
- [ ] Source citations included
- [ ] Response time < 10 seconds

---

### Local Access Verification (SSH Tunnel)

From your Mac:

```bash
# Create SSH tunnel
ssh -L 8000:localhost:8000 root@YOUR_DROPLET_IP

# In another terminal, test
curl http://localhost:8000/health
```

**Checklist:**
- [ ] SSH tunnel establishes
- [ ] Local access works
- [ ] Health check succeeds
- [ ] Upload interface accessible

---

## Security Considerations

### API Key Security

**Checklist:**
- [ ] `.env` file permissions set to 600
- [ ] API keys not in version control
- [ ] `.env` added to `.gitignore`
- [ ] No keys in logs or error messages
- [ ] Separate keys for dev/production

### Server Hardening

```bash
# Disable root SSH login (optional, after creating admin user)
nano /etc/ssh/sshd_config
# Set: PermitRootLogin no

# Change SSH port (optional)
# Set: Port 2222

# Restart SSH
systemctl restart sshd

# Install fail2ban (protects against brute force)
apt install -y fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

**Checklist:**
- [ ] Firewall configured correctly
- [ ] Only necessary ports open
- [ ] SSH keys used instead of passwords
- [ ] fail2ban installed and running
- [ ] Regular security updates enabled

---

### Rate Limiting

Add to your Nginx config (if using):

```nginx
# Rate limiting
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

server {
    location / {
        limit_req zone=api burst=20 nodelay;
        # ... rest of config
    }
}
```

**Checklist:**
- [ ] Rate limiting configured
- [ ] Tested with multiple requests
- [ ] Logs show rate limit working

---

### Spending Caps

Verify spending tracker is enforced:

```bash
# Check spending dashboard
curl http://localhost:8000/spending-dashboard

# Should show monthly cap and current usage
```

**Checklist:**
- [ ] Spending tracker database exists
- [ ] Monthly cap set ($20 default)
- [ ] Cap enforcement working
- [ ] Billing alerts configured in API accounts

---

## Backup Procedures

### Database Backup

Pinecone is cloud-hosted, but document your index configuration:

```bash
# Save index configuration
curl http://localhost:8000/stats > /root/backups/pinecone-stats-$(date +%Y%m%d).json

# Create backup script
nano /root/backup-pinecone.sh
```

Add:

```bash
#!/bin/bash
curl http://localhost:8000/stats > /root/backups/pinecone-stats-$(date +%Y%m%d).json
curl http://localhost:8000/uploaded-documents > /root/backups/documents-$(date +%Y%m%d).json
```

Make executable:

```bash
chmod +x /root/backup-pinecone.sh

# Add to crontab (daily at 2am)
crontab -e
# Add: 0 2 * * * /root/backup-pinecone.sh
```

**Checklist:**
- [ ] Backup directory created
- [ ] Backup script created
- [ ] Cron job scheduled
- [ ] Test backup runs successfully

---

### Code Backup

```bash
# Backup entire application
tar -czf /root/backups/evolve-rag-$(date +%Y%m%d).tar.gz /opt/apps/consciousness-RAG

# Backup .env separately (encrypted)
tar -czf /root/backups/env-$(date +%Y%m%d).tar.gz /opt/apps/consciousness-RAG/consciousness-rag/backend/.env
chmod 600 /root/backups/env-*.tar.gz
```

**Checklist:**
- [ ] Code backed up
- [ ] `.env` backed up separately
- [ ] Backups encrypted/secured
- [ ] Backup restoration tested

---

### DigitalOcean Snapshots

```bash
# Create snapshot via DigitalOcean dashboard or CLI
doctl compute droplet-action snapshot YOUR_DROPLET_ID --snapshot-name evolve-rag-$(date +%Y%m%d)
```

**Checklist:**
- [ ] Snapshot created
- [ ] Snapshot tested (restore to new droplet)
- [ ] Weekly snapshot schedule configured
- [ ] Old snapshots pruned regularly

---

## Monitoring Setup

### System Monitoring

```bash
# Install htop for resource monitoring
apt install -y htop

# Monitor system resources
htop

# Check disk usage
df -h

# Check memory
free -h
```

**Checklist:**
- [ ] CPU usage monitored
- [ ] Memory usage monitored
- [ ] Disk space monitored
- [ ] Alerts configured for thresholds

---

### Application Monitoring

```bash
# Monitor service logs
journalctl -u evolve-rag -f

# Check error logs
journalctl -u evolve-rag -p err

# Monitor API access (if using Nginx)
tail -f /var/log/nginx/access.log
```

**Checklist:**
- [ ] Log monitoring in place
- [ ] Error tracking configured
- [ ] Performance metrics logged
- [ ] Automated alerts for errors

---

### Cost Monitoring

Set up billing alerts:

**Pinecone:**
- Dashboard → Billing → Set alert at 80% of budget

**OpenAI:**
- https://platform.openai.com/account/billing
- Set hard limit at $10/month
- Set email alert at $5

**Anthropic:**
- https://console.anthropic.com/settings/billing
- Monitor via spending tracker: `curl http://localhost:8000/spending-dashboard`

**DigitalOcean:**
- Dashboard → Billing → Set alert at $20

**Checklist:**
- [ ] All billing alerts configured
- [ ] Weekly cost review scheduled
- [ ] Spending dashboard checked daily
- [ ] Budget tracking spreadsheet maintained

---

## Launch Day Checklist

### Pre-Launch (1 Week Before)

- [ ] Full system test completed
- [ ] All documentation updated
- [ ] Content library uploaded
- [ ] Backup procedures tested
- [ ] Recovery procedures documented
- [ ] Support contacts documented

### Pre-Launch (24 Hours Before)

- [ ] Final server health check
- [ ] All monitoring active
- [ ] Billing alerts verified
- [ ] SSH access confirmed
- [ ] Backup created
- [ ] Rollback plan documented

### Launch Day

**Morning:**
- [ ] System health check
- [ ] Create fresh backup
- [ ] Review logs for errors
- [ ] Verify all API keys active
- [ ] Test query system
- [ ] Test upload system

**MCP Server Setup (Mac):**
- [ ] Configure Claude Desktop
- [ ] Test MCP connection
- [ ] Verify queries work
- [ ] Test source citations
- [ ] Validate response quality

**Go Live:**
- [ ] Start using for course research
- [ ] Monitor performance
- [ ] Track API costs
- [ ] Log any issues
- [ ] Document feedback

---

## Post-Launch Monitoring

### Daily Checks (First Week)

```bash
# Check service status
systemctl status evolve-rag

# Check health
curl http://localhost:8000/health

# Check logs for errors
journalctl -u evolve-rag --since today -p err

# Check spending
curl http://localhost:8000/spending-dashboard
```

**Checklist:**
- [ ] Service running
- [ ] No errors in logs
- [ ] API costs within budget
- [ ] Query performance acceptable
- [ ] No security alerts

---

### Weekly Tasks

- [ ] Review spending across all services
- [ ] Check disk space usage
- [ ] Review error logs
- [ ] Update content library
- [ ] Test backup restoration
- [ ] Update documentation

---

### Monthly Tasks

- [ ] Create droplet snapshot
- [ ] Review and optimize costs
- [ ] Update dependencies
- [ ] Security audit
- [ ] Performance review
- [ ] Content quality review

---

## Rollback Plan

If critical issues occur:

### Emergency Rollback

```bash
# Stop service
systemctl stop evolve-rag

# Restore from backup
cd /opt/apps
rm -rf consciousness-RAG
tar -xzf /root/backups/evolve-rag-YYYYMMDD.tar.gz

# Restart service
systemctl start evolve-rag
```

### Restore from Snapshot

1. Log in to DigitalOcean
2. Select droplet
3. Power off
4. Restore from snapshot
5. Power on
6. Test system

**Checklist:**
- [ ] Rollback plan documented
- [ ] Rollback tested
- [ ] Recovery time measured
- [ ] Stakeholders notified

---

## Final Deployment Sign-Off

### System Verification

- [ ] Backend server running on DigitalOcean
- [ ] All API services connected
- [ ] Content uploaded successfully
- [ ] Query system working
- [ ] MCP server configured on Mac
- [ ] Claude Desktop integration working
- [ ] All tests passing

### Security Verification

- [ ] Firewall configured
- [ ] API keys secured
- [ ] SSL configured (if using domain)
- [ ] Backups automated
- [ ] Monitoring active
- [ ] Rate limiting configured

### Documentation Verification

- [ ] `INSTALLATION.md` complete
- [ ] `CLAUDE_DESKTOP_SETUP.md` complete
- [ ] `TESTING_GUIDE.md` complete
- [ ] `DEPLOYMENT_CHECKLIST.md` complete
- [ ] All procedures tested
- [ ] Known issues documented

### Cost Verification

- [ ] Monthly budget calculated
- [ ] Spending caps enforced
- [ ] Billing alerts active
- [ ] Cost tracking in place

---

## Success Criteria

Your deployment is successful when:

1. **Backend:**
   - Service runs continuously without crashes
   - All health checks pass
   - Query response time < 10 seconds
   - Upload system handles large documents

2. **MCP Integration:**
   - Claude Desktop connects successfully
   - Queries return relevant results
   - Source citations accurate
   - Performance acceptable

3. **Reliability:**
   - 99%+ uptime
   - Automatic recovery from errors
   - Backups running successfully
   - Monitoring alerts working

4. **Cost:**
   - Within monthly budget
   - Spending tracker enforcing caps
   - No surprise charges
   - Costs optimized

5. **Security:**
   - No security incidents
   - API keys protected
   - Firewall blocking attacks
   - Regular updates applied

---

**Deployment Complete!**

Your Evolve Consciousness RAG system is now live and ready for production use. Use this checklist for future updates and maintenance.

**Remember:**
- Monitor daily for the first week
- Review costs weekly
- Keep documentation updated
- Test backups regularly
- Stay within spending caps

Good luck with your consciousness research and course creation!
