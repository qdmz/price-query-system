#!/usr/bin/env python
"""
为SP系列产品添加图片的脚本
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db, Product, ProductImage
from app.services.product_service import ProductService

# Unsplash图片URL映射
PRODUCT_IMAGES = {
    '牙膏': [
        'https://images.unsplash.com/photo-1607613009820-a29f7bb81c04?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1556227702-d1e4e7b5c232?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1608571423902-eed4a5ad8108?w=400&h=400&fit=crop'
    ],
    '洗发水': [
        'https://images.unsplash.com/photo-1631729371254-42c2892f0e6e?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1556228720-195a672e8a03?w=400&h=400&fit=crop'
    ],
    '沐浴露': [
        'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1603360946369-dc9bb6258143?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1595425970377-c9703cf48b6d?w=400&h=400&fit=crop'
    ],
    '洗衣液': [
        'https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1615634260167-c8cdede054de?w=400&h=400&fit=crop'
    ],
    '洗洁精': [
        'https://images.unsplash.com/photo-1576432624372-9709e0e1f0d1?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1615634260167-c8cdede054de?w=400&h=400&fit=crop'
    ],
    '毛巾': [
        'https://images.unsplash.com/photo-1582139329536-e7284fece509?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1587909209111-5097ee578ec3?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1604014237800-1c9102c219da?w=400&h=400&fit=crop'
    ],
    '纸巾': [
        'https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1615117922848-870b4b4a474f?w=400&h=400&fit=crop'
    ],
    '卫生纸': [
        'https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1615117922848-870b4b4a474f?w=400&h=400&fit=crop'
    ],
    '垃圾袋': [
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1581578731117-104f2a2c83c6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop'
    ],
    '护手霜': [
        'https://images.unsplash.com/photo-1608248543803-ba4f8c70ae0b?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1603360946369-dc9bb6258143?w=400&h=400&fit=crop'
    ]
}


def match_product_images(product_name):
    """根据产品名称匹配图片"""
    for keyword, urls in PRODUCT_IMAGES.items():
        if keyword in product_name:
            return urls
    return None


def fix_sp_product_images():
    """为SP系列产品添加图片"""
    app = create_app('production')
    
    with app.app_context():
        print("=" * 60)
        print("为SP系列产品添加图片...")
        print("=" * 60)
        
        # 获取所有SP系列产品
        products = Product.query.filter(Product.product_code.like('SP%')).all()
        
        success_count = 0
        failed_count = 0
        
        for product in products:
            # 删除现有图片（如果是占位符）
            for img in product.images.all():
                if 'placeholder' in img.image_url:
                    db.session.delete(img)
            db.session.commit()
            
            # 匹配图片
            image_urls = match_product_images(product.name)
            
            if not image_urls:
                print(f"跳过 {product.product_code} - {product.name} (未找到匹配图片)")
                failed_count += 1
                continue
            
            # 添加图片
            added = 0
            for idx, url in enumerate(image_urls):
                try:
                    # 直接使用Unsplash URL（不下载到本地）
                    image = ProductImage(
                        product_id=product.id,
                        image_url=url,
                        is_primary=(idx == 0),
                        sort_order=idx
                    )
                    db.session.add(image)
                    added += 1
                    
                except Exception as e:
                    print(f"添加图片失败: {e}")
                    pass
            
            if added > 0:
                db.session.commit()
                print(f"✓ {product.product_code} - {product.name} (添加 {added} 张图片)")
                success_count += 1
            else:
                db.session.rollback()
                failed_count += 1
        
        print("=" * 60)
        print(f"图片添加完成 - 成功: {success_count}, 失败: {failed_count}")
        print("=" * 60)


if __name__ == '__main__':
    fix_sp_product_images()
