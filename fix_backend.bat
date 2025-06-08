@echo off
chcp 936 >nul
echo ===== IntelliCharge后端环境修复脚本 =====
echo.

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo [信息] 检测到Python已安装

REM 检查虚拟环境是否存在
if not exist "venv\" (
    echo [错误] 未找到虚拟环境，请先运行setup_backend.bat创建环境
    pause
    exit /b 1
)

REM 激活虚拟环境
echo [信息] 正在激活虚拟环境...
call venv\Scripts\activate.bat

REM 修复依赖
echo [信息] 正在修复依赖问题...
pip uninstall -y werkzeug
pip install werkzeug==2.0.2

echo [信息] 正在安装异步支持...
pip install asgiref
pip install "flask[async]"

if %errorlevel% neq 0 (
    echo [错误] 依赖修复失败
    pause
    exit /b 1
)
echo [成功] 依赖修复完成

REM 询问是否立即启动后端服务
echo.
set /p start_server="是否立即启动后端服务？(y/n): "
if /i "%start_server%"=="y" (
    echo [信息] 正在启动后端服务...
    cd backEnd
    python run.py
) else (
    echo.
    echo [信息] 如需手动启动后端服务，请执行以下命令：
    echo   cd backEnd
    echo   python run.py
)

REM 如果没有立即启动服务，保持命令行窗口打开
if /i not "%start_server%"=="y" (
    pause
) 