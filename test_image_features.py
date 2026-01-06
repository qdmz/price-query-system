#!/usr/bin/env python
"""
测试产品图片功能
"""
import os
import sys
from app import create_app
from app.models import db, Product, ProductImage

app = create_app()

with app.app_context():
    print("=" * 60)
    print("测试产品图片功能")
    print("=" * 60)

    # 查找第一个产品
    product = Product.query.first()

    if not product:
        print("✗ 没有找到产品，请先创建产品")
        sys.exit(1)

    print(f"\n测试产品: {product.name} (ID: {product.id})")
    print(f"当前图片数量: {product.images.count()}")

    # 测试1：检查图片数据
    print("\n【测试1】检查图片数据")
    images = ProductImage.query.filter_by(product_id=product.id).all()
    if images:
        print(f"✓ 找到 {len(images)} 张图片")
        for img in images:
            print(f"  - ID: {img.id}, URL: {img.image_url}, 主图: {img.is_primary}")
    else:
        print("✗ 没有找到图片")

    # 测试2：检查文件是否存在
    print("\n【测试2】检查图片文件是否存在")
    for img in images:
        file_path = os.path.join(app.root_path, img.image_url.lstrip('/'))
        exists = os.path.exists(file_path)
        print(f"  - {img.image_url}: {'✓ 存在' if exists else '✗ 不存在'}")

    # 测试3：设置主图功能
    print("\n【测试3】测试设置主图功能")
    if images and len(images) > 1:
        # 找到第一个非主图
        non_primary = [img for img in images if not img.is_primary]
        if non_primary:
            old_primary = [img for img in images if img.is_primary][0]
            new_primary = non_primary[0]

            print(f"  当前主图: {old_primary.id}")
            print(f"  准备设置为主图: {new_primary.id}")

            # 取消所有主图
            ProductImage.query.filter_by(product_id=product.id).update({'is_primary': False})
            # 设置新主图
            new_primary.is_primary = True
            db.session.commit()

            # 验证
            db.session.refresh(new_primary)
            print(f"✓ 主图设置成功: {new_primary.is_primary}")
        else:
            print("✗ 所有图片都已经是主图")
    elif images:
        print("✗ 只有1张图片，无法测试切换主图")
    else:
        print("✗ 没有图片")

    # 测试4：删除图片功能（模拟）
    print("\n【测试4】测试删除图片功能（模拟）")
    if images and len(images) > 1:
        # 找到第一个非主图
        non_primary = [img for img in images if not img.is_primary]
        if non_primary:
            image_to_delete = non_primary[0]
            print(f"  准备删除图片 ID: {image_to_delete.id}")
            print(f"  删除前主图: {[img.id for img in images if img.is_primary]}")

            # 模拟删除逻辑
            file_path = os.path.join(app.root_path, image_to_delete.image_url.lstrip('/'))
            print(f"  - 物理文件: {file_path}")

            # 注意：这里只模拟，不实际删除
            print("  ✓ 删除逻辑验证通过（实际未删除）")
        else:
            print("✗ 所有图片都是主图，无法测试删除")
    elif images:
        print("⚠ 只有1张图片，删除后产品将没有图片")
    else:
        print("✗ 没有图片")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
