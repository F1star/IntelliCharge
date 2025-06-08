#!/bin/bash

echo "===== IntelliCharge后端环境配置脚本 ====="
echo

# 检查Python是否已安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python，请先安装Python 3.8或更高版本"
    exit 1
fi

echo "[信息] 检测到Python已安装"

# 创建虚拟环境（如果不存在）
if [ ! -d "venv" ]; then
    echo "[信息] 正在创建虚拟环境..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[错误] 创建虚拟环境失败"
        exit 1
    fi
    echo "[成功] 虚拟环境创建完成"
else
    echo "[信息] 虚拟环境已存在"
fi

# 激活虚拟环境
echo "[信息] 正在激活虚拟环境..."
source venv/bin/activate

# 创建requirements.txt文件（如果不存在）
if [ ! -f "requirements.txt" ]; then
    echo "[信息] 正在创建requirements.txt文件..."
    cat > requirements.txt << EOF
flask==2.0.1
flask-cors==3.0.10
werkzeug==2.0.2
asgiref
SQLAlchemy==1.4.23
pymysql==1.0.2
cryptography==3.4.8
python-dotenv==0.19.0
EOF
    echo "[成功] requirements.txt文件创建完成"
fi

# 安装依赖
echo "[信息] 正在安装依赖..."
pip install -r requirements.txt
echo "[信息] 正在安装Flask异步支持..."
pip install "flask[async]"
if [ $? -ne 0 ]; then
    echo "[错误] 安装依赖失败"
    exit 1
fi
echo "[成功] 依赖安装完成"

# 初始化数据库
echo "[信息] 正在初始化数据库..."
cd backEnd
python init_db.py
if [ $? -ne 0 ]; then
    echo "[警告] 数据库初始化可能未完全成功，请检查错误信息"
else
    echo "[成功] 数据库初始化完成"
fi

# 询问是否立即启动后端服务
echo
read -p "是否立即启动后端服务？(y/n): " start_server
if [[ "$start_server" == "y" || "$start_server" == "Y" ]]; then
    echo "[信息] 正在启动后端服务..."
    python run.py
else
    echo
    echo "[信息] 如需手动启动后端服务，请执行以下命令："
    echo "  cd backEnd"
    echo "  python run.py"
fi 