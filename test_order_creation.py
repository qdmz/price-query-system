#!/usr/bin/env python
"""
测试订单创建功能
"""
from app import create_app
from app.services.order_service import OrderService

app = create_app()

with app.app_context():
    print("=" * 60)
    print("测试订单创建功能")
    print("=" * 60)
    
    # 测试数据
    test_order_data = {
        'customer_name': '测试客户',
        'customer_phone': '13800138000',
        'customer_email': 'test@example.com',
        'customer_address': '北京市朝阳区测试街道123号',
        'notes': '这是测试订单',
        'items': [
            {'product_id': 1, 'quantity': 2},  # 购买2个，应该使用批发价
            {'product_id': 2, 'quantity': 1},  # 购买1个，应该使用零售价
        ]
    }
    
    try:
        print("\n正在创建订单...")
        order = OrderService.create_order(test_order_data)
        
        print(f"\n✓ 订单创建成功！")
        print(f"  订单号: {order.order_no}")
        print(f"  客户: {order.customer_name}")
        print(f"  总金额: ¥{order.total_amount:.2f}")
        print(f"  总数量: {order.total_quantity}")
        print(f"  状态: {order.status}")
        
        print(f"\n订单明细:")
        for item in order.items:
            print(f"  - {item.product_name} x {item.quantity} = ¥{item.subtotal:.2f}")
        
        print("\n" + "=" * 60)
        print("✓ 订单创建功能测试通过！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 订单创建失败！")
        print(f"错误信息: {str(e)}")
        import traceback
        traceback.print_exc()
        print("\n" + "=" * 60)
