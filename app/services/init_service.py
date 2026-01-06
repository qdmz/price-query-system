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
            'description': '清新薄荷味牙膏，有效清洁口腔',
            'category': '个人护理'
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
            'description': '去屑洗发水，适用于所有发质',
            'category': '个人护理'
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
            'description': '薰衣草香洗衣液，温和不伤手',
            'category': '清洁用品'
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
            'description': '纯棉毛巾，柔软舒适',
            'category': '家居纺织'
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
            'description': '3层加厚抽纸，纸质柔软',
            'category': '纸品湿巾'
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
            'description': '海洋香型沐浴露，清爽洁净',
            'category': '个人护理'
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
            'description': '柠檬味洗洁精，去油污效果好',
            'category': '清洁用品'
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
            'description': '原生木浆卷纸，韧性好',
            'category': '纸品湿巾'
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
            'description': '加厚垃圾袋，不易破损',
            'category': '厨房用品'
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
            'description': '滋润型护手霜，保护双手',
            'category': '个人护理'
        },
    ]

    placeholder_image_url = '/static/images/product-placeholder.jpg'

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

        # 为每个产品添加占位图片
        image = ProductImage(
            product_id=product.id,
            image_url=placeholder_image_url,
            is_primary=True,
            sort_order=0
        )
        db.session.add(image)

    db.session.commit()
    print(f"示例产品已创建，共 {len(products_data)} 条")

def init_sample_data():
    """初始化所有示例数据"""
    print("=" * 60)
    print("开始初始化示例数据...")
    print("=" * 60)

    create_default_admin()
    create_default_settings()
    create_sample_categories()
    create_sample_products()

    print("=" * 60)
    print("示例数据初始化完成！")
    print("=" * 60)
