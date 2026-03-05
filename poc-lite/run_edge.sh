#!/bin/bash

# Cleanup background processes on exit (Ctrl+C)
trap "kill 0" SIGINT SIGTERM EXIT

echo "==================================================="
echo "  Lightweight Federated Learning PoC - EDGE NODE"
echo "==================================================="
echo ""

cd "$(dirname "$0")"

read -p "Enter the Hub Coordinator IP Address (e.g. 192.168.1.5): " HUB_IP

if [ -z "$HUB_IP" ]; then
    echo "Error: No IP entered. Exiting."
    exit 1
fi

export COORDINATOR_URL="http://${HUB_IP}:5000"
echo ""
echo "Connecting 6 Silos to $COORDINATOR_URL..."
echo ""

# --- START RETAIL SILOS ---
echo "Starting 3 Retail Silos..."

python.exe lite_silo.py --node_id "Silo_Retail_1" --domain "Retail" --coordinator_url "$COORDINATOR_URL" &
sleep 1

python.exe lite_silo.py --node_id "Silo_Retail_2" --domain "Retail" --coordinator_url "$COORDINATOR_URL" &
sleep 1

python.exe lite_silo.py --node_id "Silo_Retail_3" --domain "Retail" --coordinator_url "$COORDINATOR_URL" &
sleep 2

# --- START HEALTHCARE SILOS ---
echo "Starting 3 Healthcare Silos..."

python.exe lite_silo.py --node_id "Silo_Healthcare_1" --domain "Healthcare" --coordinator_url "$COORDINATOR_URL" &
sleep 1

python.exe lite_silo.py --node_id "Silo_Healthcare_2" --domain "Healthcare" --coordinator_url "$COORDINATOR_URL" &
sleep 1

python.exe lite_silo.py --node_id "Silo_Healthcare_3" --domain "Healthcare" --coordinator_url "$COORDINATOR_URL" &

echo ""
echo "All 6 Edge Silos started in the background! They should now be contacting the Hub."
echo "Press [Ctrl+C] to kill all processes and exit."
wait
