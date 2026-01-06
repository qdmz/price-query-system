#!/usr/bin/env python
"""
测试产品表单提交
"""
import requests
from app import create_app
from app.models import db, Product

app = create_app()

with app.app_context():
    print("=" * 60)
    print("测试产品表单提交")
    print("=" * 60)

    # 获取第一个产品
    product = Product.query.first()
    if not product:
        print("✗ 没有找到产品")
        exit(1)

    print(f"\n测试产品: {product.name} (ID: {product.id})")
    print(f"当前货号: {product.product_code}")
    print(f"当前价格: 零售¥{product.retail_price}, 批发¥{product.wholesale_price}")

    # 测试表单数据
    form_data = {
        'product_code': f'TEST{product.id}',
        'barcode': product.barcode or '',
        'name': product.name,
        'model': product.model or '',
        'specification': product.specification or '',
        'unit': product.unit or '件',
        'retail_price': '99.99',
        'wholesale_price': '88.88',
        'wholesale_min_qty': str(product.wholesale_min_qty),
        'stock': str(product.stock),
        'description': product.description or '',
        'category_id': str(product.category_id) if product.category_id else '',
    }

    print("\n准备提交表单数据:")
    print(f"  货号: {form_data['product_code']}")
    print(f"  零售价: {form_data['retail_price']}")
    print(f"  批发价: {form_data['wholesale_price']}")

    try:
        # 使用测试客户端
        with app.test_client() as client:
            # 模拟登录（需要先登录才能访问）
            with client.session_transaction() as sess:
                from app.models import User
                admin = User.query.filter_by(username='admin').first()
                if admin:
                    sess['_user_id'] = str(admin.id)
                else:
                    print("✗ 管理员账户不存在")
                    exit(1)

            # 提交表单
            print("\n正在提交表单...")
            response = client.post(
                f'/admin/products/{product.id}/edit',
                data=form_data,
                follow_redirects=True
            )

            print(f"响应状态码: {response.status_code}")

            if response.status_code == 200:
                # 刷新产品数据
                db.session.refresh(product)

                print(f"\n✓ 表单提交成功")
                print(f"  更新后货号: {product.product_code}")
                print(f"  更新后价格: 零售¥{product.retail_price}, 批发¥{product.wholesale_price}")

                # 验证数据是否更新
                if product.product_code == form_data['product_code']:
                    print(f"✓ 货号更新正确")
                else:
                    print(f"✗ 货号未更新")

                if float(product.retail_price) == float(form_data['retail_price']):
                    print(f"✓ 零售价更新正确")
                else:
                    print(f"✗ 零售价未更新")

                if float(product.wholesale_price) == float(form_data['wholesale_price']):
                    print(f"✓ 批发价更新正确")
                else:
                    print(f"✗ 批发价未更新")
            else:
                print(f"\n✗ 表单提交失败")
                print(f"响应内容: {response.data.decode('utf-8')[:500]}")

    except Exception as e:
        print(f"\n✗ 测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)
