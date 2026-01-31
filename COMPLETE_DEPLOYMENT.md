# Complete Production Deployment Guide
## Server IP: 52.77.229.65

This guide will take you from zero to a fully deployed production application with frontend and backend.

---

## Step 1: Transfer Files to Server

**From your Windows machine**, run:

```powershell
# Navigate to your project directory
cd N:\thumb

# Transfer entire project to server
scp -i common_key -r . ubuntu@52.77.229.65:~/thumb/
```

**Alternative:** Use WinSCP, FileZilla, or any SFTP client:
- Host: `52.77.229.65`
- Port: `22`
- Username: `ubuntu`
- Key file: `common_key`

---

## Step 2: Connect to Server

```bash
ssh -i common_key ubuntu@52.77.229.65 -p 22
```

---

## Step 3: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js and npm
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install build tools (needed for Python packages)
sudo apt install -y build-essential python3-dev

# Install FFmpeg (for video processing)
sudo apt install -y ffmpeg

# Install Nginx (for serving frontend and reverse proxy)
sudo apt install -y nginx

# Verify installations
python3 --version
node --version
npm --version
nginx -v
```

---

## Step 4: Set Up Python Backend

```bash
cd ~/thumb

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install backend dependencies (Flask)
pip install flask==3.0.0 flask-cors==4.0.0 werkzeug==3.0.1

# Install essential ML packages (install in batches to save space)
pip install opencv-python numpy pillow requests

# Install PyTorch (CPU version to save space)
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Install YOLO
pip install ultralytics
```

---

## Step 5: Set Up React Frontend

```bash
cd ~/thumb/frontend

# Install Node.js dependencies
npm install

