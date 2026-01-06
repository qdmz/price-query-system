#!/usr/bin/env python
"""
检查数据库数据状态
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db, Product, Order, Category, User

app = create_app()

with app.app_context():
    print("=" * 60)
    print("数据库数据状态检查")
    print("=" * 60)
    
    products_count = Product.query.count()
    orders_count = Order.query.count()
    categories_count = Category.query.count()
    users_count = User.query.count()
    
    print(f"\n产品数量: {products_count}")
    print(f"订单数量: {orders_count}")
    print(f"分类数量: {categories_count}")
    print(f"用户数量: {users_count}")
    
    if products_count > 0:
        print(f"\n前5个产品:")
        for p in Product.query.limit(5).all():
            print(f"  - {p.product_code} | {p.name} | 库存: {p.stock}")
    
    if orders_count > 0:
        print(f"\n前5个订单:")
        for o in Order.query.limit(5).all():
            print(f"  - 订单号: {o.order_number} | 客户: {o.customer_name} | 金额: {o.total_amount} | 状态: {o.status}")
    
    print("\n" + "=" * 60)
