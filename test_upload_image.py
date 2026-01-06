#!/usr/bin/env python
"""
测试图片上传功能
"""
import os
from PIL import Image
from app import create_app
from app.models import db, Product, ProductImage
from app.services.product_service import ProductService
from io import BytesIO

app = create_app()

with app.app_context():
    print("=" * 60)
    print("测试图片上传功能")
    print("=" * 60)

    # 获取第一个产品
    product = Product.query.first()
    if not product:
        print("✗ 没有找到产品")
        exit(1)

    print(f"\n测试产品: {product.name} (ID: {product.id})")
    print(f"当前图片数量: {product.images.count()}")

    # 创建测试图片
    print("\n【创建测试图片】")
    img = Image.new('RGB', (400, 400), color='red')
    img_bytes = BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    # 创建模拟的FileStorage对象
    from werkzeug.datastructures import FileStorage

    class MockFileStorage(FileStorage):
        def __init__(self, stream, filename):
            super().__init__(
                stream=stream,
                filename=filename,
                content_type='image/jpeg'
            )

    mock_file = MockFileStorage(img_bytes, 'test_image.jpg')

    print(f"  - 文件名: test_image.jpg")
    print(f"  - 尺寸: 400x400")
    print(f"  - 格式: JPEG")

    # 测试上传
    print("\n【测试图片上传】")
    try:
        image_url = ProductService.save_product_image(mock_file, product.id)
        print(f"✓ 上传成功: {image_url}")

        # 检查文件是否存在
        file_path = os.path.join(app.root_path, image_url.lstrip('/'))
        exists = os.path.exists(file_path)
        print(f"  - 文件路径: {file_path}")
        print(f"  - 文件存在: {'是' if exists else '否'}")

        # 添加到数据库
        print("\n【添加到数据库】")
        existing_count = product.images.count()
        image = ProductImage(
            product_id=product.id,
            image_url=image_url,
            is_primary=(existing_count == 0),  # 如果是第一张图片，设为主图
            sort_order=existing_count
        )
        db.session.add(image)
        db.session.commit()

        print(f"✓ 数据库添加成功")
        print(f"  - 图片ID: {image.id}")
        print(f"  - 是否主图: {image.is_primary}")
        print(f"  - 排序: {image.sort_order}")

        # 验证
        db.session.refresh(product)
        print(f"\n【验证结果】")
        print(f"  - 当前图片数量: {product.images.count()}")

    except Exception as e:
        print(f"✗ 上传失败: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
