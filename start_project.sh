#!/bin/bash

echo "===== IntelliCharge项目启动脚本 ====="
echo

# 检查Python是否已安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python，请先安装Python 3.8或更高版本"
    exit 1
fi

# 检查Node.js是否已安装
if ! command -v node &> /dev/null; then
    echo "[错误] 未检测到Node.js，请先安装Node.js 16.x或更高版本"
    exit 1
fi

echo "[信息] 检测到Python和Node.js已安装"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "[警告] 未找到Python虚拟环境，请先运行setup_backend.sh配置后端环境"
    exit 1
fi

# 检查前端依赖是否已安装
if [ ! -d "frontEnd/node_modules" ]; then
    echo "[警告] 未找到前端依赖，请先运行setup_frontend.sh配置前端环境"
    exit 1
fi

echo "[信息] 环境检查完成，准备启动项目..."

# 启动后端服务
echo "[信息] 正在启动后端服务..."
gnome-terminal --title="IntelliCharge后端" -- bash -c "source venv/bin/activate && cd backEnd && python run.py; exec bash" 2>/dev/null || \
xterm -T "IntelliCharge后端" -e "source venv/bin/activate && cd backEnd && python run.py; exec bash" 2>/dev/null || \
konsole --new-tab -p tabtitle="IntelliCharge后端" -e "source venv/bin/activate && cd backEnd && python run.py; exec bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'\" && source venv/bin/activate && cd backEnd && python run.py"' 2>/dev/null || \
{
    echo "[警告] 无法在新终端中启动后端，将在当前终端启动"
    echo "[警告] 请在另一个终端窗口中手动启动前端"
    source venv/bin/activate && cd backEnd && python run.py
    exit 0
}

# 等待几秒钟让后端启动
echo "[信息] 等待后端服务启动..."
sleep 5

# 启动前端服务
echo "[信息] 正在启动前端服务..."
gnome-terminal --title="IntelliCharge前端" -- bash -c "cd frontEnd && npm run dev; exec bash" 2>/dev/null || \
xterm -T "IntelliCharge前端" -e "cd frontEnd && npm run dev; exec bash" 2>/dev/null || \
konsole --new-tab -p tabtitle="IntelliCharge前端" -e "cd frontEnd && npm run dev; exec bash" 2>/dev/null || \
osascript -e 'tell app "Terminal" to do script "cd \"'$(pwd)'/frontEnd\" && npm run dev"' 2>/dev/null || \
{
    echo "[警告] 无法在新终端中启动前端，请手动启动前端："
    echo "  cd frontEnd"
    echo "  npm run dev"
}

echo
echo "[成功] 项目已启动！"
echo "[信息] 后端服务运行在: http://localhost:3000"
echo "[信息] 前端服务运行在: http://localhost:5173"
echo "[信息] 请在浏览器中访问前端地址以使用应用" 