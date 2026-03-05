#!/bin/bash

# OS detection for Python executable
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" || "$OSTYPE" == "win32" ]] || grep -q -i "microsoft" /proc/version 2>/dev/null; then
    # Windows native or Git Bash or WSL
    PYTHON_CMD="python.exe"
else
    # macOS or Native Linux
    PYTHON_CMD="python3"
fi

# Cleanup background processes on exit (Ctrl+C)
trap "kill 0" SIGINT SIGTERM EXIT

echo "==================================================="
echo "  Lightweight Federated Learning PoC - HUB NODE"
echo "==================================================="
echo ""

cd "$(dirname "$0")"

# Get the local network IP address to display to the user
echo "Your local network IP Address (give this to the Edge computer):"
if command -v ip > /dev/null 2>&1; then
    ip -4 addr show | grep -v '127.0.0.1' | grep -oP '(?<=inet\s)\d+(\.\d+){3}'
elif command -v ipconfig > /dev/null 2>&1; then
    ipconfig | grep "IPv4" | awk '{print $NF}'
else
    hostname -I | cut -d' ' -f1
fi

echo ""
echo "Waiting for 7 total nodes to connect (1 local, 6 remote)..."
echo ""

echo "1. Starting Coordinator on port 5000..."
export EXPECTED_NODES=7
$PYTHON_CMD lite_coordinator.py &
sleep 3

echo "2. Starting Local Silo (Finance)..."
$PYTHON_CMD lite_silo.py --node_id "Silo_Finance_Hub" --domain "Finance" --coordinator_url "http://localhost:5000" &

echo ""
echo "Hub processes started in the background!"
echo "Waiting for Edge machine to connect..."
echo ""
echo "Press [Ctrl+C] to stop all python processes and exit."
wait
