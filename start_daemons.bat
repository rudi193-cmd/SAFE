@echo off
REM Willow Daemon Launcher
REM Starts all background daemons for the fractal AI OS

echo ========================================
echo Willow Fractal AI OS - Daemon Launcher
echo ========================================
echo.

REM Change to Willow directory
cd /d "%~dp0"

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found in PATH
    pause
    exit /b 1
)

echo Starting daemons...
echo.

REM Start Governance Monitor (every 60s, checks pending commits)
echo [1/6] Governance Monitor...
start "Willow-GovernanceMonitor" /MIN python governance/monitor.py --interval 60 --daemon

REM Start Coherence Scanner (every 1h, scans knowledge for drift)
echo [2/6] Coherence Scanner...
start "Willow-CoherenceScanner" /MIN python core/coherence_scanner.py --interval 3600 --daemon

REM Start Topology Builder (every 1h, builds knowledge graph edges)
echo [3/6] Topology Builder...
start "Willow-TopologyBuilder" /MIN python core/topology_builder.py --interval 3600 --daemon

REM Start Knowledge Compactor (every 24h, archives old data)
echo [4/6] Knowledge Compactor...
start "Willow-KnowledgeCompactor" /MIN python core/knowledge_compactor.py --interval 86400 --daemon

REM Start SAFE Sync (every 5m, syncs to SAFE repo)
echo [5/6] SAFE Sync...
start "Willow-SAFESync" /MIN python core/safe_sync.py --interval 300 --daemon

REM Start Persona Scheduler (every 60s, runs scheduled persona tasks)
echo [6/6] Persona Scheduler...
start "Willow-PersonaScheduler" /MIN python core/persona_scheduler.py --interval 60 --daemon

echo.
echo ========================================
echo All daemons started!
echo ========================================
echo.
echo Running processes:
tasklist /FI "WINDOWTITLE eq Willow-*" 2>nul
echo.
echo To stop all daemons, run: stop_daemons.bat
echo To view daemon status, check log files in:
echo   - governance/violations.log
echo   - core/coherence_scan.log
echo   - core/topology_build.log
echo   - core/compaction.log
echo   - core/safe_sync.log
echo   - core/persona_scheduler.log
echo.
pause
