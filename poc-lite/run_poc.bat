@echo off
echo Starting Lightweight Federated Learning Proof of Concept...
echo.

cd /d "%~dp0"

echo 1. Starting Coordinator
start "Coordinator" cmd /c "title Coordinator && python lite_coordinator.py"
timeout /t 2 /nobreak > nul

echo 2. Starting Silo 1 (Healthcare)
set NODE_ID=Silo_Healthcare
set DOMAIN=Healthcare
start "Silo Healthcare" cmd /c "title Silo_Healthcare && python lite_silo.py"
timeout /t 1 /nobreak > nul

echo 3. Starting Silo 2 (Finance)
set NODE_ID=Silo_Finance
set DOMAIN=Finance
start "Silo Finance" cmd /c "title Silo_Finance && python lite_silo.py"
timeout /t 1 /nobreak > nul

echo 4. Starting Silo 3 (Retail)
set NODE_ID=Silo_Retail
set DOMAIN=Retail
start "Silo Retail" cmd /c "title Silo_Retail && python lite_silo.py"

echo.
echo All processes started! Check the Coordinator window for the aggregation logs.
echo Press any key to kill all python processes and exit.
pause > nul
taskkill /F /IM python.exe
