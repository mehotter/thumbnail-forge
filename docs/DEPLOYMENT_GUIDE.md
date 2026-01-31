# Server Deployment Guide

## Prerequisites

1. Server with Python 3.8+ and Node.js 16+
2. SSH access to server
3. Domain name (optional, for production)

## Step 1: Transfer Files to Server

### Using SCP

```bash
# Transfer entire project
scp -r . username@server_ip:/path/to/project/

# Or transfer specific folders
scp -r backend/ username@server_ip:/path/to/project/
scp -r frontend/ username@server_ip:/path/to/project/
scp *.py username@server_ip:/path/to/project/
scp requirements.txt username@server_ip:/path/to/project/
```

### Using Git (Recommended)

```bash
# On server
git clone your-repo-url
cd project-name
```

## Step 2: Setup Backend on Server

### 2.1 Install Python Dependencies

```bash
# SSH into server
ssh username@server_ip

# Navigate to project
cd /path/to/project

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

### 2.2 Setup Backend as Service (Systemd)

Create service file: `/etc/systemd/system/thumbnail-api.service`

```ini
[Unit]
Description=Thumbnail Generation API
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/project/backend
Environment="PATH=/path/to/project/venv/bin"
ExecStart=/path/to/project/venv/bin/python app.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable thumbnail-api
sudo systemctl start thumbnail-api
sudo systemctl status thumbnail-api
```

### 2.3 Using Gunicorn (Production)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
cd backend
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

Update service file to use gunicorn:

```ini
ExecStart=/path/to/project/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Step 3: Setup Frontend on Server

### 3.1 Build Frontend

```bash
cd frontend
npm install
npm run build
```

### 3.2 Serve Frontend

**Option A: Using Nginx (Recommended)**

Install nginx:
```bash
sudo apt install nginx
```

Create nginx config: `/etc/nginx/sites-available/thumbnail-forge`

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/project/frontend/build;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:5000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Static files
    location /static {
        root /path/to/project/frontend/build;
    }
}
```

Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/thumbnail-forge /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

**Option B: Using Node.js serve**

```bash
npm install -g serve
serve -s frontend/build -l 3000
```

## Step 4: Update Frontend API URL

Edit `frontend/src/App.jsx`:

```javascript
// Change from:
const response = await fetch('http://localhost:5000/api/generate', {

// To:
const response = await fetch('/api/generate', {  // Relative URL for same domain
// Or:
const response = await fetch('https://api.your-domain.com/api/generate', {  // Full URL
```

Rebuild frontend after changes:
```bash
cd frontend
npm run build
```

## Step 5: Setup SSL (HTTPS)

### Using Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

## Step 6: Firewall Configuration

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Allow SSH (if not already)
sudo ufw allow 22/tcp

# Enable firewall
sudo ufw enable
```

## Step 7: Environment Variables (Optional)

Create `.env` file in backend:

```env
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_UPLOAD_SIZE=500MB
```

Update `app.py` to use environment variables:

```python
import os
from dotenv import load_dotenv

load_dotenv()

UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_UPLOAD_SIZE = os.getenv('MAX_UPLOAD_SIZE', '500MB')
```

## Monitoring & Logs

### View Backend Logs

```bash
# Systemd service logs
sudo journalctl -u thumbnail-api -f

# Or if using gunicorn directly
tail -f /path/to/project/backend/logs/app.log
```

### View Nginx Logs

```bash
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## Performance Optimization

### 1. Increase Upload Size Limit

In `backend/app.py`:
```python
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB
```

### 2. Enable Caching

In nginx config:
```nginx
location /api/thumbnail {
    proxy_cache my_cache;
    proxy_cache_valid 200 1h;
    proxy_pass http://localhost:5000;
}
```

### 3. Use CDN for Static Files

Upload frontend build to CDN (Cloudflare, AWS CloudFront, etc.)

## Troubleshooting

### Backend not starting

```bash
# Check service status
sudo systemctl status thumbnail-api

# Check logs
sudo journalctl -u thumbnail-api -n 50

# Test manually
cd /path/to/project/backend
source ../venv/bin/activate
python app.py
```

### Frontend not loading

```bash
# Check nginx status
sudo systemctl status nginx

# Test nginx config
sudo nginx -t

# Check file permissions
sudo chown -R www-data:www-data /path/to/project/frontend/build
```

### API connection errors

- Check backend is running: `curl http://localhost:5000/api/health`
- Check firewall rules
- Verify nginx proxy configuration
- Check CORS settings in backend

## Quick Deployment Script

Create `deploy.sh`:

```bash
#!/bin/bash

# Build frontend
cd frontend
npm install
npm run build
cd ..

# Restart backend service
sudo systemctl restart thumbnail-api

# Reload nginx
sudo systemctl reload nginx

echo "Deployment complete!"
```

Make executable:
```bash
chmod +x deploy.sh
```

Run:
```bash
./deploy.sh
```

## Security Checklist

- [ ] Use HTTPS (SSL certificate)
- [ ] Set strong SECRET_KEY
- [ ] Limit file upload size
- [ ] Validate file types
- [ ] Use environment variables for secrets
- [ ] Enable firewall
- [ ] Regular security updates
- [ ] Backup database/files regularly
- [ ] Monitor logs for suspicious activity

