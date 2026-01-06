#!/usr/bin/env python
"""检查具体产品的图片"""
from app import create_app
from app.models import db, Product, ProductImage

app = create_app()
with app.app_context():
    # 查找 SP008 产品
    product = Product.query.filter_by(product_code='SP008').first()
    
    if not product:
        print('未找到产品 SP008')
        print('\n=== 搜索包含"卫生纸"的产品 ===')
        products = Product.query.filter(Product.name.contains('卫生纸')).all()
        if products:
            for p in products:
                print(f'产品代码: {p.product_code}, 产品名称: {p.name}, ID: {p.id}')
                print(f'图片数量: {p.images.count()}')
                for idx, img in enumerate(p.images.all()):
                    print(f'  [{idx+1}] {img.image_url} (主图: {"是" if img.is_primary else "否"})')
        else:
            print('未找到包含"卫生纸"的产品')
            
        # 显示所有产品
        print('\n=== 所有产品列表（前20个）===')
        all_products = Product.query.order_by(Product.id).limit(20).all()
        for p in all_products:
            img_count = p.images.count()
            print(f'{p.product_code} - {p.name} (ID: {p.id}) - 图片数: {img_count}')
    else:
        print(f'=== 产品 SP008 ({product.name}) ===')
        print(f'产品ID: {product.id}')
        print(f'图片数量: {product.images.count()}')
        
        for idx, img in enumerate(product.images.all()):
            print(f'\n[{idx+1}] 图片ID: {img.id}')
            print(f'    URL: {img.image_url}')
            print(f'    主图: {"是" if img.is_primary else "否"}')
            print(f'    排序: {img.sort_order}')
