# Quick Start - New Server Deployment
## IP: 52.77.229.65

## 1. Transfer Files
```powershell
# From Windows
scp -i common_key -r N:\thumb ubuntu@52.77.229.65:~/
```

## 2. Connect
```bash
ssh -i common_key ubuntu@52.77.229.65 -p 22
```

## 3. Run Automated Setup
```bash
cd ~/thumb
chmod +x deploy.sh
./deploy.sh
```

## 4. Manual Setup (If deploy.sh doesn't work)

### Install Dependencies
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv nodejs build-essential python3-dev ffmpeg nginx
```

### Setup Python Backend
```bash
cd ~/thumb
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install flask==3.0.0 flask-cors==4.0.0 werkzeug==3.0.1
pip install opencv-python numpy pillow requests
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
pip install ultralytics
```

### Setup Frontend
```bash
cd ~/thumb/frontend
npm install
npm run build
```

### Setup Nginx
```bash
sudo nano /etc/nginx/sites-available/thumbnail-app
```
Paste:
```nginx
server {
    listen 80;
    server_name 52.77.229.65;
    root /home/ubuntu/thumb/frontend/build;
    index index.html;
    location / {
        try_files $uri $uri/ /index.html;
    }
    location /api/ {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
    location /outputs/ {
        proxy_pass http://127.0.0.1:5000;
    }
}
```
```bash
sudo ln -s /etc/nginx/sites-available/thumbnail-app /etc/nginx/sites-enabled/
sudo rm /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx
```

### Setup Flask Service
```bash
sudo nano /etc/systemd/system/thumbnail-app.service
```
Paste:
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

[Install]
WantedBy=multi-user.target
```
```bash
sudo systemctl daemon-reload
sudo systemctl enable thumbnail-app
sudo systemctl start thumbnail-app
```

### Configure Firewall
```bash
sudo ufw allow ssh
sudo ufw allow 'Nginx HTTP'
sudo ufw allow 5000/tcp
sudo ufw enable
```

### AWS Security Group
- Add HTTP (port 80)
- Add Custom TCP (port 5000)

## 5. Access
- **App:** http://52.77.229.65/
- **Health:** http://52.77.229.65/api/health

## Quick Commands
```bash
# Check services
sudo systemctl status thumbnail-app
sudo systemctl status nginx

# View logs
sudo journalctl -u thumbnail-app -f

# Restart services
sudo systemctl restart thumbnail-app
sudo systemctl restart nginx
```



