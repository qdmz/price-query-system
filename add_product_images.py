#!/usr/bin/env python
"""
为产品添加网络图片
使用Unsplash等免费图库的图片
"""
import sys
import os
import requests

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db, Product, ProductImage
from app.services.product_service import ProductService

# Unsplash免费图片URL（日用产品相关）
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
        'https://images.unsplash.com/photo-1615117922848-870b4b4a474f?w=400&h=400&fit=crop'
    ],
    '洗洁精': [
        'https://images.unsplash.com/photo-1576432624372-9709e0e1f0d1?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1615634260167-c8cdede054de?w=400&h=400&fit=crop'
    ],
    '拖把': [
        'https://images.unsplash.com/photo-1581578731117-104f2a2c83c6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=400&fit=crop'
    ],
    '扫帚': [
        'https://images.unsplash.com/photo-1581578731117-104f2a2c83c6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1558494949-ef010cbdcc31?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400&h=400&fit=crop'
    ],
    '毛巾': [
        'https://images.unsplash.com/photo-1582139329536-e7284fece509?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1587909209111-5097ee578ec3?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1604014237800-1c9102c219da?w=400&h=400&fit=crop'
    ],
    '水杯': [
        'https://images.unsplash.com/photo-1514228742587-6b1558fcca3d?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1602143407151-011141950038?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1544145945-f90425340c7e?w=400&h=400&fit=crop'
    ],
    '菜板': [
        'https://images.unsplash.com/photo-1594549181132-9045fed330ce?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1590794056226-79ef3a8147e1?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?w=400&h=400&fit=crop'
    ],
    '餐具': [
        'https://images.unsplash.com/photo-1584634731339-252c581abfc5?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1530018607912-eff2daa1bac4?w=400&h=400&fit=crop'
    ],
    '湿巾': [
        'https://images.unsplash.com/photo-1584100936595-c0654b55a2e6?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop',
        'https://images.unsplash.com/photo-1615117922848-870b4b4a474f?w=400&h=400&fit=crop'
    ]
}


def match_product_images(product_name):
    """根据产品名称匹配图片"""
    for keyword, urls in PRODUCT_IMAGES.items():
        if keyword in product_name:
            return urls
    return None


def add_product_images():
    """为产品添加网络图片"""
    app = create_app()
    
    with app.app_context():
        # 获取所有产品
        products = Product.query.all()
        
        print("=" * 60)
        print("开始为产品添加网络图片...")
        print("=" * 60)
        
        success_count = 0
        failed_count = 0
        skip_count = 0
        
        for product in products:
            print(f"\n处理产品: {product.product_code} - {product.name}")
            
            # 检查是否已有图片
            if product.images.count() >= 3:
                print(f"  ⚠ 已有 {product.images.count()} 张图片，跳过")
                skip_count += 1
                continue
            
            # 匹配图片
            image_urls = match_product_images(product.name)
            
            if not image_urls:
                print(f"  ⚠ 未找到匹配的图片")
                skip_count += 1
                continue
            
            # 下载并添加图片
            added = 0
            for idx, url in enumerate(image_urls):
                try:
                    # 下载图片
                    downloaded_url = ProductService.download_image_from_url(url, product.id)
                    
                    if downloaded_url:
                        # 创建图片记录
                        is_primary = (idx == 0)
                        image = ProductImage(
                            product_id=product.id,
                            image_url=downloaded_url,
                            is_primary=is_primary,
                            sort_order=idx
                        )
                        db.session.add(image)
                        added += 1
                        print(f"  ✓ 图片 {idx+1} 添加成功")
                    else:
                        print(f"  ✗ 图片 {idx+1} 下载失败")
                        
                except Exception as e:
                    print(f"  ✗ 图片 {idx+1} 添加失败: {e}")
            
            if added > 0:
                db.session.commit()
                success_count += 1
                print(f"  成功添加 {added} 张图片")
            else:
                db.session.rollback()
                failed_count += 1
        
        print("\n" + "=" * 60)
        print(f"处理完成！")
        print(f"成功: {success_count} 个产品")
        print(f"失败: {failed_count} 个产品")
        print(f"跳过: {skip_count} 个产品")
        print("=" * 60)


if __name__ == '__main__':
    add_product_images()
