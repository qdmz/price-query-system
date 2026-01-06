#!/usr/bin/env python
"""
测试数据生成脚本
用于生成测试产品、分类、订单等数据
"""

import os
import random
from datetime import datetime, timedelta
from faker import Faker

# 设置环境
os.environ['FLASK_ENV'] = 'production'

from app import create_app
from app.models import db, User, Category, Product, ProductImage, Order, OrderItem

app = create_app('development')

fake = Faker('zh_CN')

# 日用产品数据
PRODUCT_DATA = [
    {'code': 'SP001', 'name': '牙膏-薄荷味', 'category': '洗护用品', 'spec': '120g', 'unit': '支', 'retail': 12.5, 'wholesale': 10.0, 'stock': 500},
    {'code': 'SP002', 'name': '牙膏-草莓味', 'category': '洗护用品', 'spec': '120g', 'unit': '支', 'retail': 12.5, 'wholesale': 10.0, 'stock': 450},
    {'code': 'SP003', 'name': '洗发水-去屑型', 'category': '洗护用品', 'spec': '400ml', 'unit': '瓶', 'retail': 38.0, 'wholesale': 32.0, 'stock': 200},
    {'code': 'SP004', 'name': '沐浴露-茉莉花香', 'category': '洗护用品', 'spec': '750ml', 'unit': '瓶', 'retail': 45.0, 'wholesale': 38.0, 'stock': 180},
    {'code': 'SP005', 'name': '洗衣液-薰衣草', 'category': '清洁用品', 'spec': '2L', 'unit': '瓶', 'retail': 25.0, 'wholesale': 20.0, 'stock': 300},
    {'code': 'SP006', 'name': '洗洁精-柠檬味', 'category': '清洁用品', 'spec': '1.5L', 'unit': '瓶', 'retail': 18.0, 'wholesale': 15.0, 'stock': 400},
    {'code': 'SP007', 'name': '拖把-旋转式', 'category': '清洁用品', 'spec': '标准款', 'unit': '个', 'retail': 35.0, 'wholesale': 28.0, 'stock': 80},
    {'code': 'SP008', 'name': '扫帚套装', 'category': '清洁用品', 'spec': '含簸箕', 'unit': '套', 'retail': 22.0, 'wholesale': 18.0, 'stock': 150},
    {'code': 'SP009', 'name': '毛巾-纯棉', 'category': '家居用品', 'spec': '30x70cm', 'unit': '条', 'retail': 8.5, 'wholesale': 7.0, 'stock': 600},
    {'code': 'SP010', 'name': '毛巾-竹纤维', 'category': '家居用品', 'spec': '30x70cm', 'unit': '条', 'retail': 12.0, 'wholesale': 10.0, 'stock': 400},
    {'code': 'SP011', 'name': '水杯-玻璃款', 'category': '家居用品', 'spec': '400ml', 'unit': '个', 'retail': 15.0, 'wholesale': 12.0, 'stock': 200},
    {'code': 'SP012', 'name': '水杯-保温款', 'category': '家居用品', 'spec': '500ml', 'unit': '个', 'retail': 35.0, 'wholesale': 28.0, 'stock': 120},
    {'code': 'SP013', 'name': '餐具套装-18件', 'category': '厨房用品', 'spec': '陶瓷', 'unit': '套', 'retail': 158.0, 'wholesale': 128.0, 'stock': 50},
    {'code': 'SP014', 'name': '保鲜盒-三件套', 'category': '厨房用品', 'spec': '不同规格', 'unit': '套', 'retail': 25.0, 'wholesale': 20.0, 'stock': 180},
    {'code': 'SP015', 'name': '菜板-竹制', 'category': '厨房用品', 'spec': '40x30cm', 'unit': '个', 'retail': 38.0, 'wholesale': 30.0, 'stock': 90},
    {'code': 'SP016', 'name': '保鲜膜-20米', 'category': '厨房用品', 'spec': '宽30cm', 'unit': '卷', 'retail': 8.0, 'wholesale': 6.5, 'stock': 350},
    {'code': 'SP017', 'name': '纸巾-抽纸-3层', 'category': '纸品', 'spec': '120抽x3包', 'unit': '提', 'retail': 12.0, 'wholesale': 10.0, 'stock': 500},
    {'code': 'SP018', 'name': '纸巾-卷纸-4层', 'category': '纸品', 'spec': '140gx10卷', 'unit': '提', 'retail': 28.0, 'wholesale': 23.0, 'stock': 300},
    {'code': 'SP019', 'name': '湿巾-婴儿专用', 'category': '纸品', 'spec': '80抽', 'unit': '包', 'retail': 15.0, 'wholesale': 12.0, 'stock': 250},
    {'code': 'SP020', 'name': '手帕纸-薄荷味', 'category': '纸品', 'spec': '10包x8片', 'unit': '包', 'retail': 6.0, 'wholesale': 5.0, 'stock': 800},
]

