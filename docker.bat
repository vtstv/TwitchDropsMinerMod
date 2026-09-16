@echo off
cd /d "%~dp0"

echo ======================================================
echo   Starting Twitch Drops Miner in Docker...
echo ======================================================
echo.

docker.exe info >nul 2>&1
if errorlevel 1 goto :docker_not_running

docker.exe compose up -d
if errorlevel 1 goto :compose_error

echo.
echo ======================================================
echo   Twitch Drops Miner successfully started!
echo   Web interface: http://localhost:28088
echo ======================================================
goto :finish

:docker_not_running
echo.
echo [ERROR] Docker is not running.
echo Please start Docker Desktop and try again.
goto :finish

:compose_error
echo.
echo [ERROR] Failed to start container with Docker Compose.
echo Check the error output above.
goto :finish

:finish
echo.
pause