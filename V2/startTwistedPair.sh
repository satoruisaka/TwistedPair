#!/bin/bash
# Script to execute port forwarding and start TwistedPair server

echo "Preparing to start TwistedPic server..."

echo "1. Checking Ollama status..."

# Check if Ollama is running (using curl from WSL)
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "❌ Ollama is not running. Please start Ollama first."
    echo "   Run: ollama serve"
    exit 1
fi
echo "✅ Ollama is running"

echo "2. Configuring port forwarding..."

# Configure port forwarding on Windows side

powershell.exe -Command "
  \$wslIP = (wsl hostname -I).Trim();
  netsh interface portproxy delete v4tov4 listenport=8000 listenaddress=0.0.0.0 2>\$null;
  netsh interface portproxy delete v4tov4 listenport=5000 listenaddress=0.0.0.0 2>\$null;
  netsh interface portproxy delete v4tov4 listenport=5001 listenaddress=0.0.0.0 2>\$null;
  netsh interface portproxy add v4tov4 listenport=8000 listenaddress=0.0.0.0 connectport=8000 connectaddress=\$wslIP;
  netsh interface portproxy add v4tov4 listenport=5000 listenaddress=0.0.0.0 connectport=5000 connectaddress=\$wslIP;
  netsh interface portproxy add v4tov4 listenport=5001 listenaddress=0.0.0.0 connectport=5001 connectaddress=\$wslIP;
  Write-Host 'Port forwarding active for 8000, 5000, and 5001 on WSL IP:' \$wslIP -ForegroundColor Green
"

# Check if PowerShell command succeeded
if [ $? -ne 0 ]; then
    echo "Port forwarding setup failed. Exiting."
    exit 1
fi

echo "Port forwarding setup complete."

# Activate venv and start server
echo "3. Starting virtual env in TwistedPair directory..."
cd ~/../../mnt/c/Users/sator/linuxproject/TwistedPair/V2 || { echo "Failed to change directory to TwistedPair"; exit 1; }
source ../.venv/bin/activate

echo "4. Starting TwistedPair server..."
uvicorn server:app --host 0.0.0.0 --port 8001 --reload

