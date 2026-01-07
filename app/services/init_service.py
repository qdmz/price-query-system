from app.models import db, User, SystemSetting, Category, Product, ProductImage, Order, OrderItem
from flask import current_app

def create_default_admin():
    """创建默认管理员账户"""
    admin = User.query.filter_by(username=current_app.config['ADMIN_USERNAME']).first()

    if not admin:
        admin = User(
            username=current_app.config['ADMIN_USERNAME'],
            email=current_app.config['ADMIN_EMAIL'],
            role='admin'
        )
        admin.set_password(current_app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
        print(f"默认管理员账户已创建 - 用户名: {admin.username}, 密码: {current_app.config['ADMIN_PASSWORD']}")
    else:
        print("管理员账户已存在")

def create_default_settings():
    """创建默认系统设置"""
    default_settings = {
        'email_enabled': 'false',
        'sms_enabled': 'false',
        'notification_emails': '',
        'admin_phones': '',
        'site_name': '日用产品批发零售系统',
        'site_title': '日用产品批发零售系统',
        'company_name': '日用产品批发零售系统',
        'company_phone': '400-888-8888',
        'company_email': 'service@example.com',
        'company_address': '北京市朝阳区XXX街道XXX号',
        'copyright': '© 2024 日用产品批发零售系统. All rights reserved.',
        'icp': '京ICP备XXXXXXXX号',
    }

    for key, value in default_settings.items():
        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            setting = SystemSetting(key=key, value=value)
            db.session.add(setting)

    db.session.commit()

def create_sample_categories():
    """创建示例分类"""
    categories_data = [
        {'name': '个人护理', 'description': '牙膏、洗发水、沐浴露等个人护理用品'},
        {'name': '清洁用品', 'description': '洗衣液、洗洁精、清洁剂等清洁用品'},
        {'name': '纸品湿巾', 'description': '卫生纸、抽纸、湿巾等纸品'},
        {'name': '厨房用品', 'description': '保鲜膜、垃圾袋等厨房用品'},
        {'name': '家居纺织', 'description': '毛巾、浴巾、床上用品等'},
    ]

    for cat_data in categories_data:
        category = Category.query.filter_by(name=cat_data['name']).first()
        if not category:
            category = Category(
                name=cat_data['name'],
                description=cat_data['description']
            )
            db.session.add(category)

    db.session.commit()
    print("示例分类已创建")

def create_sample_products():
    """创建示例产品"""
    if Product.query.count() > 0:
        print("产品数据已存在，跳过创建")
        return

    # 获取分类
    category_map = {cat.name: cat for cat in Category.query.all()}

    products_data = [
        {
            'product_code': 'SP001',
            'barcode': '6901234567890',
            'name': '牙膏-薄荷味',
            'model': 'Model-1001',
            'specification': '120g',
            'unit': '支',
            'retail_price': 12.5,
            'wholesale_price': 10.0,
            'wholesale_min_qty': 2,
            'stock': 500,
            'description': '清新薄荷味牙膏，有效清洁口腔，含氟配方，预防蛀牙',
            'category': '个人护理',
            'images': [
                'https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP002',
            'barcode': '6901234567891',
            'name': '洗发水-去屑型',
            'model': 'Model-2001',
            'specification': '400ml',
            'unit': '瓶',
            'retail_price': 38.0,
            'wholesale_price': 32.0,
            'wholesale_min_qty': 3,
            'stock': 200,
            'description': '去屑洗发水，适用于所有发质，温和不刺激，持久清香',
            'category': '个人护理',
            'images': [
                'https://images.unsplash.com/photo-1598440947619-2c35fc9aa908?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1631729371254-42c2a89e0e18?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP003',
            'barcode': '6901234567892',
            'name': '洗衣液-薰衣草',
            'model': 'Model-3001',
            'specification': '2L',
            'unit': '瓶',
            'retail_price': 25.0,
            'wholesale_price': 20.0,
            'wholesale_min_qty': 5,
            'stock': 300,
            'description': '薰衣草香洗衣液，温和不伤手，强力去污，护衣护色',
            'category': '清洁用品',
            'images': [
                'https://images.unsplash.com/photo-1584634784672-2d65a3d761be?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP004',
            'barcode': '6901234567893',
            'name': '毛巾-纯棉',
            'model': 'Model-4001',
            'specification': '30x70cm',
            'unit': '条',
            'retail_price': 8.5,
            'wholesale_price': 7.0,
            'wholesale_min_qty': 10,
            'stock': 600,
            'description': '纯棉毛巾，柔软舒适，吸水性强，适用于日常洗脸擦手',
            'category': '家居纺织',
            'images': [
                'https://images.unsplash.com/photo-1584030373081-379e4b9c3771?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1564419320461-6870880221ad?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP005',
            'barcode': '6901234567894',
            'name': '纸巾-抽纸-3层',
            'model': 'Model-5001',
            'specification': '120抽x3包',
            'unit': '提',
            'retail_price': 12.0,
            'wholesale_price': 10.0,
            'wholesale_min_qty': 2,
            'stock': 500,
            'description': '3层加厚抽纸，纸质柔软，湿水不易破，环保无漂白',
            'category': '纸品湿巾',
            'images': [
                'https://images.unsplash.com/photo-1629198688000-71f23e745b6e?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP006',
            'barcode': '6901234567895',
            'name': '沐浴露-海洋香',
            'model': 'Model-6001',
            'specification': '750ml',
            'unit': '瓶',
            'retail_price': 45.0,
            'wholesale_price': 38.0,
            'wholesale_min_qty': 3,
            'stock': 150,
            'description': '海洋香型沐浴露，清爽洁净，保湿滋润，留香持久',
            'category': '个人护理',
            'images': [
                'https://images.unsplash.com/photo-1611930022073-b7a4ba5fcccd?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1616683693504-3ea7e9ad6fec?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP007',
            'barcode': '6901234567896',
            'name': '洗洁精-柠檬',
            'model': 'Model-7001',
            'specification': '1.5kg',
            'unit': '瓶',
            'retail_price': 18.0,
            'wholesale_price': 15.0,
            'wholesale_min_qty': 5,
            'stock': 400,
            'description': '柠檬味洗洁精，去油污效果好，易冲洗，不伤手',
            'category': '清洁用品',
            'images': [
                'https://images.unsplash.com/photo-1615184697985-c9bde1b07da7?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP008',
            'barcode': '6901234567897',
            'name': '卫生纸-卷纸',
            'model': 'Model-8001',
            'specification': '140gx10卷',
            'unit': '提',
            'retail_price': 28.0,
            'wholesale_price': 24.0,
            'wholesale_min_qty': 3,
            'stock': 350,
            'description': '原生木浆卷纸，韧性好，柔韧不掉屑，四层加厚',
            'category': '纸品湿巾',
            'images': [
                'https://images.unsplash.com/photo-1628147156366-5b0e9be9c98e?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1584214102020-745498818c97?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP009',
            'barcode': '6901234567898',
            'name': '垃圾袋-大号',
            'model': 'Model-9001',
            'specification': '50x60cm',
            'unit': '卷',
            'retail_price': 15.0,
            'wholesale_price': 12.0,
            'wholesale_min_qty': 10,
            'stock': 500,
            'description': '加厚垃圾袋，不易破损，环保材质，适合家庭厨房使用',
            'category': '厨房用品',
            'images': [
                'https://images.unsplash.com/photo-1595429035839-c99c298ffdde?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP010',
            'barcode': '6901234567899',
            'name': '护手霜-滋润型',
            'model': 'Model-10001',
            'specification': '50g',
            'unit': '支',
            'retail_price': 22.0,
            'wholesale_price': 18.0,
            'wholesale_min_qty': 5,
            'stock': 250,
            'description': '滋润型护手霜，保护双手，清爽不油腻，长效保湿',
            'category': '个人护理',
            'images': [
                'https://images.unsplash.com/photo-1601049541289-9b1b7bbbfe19?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1571781926291-c477ebfd024b?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP011',
            'barcode': '6901234567900',
            'name': '面巾纸-小包',
            'model': 'Model-11001',
            'specification': '10包x8片',
            'unit': '盒',
            'retail_price': 15.0,
            'wholesale_price': 12.5,
            'wholesale_min_qty': 5,
            'stock': 400,
            'description': '便携小包面巾纸，随身携带，柔软亲肤，不掉屑',
            'category': '纸品湿巾',
            'images': [
                'https://images.unsplash.com/photo-1616401784845-180882ba9ba8?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP012',
            'barcode': '6901234567901',
            'name': '湿巾-婴儿专用',
            'model': 'Model-12001',
            'specification': '80抽x3包',
            'unit': '提',
            'retail_price': 35.0,
            'wholesale_price': 30.0,
            'wholesale_min_qty': 3,
            'stock': 200,
            'description': '婴儿专用湿巾，无酒精无香精，温和呵护宝宝肌肤',
            'category': '纸品湿巾',
            'images': [
                'https://images.unsplash.com/photo-1556228578-0d85b1a4d571?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1626803775151-61d756612f97?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP013',
            'barcode': '6901234567902',
            'name': '洗衣粉-强效去污',
            'model': 'Model-13001',
            'specification': '2kg',
            'unit': '袋',
            'retail_price': 22.0,
            'wholesale_price': 18.0,
            'wholesale_min_qty': 5,
            'stock': 300,
            'description': '强效去污洗衣粉，去渍力强，性价比高，适合大量洗涤',
            'category': '清洁用品',
            'images': [
                'https://images.unsplash.com/photo-1608248597279-f99d160bfcbc?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP014',
            'barcode': '6901234567903',
            'name': '浴巾-超柔',
            'model': 'Model-14001',
            'specification': '70x140cm',
            'unit': '条',
            'retail_price': 28.0,
            'wholesale_price': 24.0,
            'wholesale_min_qty': 5,
            'stock': 200,
            'description': '超柔浴巾，大尺寸厚实，吸水性强，洗浴后舒适包裹',
            'category': '家居纺织',
            'images': [
                'https://images.unsplash.com/photo-1564419320461-6870880221ad?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1584030373081-379e4b9c3771?w=400&h=400&fit=crop'
            ]
        },
        {
            'product_code': 'SP015',
            'barcode': '6901234567904',
            'name': '洗手液-芦荟',
            'model': 'Model-15001',
            'specification': '500ml',
            'unit': '瓶',
            'retail_price': 18.0,
            'wholesale_price': 15.0,
            'wholesale_min_qty': 5,
            'stock': 350,
            'description': '芦荟洗手液，温和滋润，抑菌消毒，适合家庭日常使用',
            'category': '个人护理',
            'images': [
                'https://images.unsplash.com/photo-1599571234909-29ed5d1321d6?w=400&h=400&fit=crop',
                'https://images.unsplash.com/photo-1582967788606-a171f1080ca8?w=400&h=400&fit=crop'
            ]
        },
    ]

    for i, prod_data in enumerate(products_data):
        product = Product(
            product_code=prod_data['product_code'],
            barcode=prod_data['barcode'],
            name=prod_data['name'],
            model=prod_data['model'],
            specification=prod_data['specification'],
            unit=prod_data['unit'],
            retail_price=prod_data['retail_price'],
            wholesale_price=prod_data['wholesale_price'],
            wholesale_min_qty=prod_data['wholesale_min_qty'],
            stock=prod_data['stock'],
            description=prod_data['description'],
            category_id=category_map.get(prod_data['category']).id if prod_data['category'] in category_map else None
        )
        db.session.add(product)
        db.session.flush()  # 获取product的ID

        # 为每个产品添加图片
        images = prod_data.get('images', [])
        for j, image_url in enumerate(images):
            image = ProductImage(
                product_id=product.id,
                image_url=image_url,
                is_primary=(j == 0),
                sort_order=j
            )
            db.session.add(image)

    db.session.commit()
    print(f"示例产品已创建，共 {len(products_data)} 条")

def create_sample_orders():
    """创建示例订单"""
    if Order.query.count() > 0:
        print("订单数据已存在，跳过创建")
        return

    # 获取管理员用户
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        print("未找到管理员用户，无法创建订单")
        return

    # 获取一些产品
    products = Product.query.limit(5).all()
    if not products:
        print("未找到产品，无法创建订单")
        return

    from datetime import datetime, timedelta

    orders_data = [
        {
            'customer_name': '张三',
            'customer_phone': '13800138001',
            'customer_email': 'zhangsan@example.com',
            'customer_address': '北京市朝阳区建国路88号',
            'status': 'completed',
            'items': [
                {'product': products[0], 'quantity': 2},
                {'product': products[1], 'quantity': 1},
                {'product': products[4], 'quantity': 3},
            ],
            'notes': '请加急发货',
            'created_at': datetime.utcnow() - timedelta(days=5)
        },
        {
            'customer_name': '李四',
            'customer_phone': '13900139002',
            'customer_email': 'lisi@example.com',
            'customer_address': '上海市浦东新区陆家嘴环路1000号',
            'status': 'shipped',
            'items': [
                {'product': products[2], 'quantity': 5},
                {'product': products[3], 'quantity': 10},
            ],
            'notes': '',
            'created_at': datetime.utcnow() - timedelta(days=3)
        },
        {
            'customer_name': '王五',
            'customer_phone': '13700137003',
            'customer_email': 'wangwu@example.com',
            'customer_address': '广州市天河区珠江新城华夏路16号',
            'status': 'confirmed',
            'items': [
                {'product': products[0], 'quantity': 3},
                {'product': products[2], 'quantity': 2},
            ],
            'notes': '周末收货',
            'created_at': datetime.utcnow() - timedelta(days=1)
        },
        {
            'customer_name': '赵六',
            'customer_phone': '13600136004',
            'customer_email': 'zhaoliu@example.com',
            'customer_address': '深圳市南山区科技园南区粤海街道',
            'status': 'pending',
            'items': [
                {'product': products[1], 'quantity': 1},
                {'product': products[3], 'quantity': 5},
                {'product': products[4], 'quantity': 2},
            ],
            'notes': '请先联系确认',
            'created_at': datetime.utcnow()
        },
    ]

    for order_data in orders_data:
        # 生成订单号
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{Order.query.count() + 1:03d}"

        # 计算总金额和总数量
        total_amount = 0
        total_quantity = 0

        # 创建订单
        order = Order(
            order_no=order_no,
            customer_name=order_data['customer_name'],
            customer_phone=order_data['customer_phone'],
            customer_email=order_data['customer_email'],
            customer_address=order_data['customer_address'],
            status=order_data['status'],
            notes=order_data['notes'],
            user_id=admin.id,
            created_at=order_data['created_at'],
            updated_at=order_data['created_at']
        )
        db.session.add(order)
        db.session.flush()  # 获取order的ID

        # 创建订单项
        for item_data in order_data['items']:
            product = item_data['product']
            quantity = item_data['quantity']

            # 根据数量选择价格（批发或零售）
            if quantity >= product.wholesale_min_qty:
                unit_price = product.wholesale_price
            else:
                unit_price = product.retail_price

            subtotal = unit_price * quantity

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

        # 更新订单总金额和总数量
        order.total_amount = total_amount
        order.total_quantity = total_quantity

    db.session.commit()
    print(f"示例订单已创建，共 {len(orders_data)} 条")

def init_sample_data():
    """初始化所有示例数据"""
    print("=" * 60)
    print("开始初始化示例数据...")
    print("=" * 60)

    create_default_admin()
    create_default_settings()
    create_sample_categories()
    create_sample_products()
    create_sample_orders()

    print("=" * 60)
    print("示例数据初始化完成！")
    print("=" * 60)
