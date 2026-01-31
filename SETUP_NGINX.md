# Setup Nginx for Frontend + Backend

## Step 1: Install Nginx

```bash
sudo apt update
sudo apt install -y nginx
```

## Step 2: Create Nginx Configuration

```bash
sudo nano /etc/nginx/sites-available/thumbnail-app
```

Paste this configuration (replace `54.169.255.188` with your server IP if needed):

```nginx
server {
    listen 80;
    server_name 54.169.255.188;  # Your server IP or domain

    # Serve React frontend static files
    root /home/ubuntu/thumb/frontend/build;
    index index.html;

    # Frontend routes - serve index.html for all routes (React Router)
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
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

Save and exit: `Ctrl+X`, then `Y`, then `Enter`

## Step 3: Enable the Configuration

```bash
# Create symbolic link to enable the site
sudo ln -s /etc/nginx/sites-available/thumbnail-app /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t
```

If test passes, restart Nginx:

```bash
sudo systemctl restart nginx
```

## Step 4: Configure Firewall

```bash
# Allow HTTP (port 80)
sudo ufw allow 'Nginx HTTP'
sudo ufw allow 'Nginx Full'

# Check status
sudo ufw status
```

## Step 5: Update AWS Security Group

1. Go to AWS Console → EC2 → Your Instance
2. Security tab → Security Group
3. Edit inbound rules
4. Add rule:
   - Type: HTTP
   - Port: 80
   - Source: 0.0.0.0/0
   - Description: Nginx Web Server
5. Save rules

## Step 6: Access Your Application

- **Frontend + Backend:** `http://54.169.255.188/`
- **API Health Check:** `http://54.169.255.188/api/health`

## Troubleshooting

**Check Nginx status:**
```bash
sudo systemctl status nginx
```

**View Nginx logs:**
```bash
sudo tail -f /var/log/nginx/error.log
```

**Restart Nginx:**
```bash
sudo systemctl restart nginx
```

**Check if Flask backend is running:**
```bash
ps aux | grep python
curl http://localhost:5000/api/health
```




