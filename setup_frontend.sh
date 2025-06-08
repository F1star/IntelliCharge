#!/bin/bash

echo "===== IntelliCharge前端环境配置脚本 ====="
echo

# 检查Node.js是否已安装
if ! command -v node &> /dev/null; then
    echo "[错误] 未检测到Node.js，请先安装Node.js 16.x或更高版本"
    exit 1
fi

echo "[信息] 检测到Node.js已安装"

# 进入前端目录
cd frontEnd

# 检查package.json是否存在
if [ ! -f "package.json" ]; then
    echo "[错误] 未找到package.json文件，请确保您在正确的目录中"
    cd ..
    exit 1
fi

# 安装依赖
echo "[信息] 正在安装依赖..."
npm install
if [ $? -ne 0 ]; then
    echo "[错误] 安装依赖失败"
    cd ..
    exit 1
fi
echo "[成功] 依赖安装完成"

# 询问是否立即启动前端服务
echo
read -p "是否立即启动前端服务？(y/n): " start_frontend
if [[ "$start_frontend" == "y" || "$start_frontend" == "Y" ]]; then
    echo "[信息] 正在启动前端服务..."
    npm run dev
else
    echo
    echo "[信息] 如需手动启动前端服务，请执行以下命令："
    echo "  cd frontEnd"
    echo "  npm run dev"
    cd ..
fi 