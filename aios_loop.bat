@echo off
title Willow AIOS Supervisor

echo ==================================================
echo   WILLOW SOVEREIGNTY NODE [ALBUQUERQUE]
echo   Initializing Nervous System...
echo ==================================================

:: 1. Ignite the Intake Engine (Watch the Drop)
start "Willow Intake (Sensing)" python willow.py

:: 2. Ignite the Refinery (Sort the Ore)
start "Kartikeya Refinery (Sorting)" python kart.py

echo.
echo [SYSTEM ONLINE]
echo Both engines are running in parallel.
echo You may minimize this window, but do not close the spawned terminals.
echo.
pause