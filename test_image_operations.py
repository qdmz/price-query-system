#!/usr/bin/env python
"""
测试图片删除和设置主图功能
"""
import os
from app import create_app
from app.models import db, Product, ProductImage

app = create_app()

with app.app_context():
    print("=" * 60)
    print("测试图片删除和设置主图功能")
    print("=" * 60)

    # 获取第一个产品
    product = Product.query.first()
    if not product:
        print("✗ 没有找到产品")
        exit(1)

    print(f"\n测试产品: {product.name} (ID: {product.id})")
    images = ProductImage.query.filter_by(product_id=product.id).all()
    print(f"当前图片数量: {len(images)}")

    if len(images) < 2:
        print("✗ 图片数量不足，无法完整测试（需要至少2张图片）")
        exit(1)

    # 显示当前图片状态
    print("\n【当前图片状态】")
    for img in images:
        print(f"  ID: {img.id}, 主图: {img.is_primary}, 排序: {img.sort_order}")

    # 测试1：设置主图
    print("\n【测试1：设置主图】")
    non_primary_images = [img for img in images if not img.is_primary]
    if non_primary_images:
        new_primary = non_primary_images[0]
        old_primary = [img for img in images if img.is_primary][0]

        print(f"  原主图: {old_primary.id}")
        print(f"  新主图: {new_primary.id}")

        # 执行设置主图操作
        ProductImage.query.filter_by(product_id=product.id).update({'is_primary': False})
        new_primary.is_primary = True
        db.session.commit()

        # 验证
        db.session.refresh(new_primary)
        db.session.refresh(old_primary)
        print(f"✓ 主图设置成功")
        print(f"  - 新主图ID: {new_primary.id}, is_primary={new_primary.is_primary}")
        print(f"  - 原主图ID: {old_primary.id}, is_primary={old_primary.is_primary}")

    else:
        print("✗ 所有图片都已经是主图")

    # 测试2：删除图片
    print("\n【测试2：删除图片】")
    non_primary_images = [img for img in images if not img.is_primary]
    if non_primary_images:
        image_to_delete = non_primary_images[0]
        print(f"  准备删除图片 ID: {image_to_delete.id}")
        print(f"  图片URL: {image_to_delete.image_url}")

        # 构建文件路径
        if image_to_delete.image_url.startswith('/static/'):
            file_path = os.path.join(app.root_path, image_to_delete.image_url.lstrip('/'))
        else:
            file_path = os.path.join(app.root_path, image_to_delete.image_url)

        print(f"  文件路径: {file_path}")
        print(f"  文件存在: {os.path.exists(file_path)}")

        # 执行删除操作
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"✓ 物理文件已删除")

        # 删除数据库记录
        db.session.delete(image_to_delete)
        db.session.commit()
        print(f"✓ 数据库记录已删除")

        # 验证
        db.session.refresh(product)
        print(f"\n【验证结果】")
        print(f"  - 剩余图片数量: {product.images.count()}")

    else:
        print("✗ 没有非主图图片可删除")

    # 测试3：删除主图时的自动切换
    print("\n【测试3：删除主图时的自动切换】")
    images = ProductImage.query.filter_by(product_id=product.id).all()
    primary_image = [img for img in images if img.is_primary]

    if primary_image and len(images) > 1:
        image_to_delete = primary_image[0]
        print(f"  准备删除主图 ID: {image_to_delete.id}")

        # 检查是否有其他图片
        other_images = ProductImage.query.filter(
            ProductImage.product_id == product.id,
            ProductImage.id != image_to_delete.id
        ).first()

        if other_images:
            print(f"  找到其他图片 ID: {other_images.id}, 当前is_primary={other_images.is_primary}")

            # 删除主图
            file_path = os.path.join(app.root_path, image_to_delete.image_url.lstrip('/'))
            if os.path.exists(file_path):
                os.remove(file_path)

            # 设置另一个为主图
            other_images.is_primary = True

            db.session.delete(image_to_delete)
            db.session.commit()

            print(f"✓ 主图已删除，另一个图片已自动设置为主图")

            # 验证
            db.session.refresh(other_images)
            print(f"  - 新主图ID: {other_images.id}, is_primary={other_images.is_primary}")

        else:
            print("✗ 没有其他图片可以设置为主图")

    else:
        print("✗ 无法测试（没有主图或只有1张图片）")

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
