#!/usr/bin/env python
"""
生成多个月的订单数据用于测试数据统计月报功能
"""
import sys
import os
import random
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import db, Order, OrderItem, Product
from app.services.order_service import OrderService

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

# 随机电话号码
def generate_phone():
    """生成随机电话号码"""
    return f"1{random.choice(['3', '5', '7', '8', '9'])}{random.randint(100000000, 999999999)}"


def generate_orders_for_month(year, month, num_orders):
    """
    为指定月份生成订单
    
    Args:
        year: 年份
        month: 月份
        num_orders: 订单数量
    """
    # 获取该月的产品
    products = Product.query.filter_by(status='active').all()
    
    if not products:
        print(f"  ⚠ 没有可用的产品")
        return
    
    # 该月的开始和结束日期
    start_date = datetime(year, month, 1)
    if month == 12:
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    # 生成该月的订单
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
            
            # 创建订单项目
            items = []
            for product in selected_products:
                quantity = random.randint(1, 10)
                items.append({
                    'product_id': product.id,
                    'quantity': quantity
                })
            
            # 创建订单数据
            order_data = {
                'customer_name': customer_name,
                'customer_phone': customer_phone,
                'customer_email': customer_email,
                'customer_address': customer_address,
                'items': items,
                'notes': f'自动生成的测试订单 - {year}年{month}月'
            }
            
            # 创建订单
            order = OrderService.create_order(order_data)
            
            # 修改订单创建时间为指定时间
            order.created_at = order_date
            order.updated_at = order_date
            
            # 随机设置订单状态（70%完成，20%已确认，10%已取消）
            status_rand = random.random()
            if status_rand < 0.7:
                order.status = 'completed'
            elif status_rand < 0.9:
                order.status = 'confirmed'
            else:
                order.status = 'cancelled'
            
            db.session.commit()
            
            print(f"  ✓ 订单 {order.order_no} - {customer_name} - ¥{order.total_amount:.2f} - {order.status}")
            
        except Exception as e:
            db.session.rollback()
            print(f"  ✗ 订单创建失败: {e}")


def generate_multi_month_orders():
    """生成多个月的订单数据"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("开始生成多个月份的订单数据...")
        print("=" * 60)
        
        # 清空现有订单（可选，注释掉这行则保留现有订单）
        # db.session.query(OrderItem).delete()
        # db.session.query(Order).delete()
        # db.session.commit()
        # print("已清空现有订单数据\n")
        
        # 获取当前时间
        now = datetime.now()
        
        # 定义要生成的月份和订单数量
        # 过去6个月的数据，每个月订单数量递增
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
            # 第1个月（最早）：5-10单
            # 第2个月：10-15单
            # 第3个月：15-20单
            # 第4个月：20-25单
            # 第5个月：25-30单
            # 第6个月（最近）：30-40单
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
            
            print(f"\n生成 {year}年{month}月 的订单 ({num_orders}单)")
            print("-" * 60)
            
            generate_orders_for_month(year, month, num_orders)
            total_orders += num_orders
        
        print("\n" + "=" * 60)
        print(f"订单生成完成！共生成 {total_orders} 个订单")
        print("=" * 60)
        
        # 统计各月订单数
        print("\n各月订单统计:")
        print("-" * 60)
        
        month_stats = db.session.query(
            db.extract('year', Order.created_at).label('year'),
            db.extract('month', Order.created_at).label('month'),
            db.func.count(Order.id).label('count'),
            db.func.sum(Order.total_amount).label('total_amount')
        ).group_by(
            db.extract('year', Order.created_at),
            db.extract('month', Order.created_at)
        ).order_by('year', 'month').all()
        
        for stat in month_stats:
            print(f"{int(stat.year)}年{int(stat.month)}月: {stat.count}单, ¥{stat.total_amount or 0:.2f}")
        
        print("=" * 60)


if __name__ == '__main__':
    generate_multi_month_orders()
