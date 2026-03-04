#!/bin/bash
set -e

echo -e "\033[1;32m--- Master Hub Startup ---\033[0m"
echo ""
echo -e "\033[1;33mGetting local IP addresses...\033[0m"

# Try getting IPs using hostname or ip route
if command -v ip > /dev/null; then
    ip -4 addr show | grep -oP '(?<=inet\s)\d+(\.\d+){3}' | grep -v '127.0.0.1' | grep -v '172.17.'
else
    hostname -I
fi

echo ""
echo -e "\033[1;33mGive one of these IPs to the Edge nodes so they can connect.\033[0m"
echo -e "\033[1;32mStarting Docker Compose...\033[0m"

docker compose -f deployment/docker-compose-hub.yml up --build -d
docker compose -f deployment/docker-compose-hub.yml logs -f coordinator
