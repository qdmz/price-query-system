#!/bin/bash
set -e

# 初始化标志文件路径
INIT_FLAG_FILE="/app/.initialized"

echo "=========================================="
echo "价格查询系统 Docker 容器启动"
echo "=========================================="

# 检查是否为首次启动
if [ ! -f "$INIT_FLAG_FILE" ]; then
    echo ""
    echo "检测到首次启动，正在初始化数据..."
    echo "----------------------------------------"
    
    # 等待数据库就绪
    echo "等待数据库连接..."
    until python -c "import psycopg2; psycopg2.connect('${DATABASE_URL}')" 2>/dev/null; do
        echo "数据库未就绪，等待中..."
        sleep 2
    done
    echo "数据库已就绪"
    
    # 运行数据初始化脚本
    echo "运行数据初始化脚本..."
    python init_data.py
    
    # 创建初始化标志文件
    touch "$INIT_FLAG_FILE"
    
    echo "----------------------------------------"
    echo "数据初始化完成！"
else
    echo "系统已初始化，跳过数据初始化步骤"
fi

echo ""
echo "=========================================="
echo "启动应用服务..."
echo "=========================================="

# 启动Gunicorn服务器
exec gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
