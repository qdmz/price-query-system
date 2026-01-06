#!/usr/bin/env python
"""查找卫生纸产品"""
from app import create_app
from app.models import db, Product, ProductImage

app = create_app()
with app.app_context():
    print('=== 搜索包含"卫生纸"或"卷纸"的产品 ===')
    products = Product.query.filter(
        (Product.name.contains('卫生纸')) | (Product.name.contains('卷纸'))
    ).all()
    
    if not products:
        print('未找到包含"卫生纸"或"卷纸"的产品')
    else:
        for p in products:
            print(f'\n产品代码: {p.product_code}')
            print(f'产品名称: {p.name}')
            print(f'产品ID: {p.id}')
            print(f'图片数量: {p.images.count()}')
            
            for idx, img in enumerate(p.images.all()):
                print(f'  [{idx+1}] {img.image_url} (主图: {"是" if img.is_primary else "否"})')
