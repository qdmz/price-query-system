#!/bin/bash

# 启动脚本 - 日用产品批发零售系统

echo "==================================="
echo "日用产品批发零售系统"
echo "==================================="
echo ""

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 检查 .env 文件
if [ ! -f .env ]; then
    echo "创建 .env 文件..."
    cp .env.example .env
    echo "已创建 .env 文件，请根据需要修改配置"
fi

# 构建并启动服务
echo "构建并启动服务..."
docker-compose up -d

# 等待数据库启动
echo "等待数据库启动..."
sleep 10

# 检查服务状态
echo ""
echo "==================================="
echo "服务状态"
echo "==================================="
docker-compose ps

echo ""
echo "==================================="
echo "访问信息"
echo "==================================="
echo "前台页面: http://localhost:5000"
echo "后台管理: http://localhost:5000/admin/dashboard"
echo "默认账号: admin"
echo "默认密码: admin123"
echo ""
echo "查看日志: docker-compose logs -f web"
echo "停止服务: docker-compose down"
echo "==================================="
