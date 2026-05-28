#!/bin/bash

# 启动脚本

echo "=== 翻墙数据可视化系统 ==="

# 检查 Python 版本
python3 --version

# 安装依赖
echo "安装 Python 依赖..."
pip3 install -r requirements.txt

# 启动后端
echo "启动后端服务..."
python3 main.py &

echo "后端服务已启动，访问地址：http://localhost:8000"
echo "API 文档地址：http://localhost:8000/docs"
echo ""
echo "前端页面：请打开 frontend/index.html"
