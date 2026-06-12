@echo off
chcp 65001 >nul
echo ========================================
echo  SeniorStrength 后端启动脚本
echo ========================================
echo.

REM 获取当前目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.11+
    echo 下载地址：https://www.python.org/downloads/
    pause
    exit /b 1
)

REM 创建虚拟环境
echo [1/4] 创建虚拟环境...
if not exist "venv" (
    python -m venv venv
)

REM 激活虚拟环境
echo [2/4] 安装依赖...
call venv\Scripts\activate

REM 升级pip
python -m pip install --upgrade pip >nul 2>&1

REM 安装依赖
pip install -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo [错误]依赖安装失败，请检查requirements.txt
    pause
    exit /b 1
)

REM 初始化数据
echo [3/4] 初始化数据库...
python seed_data.py

REM 启动服务
echo [4/4] 启动后端服务...
echo.
echo ========================================
echo  服务已启动！
echo  API文档：http://localhost:8000/docs
echo  按 Ctrl+C 停止服务
echo ========================================
echo.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause