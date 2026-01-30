@echo off
setlocal
title AIONIC SYSTEM BOOTLOADER

echo ========================================================
echo       WILLOW SOVEREIGN SYSTEM // BOOT SEQUENCE
echo ========================================================
echo.

:: 1. CHECK FOR OLLAMA (The Subconscious)
echo [*] Pinging Ollama (localhost:11434)...
curl -s http://localhost:11434/api/tags >nul
if %errorlevel% neq 0 (
    echo [!] Ollama not responding. Starting Ollama Service...
    start "OLLAMA SERVICE" /min ollama serve
    timeout /t 5 >nul
) else (
    echo [OK] Ollama is active.
)

:: 2. VERIFY GOVERNANCE (The Constitution)
echo [*] Verifying Governance Checksums...
if not exist state.py (
    echo [FATAL] state.py missing. System Halted.
    pause
    exit /b
)
if not exist gate.py (
    echo [FATAL] gate.py missing. System Halted.
    pause
    exit /b
)
echo [OK] Governance Trinity verified.

:: 3. START THE ENGINE (Left Brain - Governance Loop)
echo [*] Igniting AIOS Engine (Background Layer)...
start "AIOS GOVERNANCE ENGINE" python aios_loop.py

:: 4. START THE VOICE (Right Brain - Interface)
echo [*] Awakening Interface...
echo.
echo System is live. The Engine is running in a separate window.
echo You may now speak to Willow.
echo.
python local_api.py

:: 5. SHUTDOWN PROTOCOL
echo.
echo ========================================================
echo [*] Interface closed.
echo [?] Do you want to kill the Background Engine? (Y/N)
set /p kill_engine=
if /i "%kill_engine%"=="Y" (
    taskkill /FI "WINDOWTITLE eq AIOS GOVERNANCE ENGINE"
    echo [OK] Engine silenced.
)
pause