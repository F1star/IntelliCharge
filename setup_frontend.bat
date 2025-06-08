@echo off
chcp 936 >nul
echo ===== IntelliCharge前端环境配置脚本 =====
echo.

REM 检查Node.js是否已安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js，请先安装Node.js 16.x或更高版本
    pause
    exit /b 1
)

echo [信息] 检测到Node.js已安装

REM 进入前端目录
cd frontEnd

REM 检查package.json是否存在
if not exist "package.json" (
    echo [错误] 未找到package.json文件，请确保您在正确的目录中
    cd ..
    pause
    exit /b 1
)

REM 安装依赖
echo [信息] 正在安装依赖...
call npm install
if %errorlevel% neq 0 (
    echo [错误] 安装依赖失败
    cd ..
    pause
    exit /b 1
)
echo [成功] 依赖安装完成

REM 询问是否立即启动前端服务
echo.
set /p start_frontend="是否立即启动前端服务？(y/n): "
if /i "%start_frontend%"=="y" (
    echo [信息] 正在启动前端服务...
    call npm run dev
) else (
    echo.
    echo [信息] 如需手动启动前端服务，请执行以下命令：
    echo   cd frontEnd
    echo   npm run dev
    cd ..
    pause
) 