def generate_test_data():
    """生成测试数据"""
    with app.app_context():
        print("=" * 60)
        print("开始生成测试数据...")
        print("=" * 60)
        
        # 清空现有数据（可选）
        # OrderItem.query.delete()
        # Order.query.delete()
        # ProductImage.query.delete()
        # Product.query.delete()
        # Category.query.delete()
        
        # 创建分类
        print("\n[1/5] 创建分类...")
        categories = {}
        category_names = list(set(item['category'] for item in PRODUCT_DATA))
        
        for i, name in enumerate(category_names, 1):
            existing = Category.query.filter_by(name=name).first()
            if existing:
                categories[name] = existing
                print(f"  - 分类已存在: {name}")
            else:
                category = Category(
                    name=name,
                    description=f'{name}分类商品',
                    sort_order=i
                )
                db.session.add(category)
                db.session.commit()
                categories[name] = category
                print(f"  ✓ 创建分类: {name}")
        
        # 创建产品
        print("\n[2/5] 创建产品...")
        for item in PRODUCT_DATA:
            existing = Product.query.filter_by(product_code=item['code']).first()
            if existing:
                print(f"  - 产品已存在: {item['name']} ({item['code']})")
                continue
            
            category = categories.get(item['category'])
            product = Product(
                product_code=item['code'],
                barcode=fake.ean13(),
                name=item['name'],
                model=fake.numerify('Model-####'),
                specification=item['spec'],
                unit=item['unit'],
                retail_price=item['retail'],
                wholesale_price=item['wholesale'],
                wholesale_min_qty=random.choice([1, 2, 3, 5, 10]),
                stock=item['stock'],
                description=fake.text(max_nb_chars=200),
                status='active',
                category_id=category.id if category else None
            )
            db.session.add(product)
            db.session.commit()
            
            # 创建产品图片（占位符）
            image = ProductImage(
                product_id=product.id,
                image_url='/static/images/product-placeholder.jpg',
                is_primary=True,
                sort_order=1
            )
            db.session.add(image)
            db.session.commit()
            
            print(f"  ✓ 创建产品: {item['name']} ({item['code']})")
        
        print("\n[3/5] 创建订单...")
        products = Product.query.filter_by(status='active').all()
        statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        
        for i in range(1, 21):  # 创建20个订单
            order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{i:03d}"
            status = random.choice(statuses)
            
            # 根据状态调整日期
            if status == 'completed':
                created_at = datetime.now() - timedelta(days=random.randint(1, 30))
            elif status == 'cancelled':
                created_at = datetime.now() - timedelta(days=random.randint(1, 20))
            elif status == 'confirmed':
                created_at = datetime.now() - timedelta(hours=random.randint(1, 48))
            else:
                created_at = datetime.now() - timedelta(minutes=random.randint(1, 120))
            
            order = Order(
                order_no=order_no,
                customer_name=fake.name(),
                customer_phone=fake.phone_number(),
                customer_email=fake.email(),
                customer_address=fake.address(),
                status=status,
                notes=fake.sentence() if random.random() > 0.7 else '',
                notified=random.choice([True, False]),
                created_at=created_at,
                updated_at=created_at
            )
            db.session.add(order)
            db.session.commit()
            
            # 添加订单项
            num_items = random.randint(1, 5)
            selected_products = random.sample(products, min(num_items, len(products)))
            
            total_amount = 0
            total_quantity = 0
            
            for product in selected_products:
                quantity = random.randint(1, 10)
                unit_price = product.wholesale_price if quantity >= product.wholesale_min_qty else product.retail_price
                subtotal = quantity * unit_price
                
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    product_name=product.name,
                    product_code=product.product_code,
                    quantity=quantity,
                    unit_price=unit_price,
                    subtotal=subtotal
                )
                db.session.add(order_item)
                
                total_amount += subtotal
                total_quantity += quantity
            
            # 更新订单总额
            order.total_amount = total_amount
            order.total_quantity = total_quantity
            db.session.commit()
            
            print(f"  ✓ 创建订单: {order_no} ({status}) - ¥{total_amount:.2f}")
        
        print("\n[4/5] 更新统计数据...")
        # 统计数据由 API 动态计算，无需额外操作
        
        print("\n[5/5] 完成数据生成")
        print("=" * 60)
        print("✓ 测试数据生成完成！")
        print(f"  - 分类数量: {len(categories)}")
        print(f"  - 产品数量: {Product.query.count()}")
        print(f"  - 订单数量: {Order.query.count()}")
        print(f"  - 订单项数量: {OrderItem.query.count()}")
        print("=" * 60)
        print("\n访问以下地址查看数据：")
        print("  - 前台首页: http://localhost:5000/")
        print("  - 后台管理: http://localhost:5000/admin/products")
        print("  - 订单管理: http://localhost:5000/admin/orders")
        print("  - 系统设置: http://localhost:5000/system/settings")
        print("  - 登录: admin / admin123")
        print("=" * 60)

if __name__ == '__main__':
    try:
        generate_test_data()
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
