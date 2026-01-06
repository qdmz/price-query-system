#!/usr/bin/env python
"""
检查订单数据
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db, Order, OrderItem

app = create_app()

with app.app_context():
    print("=" * 60)
    print("订单数据检查")
    print("=" * 60)
    
    orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    print(f"\n最近10个订单:")
    for o in orders:
        items = OrderItem.query.filter_by(order_id=o.id).all()
        print(f"\n订单号: {o.order_no}")
        print(f"  客户: {o.customer_name}")
        print(f"  电话: {o.customer_phone}")
        print(f"  金额: ¥{o.total_amount}")
        print(f"  数量: {o.total_quantity}")
        print(f"  状态: {o.status}")
        print(f"  通知: {'已通知' if o.notified else '未通知'}")
        print(f"  时间: {o.created_at}")
        print(f"  商品数量: {len(items)}")
        
        if items:
            for item in items[:3]:  # 只显示前3个商品
                print(f"    - {item.product_code} {item.product_name} x{item.quantity} @¥{item.unit_price}")
