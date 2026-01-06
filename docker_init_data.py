#!/usr/bin/env python
"""
Docker环境数据初始化脚本
在Docker容器启动时自动执行，用于初始化系统数据
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db, Product, ProductImage, User, Order
from init_data import create_default_admin, create_default_settings, create_default_products, add_product_images
from init_data import generate_orders_for_month


def docker_init():
    """Docker环境初始化"""
    app = create_app('production')

    with app.app_context():
        print("=" * 60)
        print("Docker环境数据初始化开始...")
        print("=" * 60)

        # 1. 创建管理员账户
        print("\n[1/5] 创建管理员账户...")
        create_default_admin(app)

        # 2. 创建系统设置
        print("\n[2/5] 创建系统设置...")
        create_default_settings(app)

        # 3. 创建产品数据
        print("\n[3/5] 创建产品数据...")
        create_default_products(app)

        # 4. 为产品添加图片
        print("\n[4/5] 为产品添加图片...")
        add_product_images(app)

        # 5. 生成测试订单
        print("\n[5/5] 生成测试订单...")
        # 生成最近3个月的订单数据
        from datetime import datetime
        current_year = datetime.now().year
        current_month = datetime.now().month

        for i in range(3):
            month = current_month - i
            year = current_year
            if month <= 0:
                month += 12
                year -= 1
            count = generate_orders_for_month(app, year, month, 30)
            print(f"  {year}年{month}月: 生成 {count} 个订单")

        # 统计数据
        print("\n" + "=" * 60)
        print("初始化完成！数据统计:")
        print("=" * 60)
        print(f"用户数: {User.query.count()}")
        print(f"产品数: {Product.query.count()}")
        print(f"产品图片数: {ProductImage.query.count()}")
        print(f"订单数: {Order.query.count()}")
        print("=" * 60)

        # 创建初始化标志文件
        with open('/app/.docker_initialized', 'w') as f:
            f.write('initialized')


if __name__ == '__main__':
    try:
        docker_init()
        print("\n✓ 数据初始化成功！")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ 数据初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
