@echo off
chcp 65001 >nul
echo ============================================================
echo   CogniFusion - API 服务启动脚本
echo ============================================================

REM 设置环境变量
set PORTABLE_MODE=1
set PLAYWRIGHT_BROWSERS_PATH=%~dp0bin\browsers
set PYTHONPATH=%~dp0

REM 使用便携式 Python
if exist "%~dp0python\python.exe" (
    echo [信息] 使用便携式 Python: %~dp0python\python.exe
    "%~dp0python\python.exe" --version
    echo.
    
    echo [信息] 启动 API 服务...
    "%~dp0python\python.exe" main.py --serve
) else (
    echo [错误] 未找到便携式 Python
    echo 请确保 python 目录存在
    pause
    exit /b 1
)