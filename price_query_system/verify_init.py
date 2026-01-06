#!/usr/bin/env python
"""
快速验证初始化数据的脚本
用于检查系统数据是否正确初始化
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app, db
from app.models import User, SystemSetting, Category, Product, ProductImage, Order, OrderItem
from sqlalchemy import extract, func


def verify_init_data():
    """验证初始化数据"""
    app = create_app()
    
    print("=" * 70)
    print("数据初始化验证")
    print("=" * 70)
    
    with app.app_context():
        # 1. 检查管理员账户
        print("\n[1] 管理员账户检查")
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f"  ✓ 管理员账户存在: {admin.username}")
            print(f"  ✓ 邮箱: {admin.email}")
            print(f"  ✓ 角色: {admin.role}")
        else:
            print("  ✗ 管理员账户不存在")
        
        # 2. 检查系统设置
        print("\n[2] 系统设置检查")
        settings_count = SystemSetting.query.count()
        print(f"  ✓ 系统设置数量: {settings_count}")
        
        # 3. 检查产品分类
        print("\n[3] 产品分类检查")
        categories = Category.query.all()
        print(f"  ✓ 分类数量: {len(categories)}")
        if len(categories) > 0:
            print("  分类列表:")
            for cat in categories:
                product_count = Product.query.filter_by(category_id=cat.id).count()
                print(f"    - {cat.name}: {product_count}个产品")
        
        # 4. 检查产品数据
        print("\n[4] 产品数据检查")
        products = Product.query.all()
        print(f"  ✓ 产品总数: {len(products)}")
        
        active_products = Product.query.filter_by(status='active').count()
        print(f"  ✓ 上架产品: {active_products}")
        
        total_stock = db.session.query(func.sum(Product.stock)).scalar() or 0
        print(f"  ✓ 总库存: {int(total_stock)}")
        
        if len(products) > 0:
            print("\n  前5个产品:")
            for p in products[:5]:
                print(f"    - {p.product_code}: {p.name} (库存: {p.stock}, 零售价: ¥{p.retail_price})")
        
        # 5. 检查产品图片
        print("\n[5] 产品图片检查")
        image_count = ProductImage.query.count()
        print(f"  ✓ 图片总数: {image_count}")
        
        products_with_images = 0
        for p in products:
            if p.images.count() > 0:
                products_with_images += 1
        
        print(f"  ✓ 有图片的产品: {products_with_images}/{len(products)}")
        
        if len(products) > 0:
            print("\n  前3个产品的图片数量:")
            for p in products[:3]:
                print(f"    - {p.name}: {p.images.count()}张")
        
        # 6. 检查订单数据
        print("\n[6] 订单数据检查")
        orders = Order.query.all()
        print(f"  ✓ 订单总数: {len(orders)}")
        
        if len(orders) > 0:
            order_items = OrderItem.query.count()
            print(f"  ✓ 订单项总数: {order_items}")
            
            total_amount = db.session.query(func.sum(Order.total_amount)).scalar() or 0
            print(f"  ✓ 订单总金额: ¥{total_amount:.2f}")
            
            # 按状态统计
            print("\n  订单状态分布:")
            status_stats = db.session.query(
                Order.status,
                func.count(Order.id).label('count')
            ).group_by(Order.status).all()
            
            for status, count in status_stats:
                status_name = {
                    'pending': '待处理',
                    'confirmed': '已确认',
                    'shipped': '已发货',
                    'completed': '已完成',
                    'cancelled': '已取消'
                }.get(status, status)
                print(f"    - {status_name}: {count}单")
            
            # 按月份统计
            print("\n  各月订单统计:")
            month_stats = db.session.query(
                extract('year', Order.created_at).label('year'),
                extract('month', Order.created_at).label('month'),
                func.count(Order.id).label('count'),
                func.sum(Order.total_amount).label('total')
            ).group_by(
                extract('year', Order.created_at),
                extract('month', Order.created_at)
            ).order_by(
                extract('year', Order.created_at),
                extract('month', Order.created_at)
            ).all()
            
            for year, month, count, total in month_stats:
                print(f"    - {year}年{int(month)}月: {count}单, ¥{total:.2f}")
        else:
            print("  ⚠ 暂无订单数据")
        
        # 总结
        print("\n" + "=" * 70)
        print("验证完成")
        print("=" * 70)
        
        expected_data = {
            '管理员账户': 1 if admin else 0,
            '系统设置': settings_count,
            '产品分类': len(categories),
            '产品数据': len(products),
            '产品图片': image_count,
            '订单数据': len(orders)
        }
        
        # 判断是否完全初始化
        is_fully_initialized = (
            admin is not None and
            settings_count >= 5 and
            len(categories) == 6 and
            len(products) == 15 and
            image_count >= 40 and
            len(orders) >= 100
        )
        
        print("\n初始化状态:")
        if is_fully_initialized:
            print("  ✓ 所有数据已正确初始化")
        else:
            print("  ⚠ 数据未完全初始化，请运行: python init_data.py")
        
        return is_fully_initialized


if __name__ == '__main__':
    success = verify_init_data()
    sys.exit(0 if success else 1)
