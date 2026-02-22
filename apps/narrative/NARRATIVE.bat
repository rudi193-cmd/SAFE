@echo off
echo Narrative Agent starting...
echo Access at: http://localhost:8430
echo On local network: check ipconfig for your IP
echo.
cd /d "%~dp0"
python serve.py
pause
