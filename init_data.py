#!/usr/bin/env python
"""
数据初始化脚本
在系统首次部署或重置时执行，用于初始化基础数据
包括：默认管理员、系统设置、产品图片、测试订单数据
"""
import sys
import os
import random
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db, User, SystemSetting, Product, ProductImage, Order, OrderItem, Category
from app.services.product_service import ProductService
from app.services.order_service import OrderService

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

# 随机客户姓名库
CUSTOMER_NAMES = [
    "张伟", "李娜", "王芳", "刘洋", "陈静", "杨明", "赵军", "孙丽",
    "周强", "吴敏", "郑伟", "王强", "李军", "张敏", "刘芳", "陈伟",
    "杨丽", "赵敏", "孙强", "周丽", "吴伟", "郑敏", "王军", "李强",
    "张军", "刘敏", "陈丽", "杨强", "赵丽", "孙伟", "周敏", "吴军",
    "郑强", "王丽", "李敏", "张强", "刘军", "陈敏", "杨丽", "赵强",
    "孙敏", "周军", "吴丽", "郑敏", "王强", "李丽", "张敏", "刘强",
    "陈军", "杨敏", "赵丽", "孙军", "周强", "吴敏", "郑军", "王敏"
]


def match_product_images(product_name):
    """根据产品名称匹配图片"""
    for keyword, urls in PRODUCT_IMAGES.items():
        if keyword in product_name:
            return urls
    return None


def generate_phone():
    """生成随机电话号码"""
    return f"1{random.choice(['3', '5', '7', '8', '9'])}{random.randint(100000000, 999999999)}"


def create_default_admin(app):
    """创建默认管理员账户"""
    with app.app_context():
        admin = User.query.filter_by(username=app.config['ADMIN_USERNAME']).first()
        
        if not admin:
            admin = User(
                username=app.config['ADMIN_USERNAME'],
                email=app.config['ADMIN_EMAIL'],
                role='admin'
            )
            admin.set_password(app.config['ADMIN_PASSWORD'])
            db.session.add(admin)
            db.session.commit()
            print(f"✓ 默认管理员账户已创建 - 用户名: {admin.username}")
        else:
            print("✓ 管理员账户已存在")


def create_default_settings(app):
    """创建默认系统设置"""
    with app.app_context():
        default_settings = {
            'email_enabled': 'false',
            'sms_enabled': 'false',
            'notification_emails': '',
            'admin_phones': '',
            'company_name': '日用产品批发零售系统',
            'company_phone': '',
            'company_address': '',
        }
        
        for key, value in default_settings.items():
            setting = SystemSetting.query.filter_by(key=key).first()
            if not setting:
                setting = SystemSetting(key=key, value=value)
                db.session.add(setting)
        
        db.session.commit()
        print("✓ 默认系统设置已创建")


