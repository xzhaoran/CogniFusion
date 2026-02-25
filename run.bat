@echo off
chcp 65001 >nul
title CogniFusion - Intelligent Fusion Research Assistant System / 智能融合研究助手系统
color 0A

echo.
echo ============================================================
echo   CogniFusion - Intelligent Fusion Research Assistant System
echo   CogniFusion - 智能融合研究助手系统
echo ============================================================
echo.

set "PORTABLE_PYTHON=%~dp0python\python.exe"

REM 检查便携式Python / Check portable Python
if not exist "%PORTABLE_PYTHON%" (
    echo [错误/Error] 未找到便携式 Python / Portable Python not found
    echo.
    echo 请先运行 install_portable_python.bat 安装便携式 Python 环境
    echo Please run install_portable_python.bat first to install portable Python environment
    echo.
    pause
    exit /b 1
)

echo [信息/Info] 使用便携式 Python: %PORTABLE_PYTHON%
echo [Info] Using portable Python: %PORTABLE_PYTHON%
"%PORTABLE_PYTHON%" --version
echo.

REM 检查依赖 / Check dependencies
echo [信息/Info] 检查系统依赖... / Checking system dependencies...
"%PORTABLE_PYTHON%" -c "import fastapi, playwright, httpx, uvicorn" >nul 2>nul
if %errorlevel% neq 0 (
    echo [错误/Error] 依赖检查失败，请先运行 fix_dependencies.bat
    echo [Error] Dependency check failed, please run fix_dependencies.bat first
    echo.
    pause
    exit /b 1
)

echo [信息/Info] 依赖检查通过 / Dependencies check passed
echo.

REM 启动服务 - 打开两个独立窗口 / Start services - open two separate windows
echo [信息/Info] 启动 CogniFusion 服务... / Starting CogniFusion services...
echo ============================================================
echo.

echo [信息/Info] 将打开两个独立命令行窗口： / Two separate command windows will open:
echo   1. API 服务窗口 (端口: 8765) / API service window (port: 8765)
echo   2. MCP 服务窗口 (端口: 8001) / MCP service window (port: 8001)
echo.
echo [提示/Note] 请勿关闭这两个窗口，按任意键继续... / Do not close these windows, press any key to continue...
pause >nul

REM 设置环境变量 / Set environment variables
set "PORTABLE_MODE=1"
set "PLAYWRIGHT_BROWSERS_PATH=%~dp0bin\browsers"
set "PYTHONPATH=%~dp0"

REM 启动 API 服务窗口 / Start API service window
echo [信息/Info] 启动 API 服务窗口... / Starting API service window...
start "CogniFusion API Service / API 服务" cmd /k "cd /d "%~dp0" && "%PORTABLE_PYTHON%" main.py --serve"

REM 等待 API 服务启动 / Wait for API service to start
echo [信息/Info] 等待 API 服务启动... / Waiting for API service to start...
timeout /t 3 /nobreak >nul

REM 启动 MCP 服务窗口 / Start MCP service window
echo [信息/Info] 启动 MCP 服务窗口... / Starting MCP service window...
start "CogniFusion MCP Service / MCP 服务" cmd /k "cd /d "%~dp0" && "%PORTABLE_PYTHON%" main.py --mcp"

echo.
echo [信息/Info] 服务启动完成！ / Services started successfully!
echo ============================================================
echo 服务状态 / Service Status:
echo • API 服务 / API Service: http://127.0.0.1:8765
echo • MCP 服务 / MCP Service: SSE transport protocol (端口/port: 8000)
echo • 状态页面 / Status Page: http://127.0.0.1:8765/
echo • 配置页面 / Configuration Page: http://127.0.0.1:8765/config
echo ============================================================
echo.

REM 自动打开 Web UI / Automatically open Web UI
echo [信息/Info] 正在自动打开 Web UI... / Automatically opening Web UI...
start "" "http://127.0.0.1:8765/"

echo.
echo [提示/Note] 两个服务窗口已打开，请勿关闭它们 / Two service windows are open, do not close them
echo [提示/Note] Web UI 已自动在浏览器中打开 / Web UI has been automatically opened in browser
echo [提示/Note] 要停止服务，请分别关闭两个窗口 / To stop services, close both windows separately
echo.
pause
