# Deployment Guide for Ubuntu Server

This guide will help you deploy the Thumbnail Generation System on your Ubuntu 24.04.3 LTS server.

## Prerequisites

- Ubuntu 24.04.3 LTS server (you're already connected via SSH)
- SSH access to the server
- Basic knowledge of Linux commands

## Step 1: Transfer Files to Server

From your local machine (Windows), transfer the project files to the server:

```bash
# Using SCP (run from your local machine, not on the server)
scp -i test -r N:\thumb ubuntu@54.169.255.188:~/
```

Or use SFTP, WinSCP, or any file transfer tool you prefer.

## Step 2: Connect to Server and Navigate

```bash
ssh -i test ubuntu@54.169.255.188 -p 22
cd ~/thumb
```

## Step 3: Install System Dependencies

```bash
# Update package list
sudo apt update

# Install Python 3 and pip
sudo apt install -y python3 python3-pip python3-venv

# Install Node.js and npm (using NodeSource repository for latest LTS)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# Install build tools (needed for some Python packages)
sudo apt install -y build-essential python3-dev

# Install FFmpeg (for video processing)
sudo apt install -y ffmpeg

# Verify installations
python3 --version
node --version
npm --version
```

## Step 4: Set Up Python Backend

```bash
cd ~/thumb

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install backend dependencies
pip install -r backend/requirements.txt

# Install main project dependencies
pip install -r requirements.txt
```

## Step 5: Set Up React Frontend

```bash
cd ~/thumb/frontend

# Install Node.js dependencies
npm install

# Build the production version
npm run build
```

## Step 6: Configure Backend for Production

The backend needs to be configured to serve the frontend and handle CORS properly. You may need to:

1. Update the Flask app to serve static files from the frontend build
2. Update CORS settings if needed
3. Change `localhost:5000` references to your server's IP or domain

## Step 7: Run the Application

### Option A: Run in Screen/Tmux (Simple)

```bash
# Install screen if not already installed
sudo apt install -y screen

# Create a new screen session
screen -S thumbnail-app

# Activate virtual environment
cd ~/thumb
source venv/bin/activate

# Run the Flask app
cd backend
python app.py

# Press Ctrl+A then D to detach from screen
# To reattach: screen -r thumbnail-app
```

### Option B: Run as Systemd Service (Recommended for Production)

Create a systemd service file:

```bash
sudo nano /etc/systemd/system/thumbnail-app.service
```

Add the following content:

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

Then enable and start the service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable thumbnail-app
sudo systemctl start thumbnail-app

# Check status
sudo systemctl status thumbnail-app

# View logs
sudo journalctl -u thumbnail-app -f
```

## Step 8: Configure Firewall

```bash
# Allow HTTP (port 5000) - adjust if using different port
sudo ufw allow 5000/tcp

# Or if using a reverse proxy (nginx) on port 80/443
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall if not already enabled
sudo ufw enable
```

## Step 9: Access the Application

- Backend API: `    http://54.169.255.188:5000`
- Health Check: `http://54.169.255.188:5000/api/health`
- Frontend: You'll need to configure the frontend to point to the backend URL

## Troubleshooting

### Check if the app is running:
```bash
ps aux | grep python
netstat -tulpn | grep 5000
```

### View logs:
```bash
# If using systemd
sudo journalctl -u thumbnail-app -f

# If using screen
screen -r thumbnail-app
```

### Common Issues:

1. **Port already in use**: Change the port in `app.py` or kill the process using port 5000
2. **Permission errors**: Make sure the `ubuntu` user owns the project directory
3. **Missing dependencies**: Reinstall requirements
4. **CORS errors**: Update CORS settings in `app.py`

## Next Steps

1. Set up a reverse proxy (nginx) for better production setup
2. Configure SSL/HTTPS with Let's Encrypt
3. Set up automatic backups
4. Configure monitoring and logging