# 默认产品数据
DEFAULT_PRODUCTS = [
    {'code': 'P001', 'name': '牙膏 清爽薄荷味', 'category': '个护用品', 'retail': 12.8, 'wholesale': 10.0, 'stock': 500, 'unit': '支', 'model': 'TB-001', 'specification': '120g', 'description': '清爽薄荷味牙膏，有效清新口气，保护牙龈健康'},
    {'code': 'P002', 'name': '洗发水 去屑型', 'category': '个护用品', 'retail': 38.5, 'wholesale': 32.0, 'stock': 300, 'unit': '瓶', 'model': 'XP-002', 'specification': '500ml', 'description': '去屑型洗发水，温和配方，有效去屑止痒'},
    {'code': 'P003', 'name': '沐浴露 薰衣草香', 'category': '个护用品', 'retail': 45.0, 'wholesale': 38.0, 'stock': 280, 'unit': '瓶', 'model': 'MY-003', 'specification': '750ml', 'description': '薰衣草香沐浴露，滋润保湿，舒缓放松'},
    {'code': 'P004', 'name': '洗衣液 深层洁净', 'category': '清洁用品', 'retail': 29.9, 'wholesale': 25.0, 'stock': 600, 'unit': '瓶', 'model': 'XY-004', 'specification': '1kg', 'description': '深层洁净洗衣液，强力去污，护衣护色'},
    {'code': 'P005', 'name': '洗洁精 柠檬味', 'category': '清洁用品', 'retail': 15.8, 'wholesale': 13.0, 'stock': 800, 'unit': '瓶', 'model': 'XJ-005', 'specification': '500ml', 'description': '柠檬味洗洁精，天然去油，不伤手'},
    {'code': 'P006', 'name': '拖把 旋转拖地神器', 'category': '清洁工具', 'retail': 89.0, 'wholesale': 75.0, 'stock': 120, 'unit': '个', 'model': 'TB-006', 'specification': '标准版', 'description': '旋转拖地神器，拖地更轻松，无需弯腰'},
    {'code': 'P007', 'name': '扫帚套装 扫把簸箕', 'category': '清洁工具', 'retail': 35.0, 'wholesale': 28.0, 'stock': 200, 'unit': '套', 'model': 'SB-007', 'specification': '组合装', 'description': '扫帚套装，包含扫把和簸箕，清洁必备'},
    {'code': 'P008', 'name': '毛巾 纯棉吸水', 'category': '家居用品', 'retail': 18.0, 'wholesale': 15.0, 'stock': 500, 'unit': '条', 'model': 'MJ-008', 'specification': '35x75cm', 'description': '纯棉吸水毛巾，柔软亲肤，吸水性强'},
    {'code': 'P009', 'name': '水杯 不锈钢保温', 'category': '家居用品', 'retail': 68.0, 'wholesale': 55.0, 'stock': 250, 'unit': '个', 'model': 'SB-009', 'specification': '500ml', 'description': '不锈钢保温水杯，长效保温，安全健康'},
    {'code': 'P010', 'name': '菜板 竹制防霉', 'category': '厨房用品', 'retail': 42.0, 'wholesale': 35.0, 'stock': 180, 'unit': '块', 'model': 'CB-010', 'specification': '40x30cm', 'description': '竹制防霉菜板，天然材质，健康环保'},
    {'code': 'P011', 'name': '餐具套装 不锈钢', 'category': '厨房用品', 'retail': 128.0, 'wholesale': 105.0, 'stock': 80, 'unit': '套', 'model': 'CJ-011', 'specification': '4人装', 'description': '不锈钢餐具套装，包含勺子、叉子、筷子，耐用易清洗'},
    {'code': 'P012', 'name': '湿巾 婴儿专用', 'category': '母婴用品', 'retail': 25.0, 'wholesale': 20.0, 'stock': 400, 'unit': '包', 'model': 'WS-012', 'specification': '80片', 'description': '婴儿专用湿巾，无酒精无刺激，温和清洁'},
    {'code': 'P013', 'name': '牙膏 洁白亮齿', 'category': '个护用品', 'retail': 14.5, 'wholesale': 12.0, 'stock': 450, 'unit': '支', 'model': 'TB-013', 'specification': '120g', 'description': '洁白亮齿牙膏，有效去除牙渍，让牙齿更洁白'},
    {'code': 'P014', 'name': '洗发水 滋润养护', 'category': '个护用品', 'retail': 42.0, 'wholesale': 35.0, 'stock': 320, 'unit': '瓶', 'model': 'XP-014', 'specification': '500ml', 'description': '滋润养护洗发水，修复受损发质，柔顺亮泽'},
    {'code': 'P015', 'name': '洗衣液 香氛柔顺', 'category': '清洁用品', 'retail': 32.9, 'wholesale': 28.0, 'stock': 550, 'unit': '瓶', 'model': 'XY-015', 'specification': '1kg', 'description': '香氛柔顺洗衣液，留香持久，衣物柔顺'},
]


def create_default_products(app):
    """创建默认产品数据和分类"""
    with app.app_context():
        print("\n" + "=" * 60)
        print("开始创建默认产品数据...")
        print("=" * 60)
        
        # 获取所有分类名称
        category_names = list(set(p['category'] for p in DEFAULT_PRODUCTS))
        
        # 创建分类
        for category_name in category_names:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name, description=category_name)
                db.session.add(category)
                print(f"  创建分类: {category_name}")
        
        db.session.commit()
        
        # 创建产品
        created_count = 0
        skipped_count = 0
        
        for product_data in DEFAULT_PRODUCTS:
            # 检查产品是否已存在
            existing_product = Product.query.filter_by(product_code=product_data['code']).first()
            if existing_product:
                skipped_count += 1
                continue
            
            # 获取分类
            category = Category.query.filter_by(name=product_data['category']).first()
            
            # 生成条码
            barcode = f"690{product_data['code'][1:]:0>10}"
            
            # 创建产品
            product = Product(
                product_code=product_data['code'],
                barcode=barcode,
                name=product_data['name'],
                model=product_data['model'],
                specification=product_data['specification'],
                unit=product_data['unit'],
                retail_price=product_data['retail'],
                wholesale_price=product_data['wholesale'],
                wholesale_min_qty=3,
                stock=product_data['stock'],
                description=product_data['description'],
                category_id=category.id if category else None,
                status='active'
            )
            
            db.session.add(product)
            created_count += 1
            print(f"  创建产品: {product_data['code']} - {product_data['name']}")
        
        db.session.commit()
        
        print(f"✓ 产品数据创建完成 - 新增: {created_count}, 跳过: {skipped_count}")


def add_product_images(app):
    """为产品添加网络图片"""
    with app.app_context():
        # 获取所有产品
        products = Product.query.all()
        
        print("\n" + "=" * 60)
        print("开始为产品添加网络图片...")
        print("=" * 60)
        
        success_count = 0
        failed_count = 0
        skip_count = 0
        
        for product in products:
            # 检查是否已有图片
            if product.images.count() >= 3:
                skip_count += 1
                continue
            
            # 匹配图片
            image_urls = match_product_images(product.name)
            
            if not image_urls:
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
                        
                except Exception as e:
                    pass
            
            if added > 0:
                db.session.commit()
                success_count += 1
            else:
                db.session.rollback()
                failed_count += 1
        
        print(f"✓ 产品图片添加完成 - 成功: {success_count}, 失败: {failed_count}, 跳过: {skip_count}")


