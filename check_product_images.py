#!/usr/bin/env python
"""检查产品图片数据"""
from app import create_app
from app.models import db, Product, ProductImage

app = create_app()
with app.app_context():
    print('=== 检查 SP008 产品图片 ===')
    product = Product.query.filter_by(product_code='SP008').first()
    
    if not product:
        print('未找到产品 SP008')
        # 显示所有产品
        print('\n=== 所有产品列表 ===')
        products = Product.query.all()
        for p in products[:10]:
            img_count = p.images.count()
            print(f'{p.product_code} - {p.name} - 图片数: {img_count}')
    else:
        print(f'产品名称: {product.name}')
        print(f'产品ID: {product.id}')
        print(f'图片数量: {product.images.count()}')
        
        print('\n=== 图片详情 ===')
        for idx, img in enumerate(product.images.all()):
            print(f'[{idx+1}] ID: {img.id}')
            print(f'    URL: {img.image_url}')
            print(f'    主图: {"是" if img.is_primary else "否"}')
            print(f'    排序: {img.sort_order}')
            print()
    
    print('\n=== 检查图片URL格式 ===')
    all_images = ProductImage.query.limit(10).all()
    for img in all_images:
        print(f'ID {img.id}: {img.image_url[:80]}...')
