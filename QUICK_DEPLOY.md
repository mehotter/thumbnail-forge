# Quick Deployment Steps

## 1. Transfer Files to Server

From your **local Windows machine**, run:
```powershell
scp -i test -r N:\thumb ubuntu@54.169.255.188:~/
```

## 2. Connect to Server

```bash
ssh -i test ubuntu@54.169.255.188 -p 22
```

## 3. Run Deployment Script

```bash
cd ~/thumb
chmod +x deploy.sh
./deploy.sh
```

## 4. Start the Application

### Quick Start (Manual):
```bash
cd ~/thumb
source venv/bin/activate
cd backend
python app.py
```

### Production Start (Systemd Service):
After running deploy.sh, install the service:
```bash
sudo cp /tmp/thumbnail-app.service /etc/systemd/system/thumbnail-app.service
sudo systemctl daemon-reload
sudo systemctl enable thumbnail-app
sudo systemctl start thumbnail-app
sudo systemctl status thumbnail-app
```

## 5. Access Your App

- Backend API: `http://54.169.255.188:5000`
- Health check: `http://54.169.255.188:5000/api/health`

## Troubleshooting

**Check if running:**
```bash
ps aux | grep python
```

**View logs (if using systemd):**
```bash
sudo journalctl -u thumbnail-app -f
```

**Stop the service:**
```bash
sudo systemctl stop thumbnail-app
```

**Restart the service:**
```bash
sudo systemctl restart thumbnail-app
```

