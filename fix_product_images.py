#!/usr/bin/env python
"""修复产品图片数据"""
from app import create_app
from app.models import db, ProductImage

app = create_app()
with app.app_context():
    print('=== 检查并修复产品图片数据 ===')
    
    # 获取所有使用占位图的图片记录
    placeholder_images = ProductImage.query.filter(
        ProductImage.image_url.like('%product-placeholder%')
    ).all()
    
    print(f'\n发现 {len(placeholder_images)} 个占位图记录')
    
    # 更新占位图路径
    for img in placeholder_images:
        old_url = img.image_url
        # 确保使用 .jpg 后缀
        img.image_url = '/static/images/product-placeholder.jpg'
        print(f'更新图片 ID {img.id}: {old_url} -> {img.image_url}')
    
    db.session.commit()
    
    # 统计图片类型
    print('\n=== 图片统计 ===')
    all_images = ProductImage.query.all()
    placeholder_count = len([img for img in all_images if 'placeholder' in img.image_url])
    upload_count = len([img for img in all_images if 'uploads' in img.image_url])
    
    print(f'占位图: {placeholder_count}')
    print(f'上传图片: {upload_count}')
    print(f'总计: {len(all_images)}')
    
    # 显示最近的图片示例
    print('\n=== 前10个图片示例 ===')
    for img in all_images[:10]:
        product_name = img.product.name if img.product else '未知'
        print(f'产品: {product_name}, URL: {img.image_url}')
