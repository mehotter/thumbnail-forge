#!/bin/bash

# Deployment script for Thumbnail Generation System on Ubuntu Server
# Run this script on your Ubuntu server after transferring the project files

set -e  # Exit on error

echo "=========================================="
echo "Thumbnail Generation System - Deployment"
echo "=========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -eq 0 ]; then 
    print_error "Please do not run as root. Run as ubuntu user."
    exit 1
fi

# Get the project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

print_status "Project directory: $PROJECT_DIR"

# Step 1: Update system packages
print_status "Updating system packages..."
sudo apt update

# Step 2: Install Python 3 and pip
print_status "Installing Python 3 and pip..."
sudo apt install -y python3 python3-pip python3-venv

# Step 3: Install Node.js and npm
print_status "Checking Node.js installation..."
if ! command -v node &> /dev/null; then
    print_status "Installing Node.js..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt install -y nodejs
else
    print_warning "Node.js already installed: $(node --version)"
fi

# Step 4: Install build tools
print_status "Installing build tools..."
sudo apt install -y build-essential python3-dev

# Step 5: Install FFmpeg
print_status "Installing FFmpeg..."
sudo apt install -y ffmpeg

# Step 6: Create Python virtual environment
print_status "Creating Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Step 7: Activate virtual environment and install Python dependencies
print_status "Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip

if [ -f "backend/requirements.txt" ]; then
    pip install -r backend/requirements.txt
fi

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
fi

print_status "Python dependencies installed"

# Step 8: Install Node.js dependencies and build frontend
print_status "Installing Node.js dependencies..."
if [ -d "frontend" ]; then
    cd frontend
    npm install
    print_status "Building frontend for production..."
    npm run build
    cd ..
    print_status "Frontend built successfully"
else
    print_warning "Frontend directory not found, skipping frontend setup"
fi

# Step 9: Create necessary directories
print_status "Creating necessary directories..."
mkdir -p backend/uploads
mkdir -p backend/outputs
chmod 755 backend/uploads
chmod 755 backend/outputs

# Step 10: Configure firewall
print_status "Configuring firewall..."
if sudo ufw status | grep -q "Status: active"; then
    print_warning "Firewall is active"
else
    print_status "Enabling firewall..."
    sudo ufw --force enable
fi

sudo ufw allow 5000/tcp
print_status "Port 5000 opened in firewall"

# Step 11: Create systemd service file
print_status "Creating systemd service..."
SERVICE_FILE="/tmp/thumbnail-app.service"
cat > "$SERVICE_FILE" << EOF
[Unit]
Description=Thumbnail Generation Flask App
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_DIR/backend
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/backend/app.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

print_status "Service file created at $SERVICE_FILE"
print_warning "To install the service, run:"
echo "  sudo cp $SERVICE_FILE /etc/systemd/system/thumbnail-app.service"
echo "  sudo systemctl daemon-reload"
echo "  sudo systemctl enable thumbnail-app"
echo "  sudo systemctl start thumbnail-app"

# Summary
echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
print_status "Python version: $(python3 --version)"
print_status "Node.js version: $(node --version)"
print_status "npm version: $(npm --version)"
print_status "Project directory: $PROJECT_DIR"
echo ""
print_status "Next steps:"
echo "  1. Review the service file: cat $SERVICE_FILE"
echo "  2. Install and start the service (commands shown above)"
echo "  3. Check service status: sudo systemctl status thumbnail-app"
echo "  4. View logs: sudo journalctl -u thumbnail-app -f"
echo "  5. Access the app at: http://$(hostname -I | awk '{print $1}'):5000"
echo ""
print_status "Or run manually with:"
echo "  cd $PROJECT_DIR"
echo "  source venv/bin/activate"
echo "  cd backend"
echo "  python app.py"
echo ""
print_status "Deployment script completed!"




