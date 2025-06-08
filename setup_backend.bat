@echo off
chcp 936 >nul
echo ===== IntelliCharge后端环境配置脚本 =====
echo.

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

echo [信息] 检测到Python已安装

REM 创建虚拟环境（如果不存在）
if not exist "venv\" (
    echo [信息] 正在创建虚拟环境...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
    echo [成功] 虚拟环境创建完成
) else (
    echo [信息] 虚拟环境已存在
)

REM 激活虚拟环境
echo [信息] 正在激活虚拟环境...
call venv\Scripts\activate.bat

REM 创建requirements.txt文件（如果不存在）
if not exist "requirements.txt" (
    echo [信息] 正在创建requirements.txt文件...
    echo flask==2.0.1 > requirements.txt
    echo flask-cors==3.0.10 >> requirements.txt
    echo werkzeug==2.0.2 >> requirements.txt
    echo asgiref >> requirements.txt
    echo SQLAlchemy==1.4.23 >> requirements.txt
    echo pymysql==1.0.2 >> requirements.txt
    echo cryptography==3.4.8 >> requirements.txt
    echo python-dotenv==0.19.0 >> requirements.txt
    echo [成功] requirements.txt文件创建完成
)

REM 安装依赖
echo [信息] 正在安装依赖...
pip install -r requirements.txt
echo [信息] 正在安装Flask异步支持...
pip install "flask[async]"
if %errorlevel% neq 0 (
    echo [错误] 安装依赖失败
    pause
    exit /b 1
)
echo [成功] 依赖安装完成

REM 初始化数据库
echo [信息] 正在初始化数据库...
cd backEnd
python init_db.py
if %errorlevel% neq 0 (
    echo [警告] 数据库初始化可能未完全成功，请检查错误信息
) else (
    echo [成功] 数据库初始化完成
)

REM 询问是否立即启动后端服务
echo.
set /p start_server="是否立即启动后端服务？(y/n): "
if /i "%start_server%"=="y" (
    echo [信息] 正在启动后端服务...
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