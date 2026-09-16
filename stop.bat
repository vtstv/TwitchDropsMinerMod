@echo off
cd /d "%~dp0"

echo ======================================================
echo   Stopping Twitch Drops Miner...
echo ======================================================
echo.

docker.exe compose down

echo.
echo Container stopped.
pause
