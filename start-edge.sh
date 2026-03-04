#!/bin/bash
set -e

echo -e "\033[1;32m--- Remote Edge Startup ---\033[0m"
echo ""

read -p "Please enter the Master Hub IP Address (e.g. 192.168.1.5): " coordinatorIp

if [ -z "$coordinatorIp" ]; then
    echo -e "\033[1;31mError: No IP entered. Exiting.\033[0m"
    exit 1
fi

echo -e "\033[1;33mSetting Coordinator IP to $coordinatorIp...\033[0m"
export COORDINATOR_IP=$coordinatorIp

echo -e "\033[1;32mStarting Docker Compose...\033[0m"
docker compose -f deployment/docker-compose-edge.yml up --build -d
docker compose -f deployment/docker-compose-edge.yml logs -f
