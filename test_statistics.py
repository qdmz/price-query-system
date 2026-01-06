#!/usr/bin/env python
"""
测试数据统计功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.services.statistics_service import StatisticsService
from app.models import db, Order, OrderItem, Product

def test_statistics():
    """测试统计功能"""
    app = create_app()
    
    with app.app_context():
        # 测试销售概况
        print("=== 测试销售概况 ===")
        overview = StatisticsService.get_sales_overview()
        print(f"总订单数: {overview['total_orders']}")
        print(f"总销售额: {overview['total_sales']}")
        print(f"销售数量: {overview['total_quantity']}")
        print(f"平均订单金额: {overview['avg_order_amount']}")
        print()
        
        # 测试产品销售比例
        print("=== 测试产品销售比例 ===")
        product_sales = StatisticsService.get_product_sales_ratio(limit=5)
        for item in product_sales:
            print(f"{item['product_name']}: ¥{item['total_sales']} (数量: {item['total_quantity']})")
        print()
        
        # 测试客户排名
        print("=== 测试客户消费排名 ===")
        customers = StatisticsService.get_customer_ranking(limit=5)
        for item in customers:
            print(f"{item['customer_name']}: ¥{item['total_amount']} (订单数: {item['order_count']})")
        print()
        
        # 测试畅销品
        print("=== 测试畅销品 ===")
        best_selling = StatisticsService.get_best_selling_products(limit=5)
        for item in best_selling:
            print(f"{item['product_name']}: {item['total_quantity']}件 (¥{item['total_sales']})")
        print()
        
        # 测试滞销品
        print("=== 测试滞销品 ===")
        slow_moving = StatisticsService.get_slow_moving_products(limit=5)
        for item in slow_moving:
            print(f"{item['product_name']}: 库存{item['stock']} (最后销售: {item['last_sale_date']})")
        print()
        
        # 测试月度统计
        print("=== 测试月度统计 ===")
        from datetime import datetime
        now = datetime.now()
        monthly = StatisticsService.get_monthly_statistics(now.year, now.month)
        print(f"月份: {monthly['year']}-{monthly['month']}")
        print(f"总订单数: {monthly['overview']['total_orders']}")
        print(f"总销售额: {monthly['overview']['total_sales']}")
        print()
        
        # 测试年度汇总
        print("=== 测试年度汇总 ===")
        yearly = StatisticsService.get_yearly_summary(now.year)
        print(f"年份: {yearly['year']}")
        for item in yearly['monthly_sales']:
            if item['order_count'] > 0:
                print(f"{item['month']}月: 订单{item['order_count']}, 销售额¥{item['total_sales']}")
        print()
        
        print("=== 所有测试通过 ===")

if __name__ == '__main__':
    test_statistics()
