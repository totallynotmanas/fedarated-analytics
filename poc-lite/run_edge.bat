@echo off
setlocal
echo ===================================================
echo   Lightweight Federated Learning PoC - EDGE NODE
echo ===================================================
echo.

cd /d "%~dp0"

:: Prompt for the Hub IP Address
set /p HUB_IP="Enter the Hub Coordinator IP Address (e.g. 192.168.1.5): "

if "%HUB_IP%"=="" (
    echo Error: No IP entered. Exiting.
    pause
    exit /b 1
)

set COORDINATOR_URL=http://%HUB_IP%:5000
echo.
echo Connecting 6 Silos to %COORDINATOR_URL%...
echo.

:: --- START RETAIL SILOS ---
echo Starting 3 Retail Silos...
set DOMAIN=Retail

set NODE_ID=Silo_Retail_1
start "Retail 1" cmd /c "title %NODE_ID% && python lite_silo.py"
timeout /t 1 /nobreak > nul

set NODE_ID=Silo_Retail_2
start "Retail 2" cmd /c "title %NODE_ID% && python lite_silo.py"
timeout /t 1 /nobreak > nul

set NODE_ID=Silo_Retail_3
start "Retail 3" cmd /c "title %NODE_ID% && python lite_silo.py"
timeout /t 2 /nobreak > nul

:: --- START HEALTHCARE SILOS ---
echo Starting 3 Healthcare Silos...
set DOMAIN=Healthcare

set NODE_ID=Silo_Healthcare_1
start "Healthcare 1" cmd /c "title %NODE_ID% && python lite_silo.py"
timeout /t 1 /nobreak > nul

set NODE_ID=Silo_Healthcare_2
start "Healthcare 2" cmd /c "title %NODE_ID% && python lite_silo.py"
timeout /t 1 /nobreak > nul

set NODE_ID=Silo_Healthcare_3
start "Healthcare 3" cmd /c "title %NODE_ID% && python lite_silo.py"

echo.
echo All 6 Edge Silos started! They should now be contacting the Hub.
echo Press any key to kill all python processes and exit.
pause > nul
taskkill /F /IM python.exe
