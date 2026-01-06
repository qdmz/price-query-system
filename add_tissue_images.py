#!/usr/bin/env python
"""为卫生纸产品添加图片"""
from app import create_app
from app.models import db, Product, ProductImage
from app.services.product_service import ProductService

app = create_app()
with app.app_context():
    # 找到 SP018 产品
    product = Product.query.filter_by(product_code='SP018').first()
    
    if not product:
        print('未找到产品 SP018')
    else:
        print(f'=== 为产品 {product.name} (ID: {product.id}) 添加图片 ===')
        
        # Unsplash上卫生纸相关的图片URL
        tissue_image_urls = [
            'https://images.unsplash.com/photo-1629198688000-71f23e745b6e?w=400&h=400&fit=crop',
            'https://images.unsplash.com/photo-1586036393667-965338f0f908?w=400&h=400&fit=crop',
            'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=400&fit=crop'
        ]
        
        # 删除旧的占位图
        old_images = ProductImage.query.filter_by(product_id=product.id).all()
        for old_img in old_images:
            db.session.delete(old_img)
            print(f'  删除旧图片: {old_img.image_url}')
        
        db.session.flush()
        
        # 下载新图片
        for idx, url in enumerate(tissue_image_urls):
            print(f'  正在下载图片 {idx+1}: {url}')
            downloaded_url = ProductService.download_image_from_url(url, product.id)
            
            if downloaded_url:
                image = ProductImage(
                    product_id=product.id,
                    image_url=downloaded_url,
                    is_primary=(idx == 0),
                    sort_order=idx
                )
                db.session.add(image)
                print(f'    ✓ 下载成功: {downloaded_url}')
            else:
                print(f'    ✗ 下载失败')
        
        db.session.commit()
        
        # 显示结果
        print(f'\n=== 结果 ===')
        print(f'当前图片数量: {product.images.count()}')
        for img in product.images.all():
            print(f'  - {img.image_url} (主图: {"是" if img.is_primary else "否"})')
