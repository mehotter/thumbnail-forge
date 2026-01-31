# SSH Key Setup Guide for Server Deployment

## Generate SSH Key on Windows

### Method 1: Using PowerShell (Recommended)

1. **Open PowerShell** (as Administrator if needed)

2. **Generate SSH Key:**
```powershell
ssh-keygen -t ed25519 -C "your_email@example.com"
```

   Or if ed25519 is not supported:
```powershell
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

3. **When prompted:**
   - **File location**: Press Enter to use default (`C:\Users\YourUsername\.ssh\id_ed25519`)
   - **Passphrase**: Enter a secure passphrase (optional but recommended)
   - **Confirm passphrase**: Re-enter the passphrase

4. **Your keys will be created:**
   - Private key: `C:\Users\YourUsername\.ssh\id_ed25519` (keep this secret!)
   - Public key: `C:\Users\YourUsername\.ssh\id_ed25519.pub` (share this)

### Method 2: Using Git Bash (If installed)

1. Open Git Bash
2. Run the same commands as above

### Method 3: Using Windows OpenSSH Client

1. Open Command Prompt or PowerShell
2. Run:
```cmd
ssh-keygen -t rsa -b 4096
```

---

## Copy Public Key to Server

### Option 1: Using ssh-copy-id (if available)

```powershell
ssh-copy-id username@server_ip
```

### Option 2: Manual Copy (Windows)

1. **Display your public key:**
```powershell
cat C:\Users\YourUsername\.ssh\id_ed25519.pub
```

2. **Copy the entire output** (starts with `ssh-ed25519` or `ssh-rsa`)

3. **SSH into your server:**
```powershell
ssh username@server_ip
```

4. **On the server, run:**
```bash
mkdir -p ~/.ssh
chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
```

5. **Paste your public key** into the file, save and exit (Ctrl+X, Y, Enter)

6. **Set correct permissions:**
```bash
chmod 600 ~/.ssh/authorized_keys
```

### Option 3: Using PowerShell to Copy

```powershell
# Get your public key
$publicKey = Get-Content C:\Users\YourUsername\.ssh\id_ed25519.pub

# Copy to server (replace with your details)
$publicKey | ssh username@server_ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

---

## Test SSH Connection

```powershell
ssh username@server_ip
```

If successful, you should be logged in without entering a password!

---

## Transfer Files to Server

### Using SCP (Secure Copy)

```powershell
# Copy single file
scp file.py username@server_ip:/path/to/destination/

# Copy entire directory
scp -r folder_name username@server_ip:/path/to/destination/

# Copy multiple files
scp file1.py file2.py username@server_ip:/path/to/destination/
```

### Example: Transfer Your Thumbnail System

```powershell
# Copy all Python files
scp *.py username@server_ip:~/thumbnail_system/

# Copy requirements file
scp requirements.txt username@server_ip:~/thumbnail_system/

# Copy video file
scp test1.mp4 username@server_ip:~/thumbnail_system/videos/
```

### Using SFTP (Interactive)

```powershell
sftp username@server_ip
```

Then use commands:
- `put local_file remote_path` - Upload file
- `get remote_file local_path` - Download file
- `put -r local_folder remote_path` - Upload folder
- `ls` - List remote files
- `cd` - Change remote directory
- `exit` - Quit

---

## Setup Python Environment on Server

### 1. SSH into server:
```powershell
ssh username@server_ip
```

### 2. Install Python dependencies:
```bash
# Update package list
sudo apt update  # For Ubuntu/Debian
# or
sudo yum update   # For CentOS/RHEL

# Install Python and pip
sudo apt install python3 python3-pip  # Ubuntu/Debian
# or
sudo yum install python3 python3-pip  # CentOS/RHEL

# Install virtual environment
sudo apt install python3-venv  # Ubuntu/Debian
```

### 3. Create virtual environment:
```bash
cd ~/thumbnail_system
python3 -m venv venv
source venv/bin/activate
```

### 4. Install requirements:
```bash
pip install -r requirements.txt
```

### 5. Run your system:
```bash
python hybrid_netflix_disney_system.py test1.mp4 --title "Gujarati Drama" --genre drama family --variants 20
```

---

## Troubleshooting

### SSH Connection Issues

**Problem: Permission denied**
- Solution: Check that your public key is in `~/.ssh/authorized_keys` on server
- Check permissions: `chmod 600 ~/.ssh/authorized_keys`

**Problem: Host key verification failed**
- Solution: Remove old host key:
```powershell
ssh-keygen -R server_ip
```

**Problem: SSH not found**
- Solution: Install OpenSSH on Windows:
```powershell
# Run as Administrator
Add-WindowsCapability -Online -Name OpenSSH.Client~~~~0.0.1.0
```

### File Transfer Issues

**Problem: Permission denied on server**
- Solution: Check directory permissions:
```bash
chmod 755 ~/thumbnail_system
```

**Problem: File not found**
- Solution: Use absolute paths or check current directory with `pwd`

---

## Security Best Practices

1. **Use strong passphrase** for your SSH key
2. **Never share your private key** (`id_ed25519` or `id_rsa`)
3. **Only share your public key** (`id_ed25519.pub` or `id_rsa.pub`)
4. **Use ed25519** keys (more secure than RSA)
5. **Disable password authentication** on server (after SSH key setup)
6. **Use different keys** for different servers

---

## Quick Reference Commands

```powershell
# Generate key
ssh-keygen -t ed25519 -C "your_email@example.com"

# View public key
cat C:\Users\YourUsername\.ssh\id_ed25519.pub

# Copy key to server
type C:\Users\YourUsername\.ssh\id_ed25519.pub | ssh username@server_ip "cat >> ~/.ssh/authorized_keys"

# Test connection
ssh username@server_ip

# Copy files
scp file.py username@server_ip:~/destination/

# Copy folder
scp -r folder username@server_ip:~/destination/
```

---

## Example: Complete Setup Workflow

```powershell
# 1. Generate SSH key (one-time)
ssh-keygen -t ed25519 -C "your_email@example.com"

# 2. Copy public key to server
type C:\Users\YourUsername\.ssh\id_ed25519.pub | ssh username@server_ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# 3. Test connection
ssh username@server_ip

# 4. On server, create project directory
ssh username@server_ip "mkdir -p ~/thumbnail_system"

# 5. Copy all files
scp *.py username@server_ip:~/thumbnail_system/
scp requirements.txt username@server_ip:~/thumbnail_system/

# 6. SSH and setup
ssh username@server_ip
cd ~/thumbnail_system
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 7. Run your system
python hybrid_netflix_disney_system.py test1.mp4 --title "Gujarati Drama" --genre drama family --variants 20
```

---

## Need Help?

- **Check SSH version**: `ssh -V`
- **View SSH config**: `cat ~/.ssh/config`
- **Test connection with verbose output**: `ssh -v username@server_ip`
- **Check server SSH logs**: `sudo tail -f /var/log/auth.log` (on server)

