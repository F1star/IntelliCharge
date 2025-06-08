# IntelliCharge后端环境配置指南

本文档提供了如何使用一键配置脚本来设置和运行IntelliCharge后端环境的说明。

## 前提条件

- Python 3.8或更高版本
- 对于Windows用户：命令提示符(CMD)或PowerShell
- 对于Linux/macOS用户：终端

## 使用方法

### Windows用户

1. 在项目根目录下找到`setup_backend.bat`文件
2. 双击该文件或在命令提示符中运行：
   ```
   setup_backend.bat
   ```
3. 脚本将自动执行以下操作：
   - 检查Python是否已安装
   - 创建虚拟环境（如果不存在）
   - 安装所需依赖
   - 初始化数据库
   - 询问是否立即启动后端服务

### Linux/macOS用户

1. 在项目根目录下找到`setup_backend.sh`文件
2. 首先确保脚本有执行权限：
   ```
   chmod +x setup_backend.sh
   ```
3. 然后运行脚本：
   ```
   ./setup_backend.sh
   ```
4. 脚本将自动执行与Windows版本相同的操作

## 脚本功能

这些脚本会自动完成以下任务：

1. 检查Python是否已安装
2. 创建Python虚拟环境（如果不存在）
3. 激活虚拟环境
4. 创建requirements.txt文件（如果不存在）
5. 安装所需的Python依赖
6. 初始化数据库
7. 提供选项立即启动后端服务或稍后手动启动

## 手动启动后端服务

如果您选择不立即启动后端服务，可以稍后通过以下步骤手动启动：

1. 激活虚拟环境：
   - Windows: `venv\Scripts\activate.bat`
   - Linux/macOS: `source venv/bin/activate`
2. 进入后端目录：`cd backEnd`
3. 运行后端服务：`python run.py`

## 故障排除

如果遇到问题：

1. 确保已安装Python 3.8或更高版本
2. 确保有足够的权限创建文件和目录
3. 检查网络连接以确保可以下载依赖包
4. 如果数据库初始化失败，检查数据库配置是否正确 