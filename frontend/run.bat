@echo off
chcp 65001 >nul
echo ========================================
echo  SeniorStrength Flutter APP启动脚本
echo ========================================
echo.

REM 获取当前目录
set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

REM 检查Flutter
flutter --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Flutter，请先安装Flutter
    echo 下载地址：https://docs.flutter.dev/get-started/install
    echo.
    echo 或者在VS Code中安装Flutter插件后重试
    pause
    exit /b 1
)

REM 获取依赖
echo [1/3] 获取Flutter依赖...
call flutter pub get
if errorlevel 1 (
    echo [错误]依赖获取失败
    pause
    exit /b 1
)

REM 检查设备
echo [2/3] 检查设备...
flutter devices

REM 运行
echo [3/3] 启动APP...
echo.
echo ========================================
echo  如果没有自动选择设备，请手动运行：
echo  flutter run -d<device_id>
echo.
echo  设备列表见上方
echo ========================================
echo.
flutter run

pause