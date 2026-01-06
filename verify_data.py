#!/usr/bin/env python
"""验证数据初始化状态"""
from app import create_app
from app.models import db, Product, Order, ProductImage, Category

app = create_app()
with app.app_context():
    print('=== 数据库状态检查 ===')
    print(f'产品数量: {Product.query.count()}')
    print(f'订单数量: {Order.query.count()}')
    print(f'分类数量: {Category.query.count()}')
    print(f'产品图片数量: {ProductImage.query.count()}')
    
    print('\n=== 最近5个订单 ===')
    for order in Order.query.order_by(Order.created_at.desc()).limit(5).all():
        print(f'订单号: {order.order_no}, 客户: {order.customer_name}, 金额: ¥{order.total_amount:.2f}, 状态: {order.status}')
    
    print('\n=== 产品分类统计 ===')
    for category in Category.query.all():
        product_count = Product.query.filter_by(category_id=category.id).count()
        print(f'{category.name}: {product_count} 个产品')
