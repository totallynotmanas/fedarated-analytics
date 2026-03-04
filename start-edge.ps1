$ErrorActionPreference = "Stop"

Write-Host "--- Remote Edge Startup ---" -ForegroundColor Green
Write-Host ""

$coordinatorIp = Read-Host "Please enter the Master Hub IP Address (e.g. 192.168.1.5)"

if ([string]::IsNullOrWhiteSpace($coordinatorIp)) {
    Write-Host "Error: No IP entered. Exiting." -ForegroundColor Red
    exit 1
}

Write-Host "Setting Coordinator IP to $coordinatorIp..." -ForegroundColor Yellow
$env:COORDINATOR_IP = $coordinatorIp

Write-Host "Starting Docker Compose..." -ForegroundColor Green
docker compose -f deployment/docker-compose-edge.yml up --build -d
docker compose -f deployment/docker-compose-edge.yml logs -f
