$ErrorActionPreference = "Stop"

Write-Host "--- Master Hub Startup ---" -ForegroundColor Green
Write-Host ""
Write-Host "Getting local IP addresses..." -ForegroundColor Yellow

# Try to get the local IPv4 address, filtering out loopback and virtual adapters
$ips = Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch "vEthernet|Loopback|WSL" }

Write-Host "Your Hub is listening on the following Local IP Addresses:" -ForegroundColor Cyan
foreach ($ip in $ips) {
    Write-Host " -> $($ip.IPAddress) ($($ip.InterfaceAlias))" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Give one of these IPs to the Edge nodes so they can connect." -ForegroundColor Yellow
Write-Host "Starting Docker Compose..." -ForegroundColor Green

docker compose -f deployment/docker-compose-hub.yml up --build -d
docker compose -f deployment/docker-compose-hub.yml logs -f coordinator