def generate_orders_for_month(app, year, month, num_orders):
    """为指定月份生成订单"""
    with app.app_context():
        # 获取该月的产品
        products = Product.query.filter_by(status='active').all()
        
        if not products:
            return 0
        
        # 该月的开始和结束日期
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # 生成该月的订单
        created_count = 0
        for i in range(num_orders):
            try:
                # 随机生成订单时间（在该月内均匀分布）
                total_days = (end_date - start_date).days
                random_days = random.randint(0, total_days)
                random_hours = random.randint(0, 23)
                random_minutes = random.randint(0, 59)
                
                order_date = start_date + timedelta(
                    days=random_days,
                    hours=random_hours,
                    minutes=random_minutes
                )
                
                # 随机选择客户
                customer_name = random.choice(CUSTOMER_NAMES)
                customer_phone = generate_phone()
                customer_email = f"{customer_name}@example.com"
                customer_address = f"北京市朝阳区{random.randint(1, 999)}号院"
                
                # 随机选择2-5个产品
                num_products = random.randint(2, 5)
                selected_products = random.sample(products, min(num_products, len(products)))
                
                # 计算订单总金额和总数量
                total_amount = 0
                total_quantity = 0
                order_items = []
                
                for product in selected_products:
                    quantity = random.randint(1, 10)
                    
                    # 判断使用零售价还是批发价
                    if quantity >= product.wholesale_min_qty:
                        price = product.wholesale_price
                    else:
                        price = product.retail_price
                    
                    subtotal = price * quantity
                    total_amount += subtotal
                    total_quantity += quantity
                    
                    order_items.append({
                        'product': product,
                        'quantity': quantity,
                        'price': price,
                        'subtotal': subtotal
                    })
                
                # 生成订单号
                order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
                
                # 随机设置订单状态（70%完成，20%已确认，10%已取消）
                status_rand = random.random()
                if status_rand < 0.7:
                    status = 'completed'
                elif status_rand < 0.9:
                    status = 'confirmed'
                else:
                    status = 'cancelled'
                
                # 创建订单
                order = Order(
                    order_no=order_no,
                    customer_name=customer_name,
                    customer_phone=customer_phone,
                    customer_email=customer_email,
                    customer_address=customer_address,
                    total_amount=total_amount,
                    total_quantity=total_quantity,
                    status=status,
                    notes=f'自动生成的测试订单 - {year}年{month}月',
                    created_at=order_date,
                    updated_at=order_date
                )
                
                db.session.add(order)
                db.session.flush()  # 获取订单ID
                
                # 创建订单项
                for item_data in order_items:
                    order_item = OrderItem(
                        order_id=order.id,
                        product_id=item_data['product'].id,
                        product_name=item_data['product'].name,
                        product_code=item_data['product'].product_code,
                        quantity=item_data['quantity'],
                        unit_price=item_data['price'],
                        subtotal=item_data['subtotal']
                    )
                    db.session.add(order_item)
                
                db.session.commit()
                created_count += 1
                
            except Exception as e:
                db.session.rollback()
                print(f"  订单创建失败: {e}")
        
        return created_count


def generate_test_orders(app):
    """生成多个月的订单数据"""
    with app.app_context():
        print("\n" + "=" * 60)
        print("开始生成多个月份的订单数据...")
        print("=" * 60)
        
        # 检查是否已有订单数据
        existing_orders = Order.query.count()
        if existing_orders > 0:
            print(f"✓ 已有 {existing_orders} 个订单，跳过生成")
            return
        
        # 获取当前时间
        now = datetime.now()
        
        # 定义要生成的月份和订单数量
        month_configs = []
        
        for i in range(6):
            # 计算年月
            if now.month - i <= 0:
                year = now.year - 1
                month = now.month - i + 12
            else:
                year = now.year
                month = now.month - i
            
            # 订单数量：越近的月份订单越多
            base_orders = 5 + i * 5
            num_orders = random.randint(base_orders, base_orders + 5)
            
            month_configs.append({
                'year': year,
                'month': month,
                'num_orders': num_orders
            })
        
        # 按时间顺序生成（从最早的月份开始）
        month_configs.reverse()
        
        total_orders = 0
        
        for config in month_configs:
            year = config['year']
            month = config['month']
            num_orders = config['num_orders']
            
            created = generate_orders_for_month(app, year, month, num_orders)
            total_orders += created
        
        print(f"✓ 订单数据生成完成 - 共生成 {total_orders} 个订单")


def init_all_data():
    """初始化所有数据"""
    app = create_app()
    
    print("=" * 60)
    print("开始初始化系统数据...")
    print("=" * 60)
    
    try:
        # 1. 创建默认管理员
        create_default_admin(app)
        
        # 2. 创建默认系统设置
        create_default_settings(app)
        
        # 3. 创建默认产品数据（新增）
        create_default_products(app)
        
        # 4. 为产品添加网络图片
        add_product_images(app)
        
        # 5. 生成测试订单数据
        generate_test_orders(app)
        
        print("\n" + "=" * 60)
        print("✓ 所有数据初始化完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 数据初始化失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    init_all_data()
