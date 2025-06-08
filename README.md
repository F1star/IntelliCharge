# IntelliCharge 项目

IntelliCharge 是一个全栈应用程序，包含Vue.js前端和Flask后端。本文档提供了如何配置和运行整个项目的详细说明。

## 项目结构

```
IntelliCharge/
├── frontEnd/           # Vue.js 前端
├── backEnd/            # Flask 后端
├── setup_backend.bat   # Windows 后端配置脚本
├── setup_backend.sh    # Linux/macOS 后端配置脚本
├── setup_frontend.bat  # Windows 前端配置脚本
├── setup_frontend.sh   # Linux/macOS 前端配置脚本
├── start_project.bat   # Windows 一键启动整个项目脚本
├── start_project.sh    # Linux/macOS 一键启动整个项目脚本
└── README.md           # 本文档
```

## 系统要求

- **后端**：
  - Python 3.8 或更高版本
  - MySQL 数据库（可选，取决于项目配置）

- **前端**：
  - Node.js 16.x 或更高版本
  - npm 或 yarn 包管理器

## 快速开始（推荐）

### Windows 用户

1. **一键配置和启动整个项目**：
   - 首先运行 `setup_backend.bat` 配置后端环境
   - 然后运行 `setup_frontend.bat` 配置前端环境
   - 最后运行 `start_project.bat` 一键启动整个项目

2. **分别配置**：
   - 后端配置：运行 `setup_backend.bat`
   - 前端配置：运行 `setup_frontend.bat`

### Linux/macOS 用户

1. **一键配置和启动整个项目**：
   - 首先运行 `chmod +x *.sh` 赋予所有脚本执行权限
   - 然后运行 `./setup_backend.sh` 配置后端环境
   - 接着运行 `./setup_frontend.sh` 配置前端环境
   - 最后运行 `./start_project.sh` 一键启动整个项目

2. **分别配置**：
   - 后端配置：运行 `./setup_backend.sh`
   - 前端配置：运行 `./setup_frontend.sh`

## 配置和运行后端

### 自动配置（推荐）

#### Windows 用户

1. 在项目根目录下找到 `setup_backend.bat` 文件
2. 双击该文件或在命令提示符中运行：
   ```
   setup_backend.bat
   ```
3. 脚本将自动执行以下操作：
   - 检查 Python 是否已安装
   - 创建虚拟环境（如果不存在）
   - 安装所需依赖
   - 初始化数据库
   - 询问是否立即启动后端服务

#### Linux/macOS 用户

1. 在项目根目录下找到 `setup_backend.sh` 文件
2. 首先确保脚本有执行权限：
   ```
   chmod +x setup_backend.sh
   ```
3. 然后运行脚本：
   ```
   ./setup_backend.sh
   ```

### 手动配置

如果您希望手动配置后端，请按照以下步骤操作：

1. 创建并激活 Python 虚拟环境：
   ```
   # Windows
   python -m venv venv
   venv\Scripts\activate.bat

   # Linux/macOS
   python3 -m venv venv
   source venv/bin/activate
   ```

2. 安装依赖：
   ```
   pip install flask==2.0.1 flask-cors==3.0.10 werkzeug==2.0.2 asgiref SQLAlchemy==1.4.23 pymysql==1.0.2 cryptography==3.4.8 python-dotenv==0.19.0
   pip install "flask[async]"
   ```

3. 初始化数据库：
   ```
   cd backEnd
   python init_db.py
   ```

4. 运行后端服务：
   ```
   python run.py
   ```

## 配置和运行前端

### 自动配置（推荐）

#### Windows 用户

1. 在项目根目录下找到 `setup_frontend.bat` 文件
2. 双击该文件或在命令提示符中运行：
   ```
   setup_frontend.bat
   ```
3. 脚本将自动执行以下操作：
   - 检查 Node.js 是否已安装
   - 安装所需依赖
   - 询问是否立即启动前端服务

#### Linux/macOS 用户

1. 在项目根目录下找到 `setup_frontend.sh` 文件
2. 首先确保脚本有执行权限：
   ```
   chmod +x setup_frontend.sh
   ```
3. 然后运行脚本：
   ```
   ./setup_frontend.sh
   ```

### 手动配置

1. 进入前端目录：
   ```
   cd frontEnd
   ```

2. 安装依赖包：
   ```
   npm install
   # 或者使用 yarn
   yarn
   ```

3. 开发模式运行：
   ```
   npm run dev
   # 或者使用 yarn
   yarn dev
   ```

这将启动开发服务器，通常在 http://localhost:5173 上可以访问。

### 构建生产版本

在前端目录下执行：
```
npm run build
# 或者使用 yarn
yarn build
```

构建完成后，生成的文件将位于 `frontEnd/dist` 目录中。

## 一键启动整个项目

### Windows 用户

1. 确保已经运行过 `setup_backend.bat` 和 `setup_frontend.bat` 配置好环境
2. 双击运行 `start_project.bat` 或在命令提示符中执行：
   ```
   start_project.bat
   ```
3. 脚本将自动在两个独立的命令窗口中启动后端和前端服务

### Linux/macOS 用户

1. 确保已经运行过 `./setup_backend.sh` 和 `./setup_frontend.sh` 配置好环境
2. 确保脚本有执行权限：
   ```
   chmod +x start_project.sh
   ```
3. 运行脚本：
   ```
   ./start_project.sh
   ```
4. 脚本将尝试在新的终端窗口中启动后端和前端服务

## 常见问题解决

### 后端问题

1. **数据库连接错误**：
   - 检查 `backEnd/config/db_config.py` 中的数据库配置是否正确
   - 确保数据库服务正在运行

2. **依赖安装失败**：
   - 尝试使用 `pip install --upgrade pip` 更新 pip
   - 检查网络连接
   - 如果某个特定依赖安装失败，尝试单独安装它

### 前端问题

1. **Node.js 版本兼容性**：
   - 使用 Node.js 16.x 或更高版本
   - 可以使用 nvm 管理多个 Node.js 版本

2. **依赖安装错误**：
   - 删除 `node_modules` 目录和 `package-lock.json` 文件，然后重新运行 `npm install`
   - 检查网络连接

3. **端口冲突**：
   - 如果端口已被占用，可以在 `vite.config.js` 中修改端口配置

## 部署指南

### 后端部署

1. 在生产服务器上安装 Python 和所需依赖
2. 配置生产环境的数据库
3. 使用 Gunicorn 或 uWSGI 作为 WSGI 服务器
4. 配置 Nginx 作为反向代理

### 前端部署

1. 构建生产版本：`npm run build`
2. 将 `dist` 目录中的文件部署到 Web 服务器
3. 配置 Nginx 或其他 Web 服务器提供静态文件

## 贡献指南

1. Fork 本仓库
2. 创建您的特性分支：`git checkout -b feature/amazing-feature`
3. 提交您的更改：`git commit -m 'Add some amazing feature'`
4. 推送到分支：`git push origin feature/amazing-feature`
5. 提交拉取请求