# Build production version
npm run build
```

---

## Step 6: Configure Nginx (Reverse Proxy)

```bash
# Create Nginx configuration file
sudo nano /etc/nginx/sites-available/thumbnail-app
```

**Paste this configuration:**

```nginx
server {
    listen 80;
    server_name 52.77.229.65;  # Your server IP

    # Serve React frontend static files
    root /home/ubuntu/thumb/frontend/build;
    index index.html;

    # Frontend routes - serve index.html for React Router
    location / {
        try_files $uri $uri/ /index.html;
    }

    # Proxy API requests to Flask backend
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Proxy thumbnail/image requests
    location /outputs/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

**Save:** `Ctrl+X`, then `Y`, then `Enter`

**Enable and test:**

```bash
# Enable the site
sudo ln -s /etc/nginx/sites-available/thumbnail-app /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# If test passes, restart Nginx
sudo systemctl restart nginx

# Enable Nginx to start on boot
sudo systemctl enable nginx
```

---

## Step 7: Set Up Flask Backend as Systemd Service

```bash
# Create systemd service file
sudo nano /etc/systemd/system/thumbnail-app.service
```

**Paste this content:**

```ini
[Unit]
Description=Thumbnail Generation Flask App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/thumb/backend
Environment="PATH=/home/ubuntu/thumb/venv/bin"
ExecStart=/home/ubuntu/thumb/venv/bin/python /home/ubuntu/thumb/backend/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
```

**Save:** `Ctrl+X`, then `Y`, then `Enter`

**Enable and start the service:**

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service to start on boot
sudo systemctl enable thumbnail-app

# Start the service
sudo systemctl start thumbnail-app

# Check status
sudo systemctl status thumbnail-app

# View logs
sudo journalctl -u thumbnail-app -f
```

---

## Step 8: Configure Firewall

```bash
# Allow SSH (important - don't get locked out!)
sudo ufw allow ssh
sudo ufw allow 22/tcp

# Allow HTTP (Nginx)
sudo ufw allow 'Nginx HTTP'
sudo ufw allow 80/tcp

# Allow Flask backend directly (optional, if you want direct access)
sudo ufw allow 5000/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

---

## Step 9: Configure AWS Security Group

**In AWS Console:**

1. Go to **EC2** → Select your instance
2. Click **Security** tab → Click on **Security Group**
3. Click **Edit inbound rules**
4. Add these rules:
   - **SSH (Port 22)**: Type: SSH, Source: Your IP or 0.0.0.0/0
   - **HTTP (Port 80)**: Type: HTTP, Source: 0.0.0.0/0
   - **Custom TCP (Port 5000)**: Type: Custom TCP, Port: 5000, Source: 0.0.0.0/0 (optional)
5. Click **Save rules**

---

## Step 10: Verify Everything is Running

```bash
# Check Flask service
sudo systemctl status thumbnail-app

# Check Nginx service
sudo systemctl status nginx

# Check if Flask is listening
sudo ss -tulpn | grep 5000

# Test Flask API locally
curl http://localhost:5000/api/health

# Test Nginx
curl http://localhost/api/health
```

---

## Step 11: Access Your Application

**From your browser:**

- **Full Application (Frontend + Backend):** `http://52.77.229.65/`
- **API Health Check:** `http://52.77.229.65/api/health`
- **API Info:** `http://52.77.229.65/`

---

## Useful Management Commands

### Flask Service Management

```bash
# Start service
sudo systemctl start thumbnail-app

# Stop service
sudo systemctl stop thumbnail-app

# Restart service
sudo systemctl restart thumbnail-app

# Check status
sudo systemctl status thumbnail-app

# View logs
sudo journalctl -u thumbnail-app -f

# View last 100 lines of logs
sudo journalctl -u thumbnail-app -n 100
```

### Nginx Management

```bash
# Restart Nginx
sudo systemctl restart nginx

# Reload Nginx (without downtime)
sudo systemctl reload nginx

# Check Nginx status
sudo systemctl status nginx

# Test Nginx configuration
sudo nginx -t

# View error logs
sudo tail -f /var/log/nginx/error.log

# View access logs
sudo tail -f /var/log/nginx/access.log
```

### Troubleshooting

```bash
# Check if processes are running
ps aux | grep python
ps aux | grep nginx

# Check ports
sudo ss -tulpn | grep 5000
sudo ss -tulpn | grep 80

# Check disk space
df -h

# Check system resources
free -h
top
```

---

## Quick Reference

**Server IP:** `52.77.229.65`  
**SSH Command:** `ssh -i common_key ubuntu@52.77.229.65 -p 22`  
**Application URL:** `http://52.77.229.65/`  
**API Health:** `http://52.77.229.65/api/health`

---

## Troubleshooting Common Issues

### 1. Flask service won't start
```bash
# Check logs
sudo journalctl -u thumbnail-app -n 50

# Check if port is already in use
sudo lsof -i :5000

# Kill process if needed
sudo kill <PID>
```

### 2. Nginx 502 Bad Gateway
- Check if Flask is running: `sudo systemctl status thumbnail-app`
- Check Flask logs: `sudo journalctl -u thumbnail-app -f`
- Verify Flask is listening: `sudo ss -tulpn | grep 5000`

### 3. Frontend not loading
- Check if build directory exists: `ls -la ~/thumb/frontend/build`
- Check Nginx error logs: `sudo tail -f /var/log/nginx/error.log`
- Verify Nginx config: `sudo nginx -t`

### 4. Can't access from browser
- Check AWS Security Group (ports 80, 5000)
- Check firewall: `sudo ufw status`
- Test locally on server: `curl http://localhost/api/health`

---

## Next Steps (Optional Enhancements)

1. **Set up SSL/HTTPS** with Let's Encrypt
2. **Configure domain name** instead of IP
3. **Set up monitoring** and logging
4. **Configure automatic backups**
5. **Set up CI/CD** pipeline

---

## Summary

After completing all steps:
- ✅ Backend Flask API running on port 5000 (via systemd)
- ✅ Frontend React app served by Nginx on port 80
- ✅ Nginx reverse proxy forwarding `/api/*` to Flask
- ✅ Firewall configured
- ✅ Services auto-start on server reboot
- ✅ Application accessible at `http://52.77.229.65/`



