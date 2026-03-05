@echo off
setlocal
echo ===================================================
echo   Lightweight Federated Learning PoC - HUB NODE
echo ===================================================
echo.

cd /d "%~dp0"

:: Get the local network IP address to display to the user
echo Your local network IP Address (give this to the Edge computer):
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do echo   %%a
echo.
echo Waiting for 7 total nodes to connect (1 local, 6 remote)...
echo.

echo 1. Starting Coordinator on port 5000...
start "Coordinator" cmd /c "title Coordinator && set EXPECTED_NODES=7&& python lite_coordinator.py"
timeout /t 3 /nobreak > nul

echo 2. Starting Local Silo (Finance)...
set NODE_ID=Silo_Finance_Hub
set DOMAIN=Finance
set COORDINATOR_URL=http://localhost:5000
start "Silo Finance (Hub)" cmd /c "title Silo_Finance_Hub && python lite_silo.py"

echo.
echo Hub processes started! Leave these windows open.
echo Waiting for Edge machine to connect...
echo.
echo Press any key to kill all python processes and exit.
pause > nul
taskkill /F /IM python.exe
