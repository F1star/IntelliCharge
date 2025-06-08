@echo off
chcp 936 >nul
echo ===== IntelliCharge项目启动脚本 =====
echo.

REM 检查Python是否已安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Python，请先安装Python 3.8或更高版本
    pause
    exit /b 1
)

REM 检查Node.js是否已安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未检测到Node.js，请先安装Node.js 16.x或更高版本
    pause
    exit /b 1
)

echo [信息] 检测到Python和Node.js已安装

REM 检查虚拟环境是否存在
if not exist "venv\" (
    echo [警告] 未找到Python虚拟环境，请先运行setup_backend.bat配置后端环境
    pause
    exit /b 1
)

REM 检查前端依赖是否已安装
if not exist "frontEnd\node_modules\" (
    echo [警告] 未找到前端依赖，请先运行setup_frontend.bat配置前端环境
    pause
    exit /b 1
)

echo [信息] 环境检查完成，准备启动项目...

REM 启动后端服务
echo [信息] 正在启动后端服务...
start cmd /k "chcp 936 >nul && call venv\Scripts\activate.bat && cd backEnd && python run.py"

REM 等待几秒钟让后端启动
echo [信息] 等待后端服务启动...
timeout /t 5 /nobreak >nul

REM 启动前端服务
echo [信息] 正在启动前端服务...
start cmd /k "chcp 936 >nul && cd frontEnd && npm run dev"

echo.
echo [成功] 项目已启动！
echo [信息] 后端服务运行在: http://localhost:3000
echo [信息] 前端服务运行在: http://localhost:5173
echo [信息] 请在浏览器中访问前端地址以使用应用
echo.
echo 按任意键退出此脚本（不会关闭已启动的服务）
pause > nul 