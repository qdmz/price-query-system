#!/usr/bin/env python
"""
检查数据是否能正确显示在页面上
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.services.statistics_service import StatisticsService
from datetime import datetime

def check_data_display():
    """检查数据是否可以正确显示"""
    app = create_app()

    print("=" * 60)
    print("数据显示检查")
    print("=" * 60)

    with app.app_context():
        # 1. 检查销售概况
        print("\n[1] 销售概况:")
        overview = StatisticsService.get_sales_overview()
        print(f"  总订单数: {overview['total_orders']}")
        print(f"  总销售额: ¥{overview['total_sales']}")
        print(f"  销售数量: {overview['total_quantity']}")
        print(f"  平均订单金额: ¥{overview['avg_order_amount']}")

        # 2. 检查产品销售比例
        print("\n[2] 产品销售比例 (Top 5):")
        products = StatisticsService.get_product_sales_ratio(limit=5)
        for idx, p in enumerate(products, 1):
            print(f"  {idx}. {p['product_name']}: ¥{p['total_sales']} ({p['total_quantity']}件)")

        # 3. 检查客户排名
        print("\n[3] 客户消费排名 (Top 5):")
        customers = StatisticsService.get_customer_ranking(limit=5)
        for idx, c in enumerate(customers, 1):
            print(f"  {idx}. {c['customer_name']}: ¥{c['total_amount']} ({c['order_count']}单)")

        # 4. 检查畅销品
        print("\n[4] 畅销品 (Top 5):")
        best_selling = StatisticsService.get_best_selling_products(limit=5)
        for idx, b in enumerate(best_selling, 1):
            print(f"  {idx}. {b['product_name']}: {b['total_quantity']}件, ¥{b['total_sales']}")

        # 5. 检查滞销品
        print("\n[5] 滞销品 (Top 5):")
        slow_moving = StatisticsService.get_slow_moving_products(limit=5)
        for idx, s in enumerate(slow_moving, 1):
            print(f"  {idx}. {s['product_name']}: 库存{s['stock']} (最后销售: {s['last_sale_date']})")

        # 6. 检查月度统计
        print("\n[6] 月度统计 (2026年1月):")
        monthly = StatisticsService.get_monthly_statistics(2026, 1)
        print(f"  总订单数: {monthly['overview']['total_orders']}")
        print(f"  总销售额: ¥{monthly['overview']['total_sales']}")
        print(f"  销售数量: {monthly['overview']['total_quantity']}")
        print(f"  平均订单金额: ¥{monthly['overview']['avg_order_amount']}")

        print("\n  每日销售 (前5天):")
        for day in monthly['daily_sales'][:5]:
            print(f"    {day['date']}: {day['order_count']}单, ¥{day['total_sales']}")

        # 7. 检查年度汇总
        print("\n[7] 年度汇总 (2025年):")
        yearly = StatisticsService.get_yearly_summary(2025)
        print(f"  月份\t订单数\t销售额")
        for item in yearly['monthly_sales']:
            if item['order_count'] > 0:
                print(f"  {item['month']}\t{item['order_count']}\t¥{item['total_sales']}")

        # 8. 检查模板渲染
        print("\n[8] 模板渲染测试:")
        with app.test_request_context():
            from flask import render_template
            try:
                now = datetime.now()
                stats = {
                    'overview': overview,
                    'product_sales_ratio': products,
                    'customer_ranking': customers,
                    'best_selling': best_selling,
                    'slow_moving': slow_moving,
                    'monthly_sales': monthly.get('daily_sales', [])
                }

                html = render_template('admin/statistics.html',
                                      stats=stats,
                                      current_year=now.year,
                                      current_month=now.month,
                                      start_date=None,
                                      end_date=None)

                if html and len(html) > 0:
                    print(f"  ✓ 模板渲染成功")
                    print(f"  ✓ HTML长度: {len(html)} 字符")

                    # 检查关键数据是否存在
                    checks = [
                        ('销售订单数', str(overview['total_orders'])),
                        ('销售额', str(int(overview['total_sales']))),
                        ('产品销售比例', 'product_sales_ratio'),
                        ('客户排名', 'customer_ranking'),
                        ('畅销品', 'best_selling'),
                        ('滞销品', 'slow_moving'),
                        ('月度销售', 'monthly_sales'),
                    ]

                    print("\n  关键数据检查:")
                    for name, value in checks:
                        if value in html:
                            print(f"    ✓ {name} 数据存在")
                        else:
                            print(f"    ✗ {name} 数据不存在")

                else:
                    print("  ✗ 模板渲染失败")
            except Exception as e:
                print(f"  ✗ 模板渲染错误: {e}")

        print("\n" + "=" * 60)
        print("检查完成！")
        print("=" * 60)

        print("\n建议操作：")
        print("1. 清除浏览器缓存 (Ctrl + Shift + Delete)")
        print("2. 使用无痕模式重新打开页面")
        print("3. 按 Ctrl + F5 强制刷新页面")
        print("4. 登录后台: http://localhost:5000/auth/login")
        print("5. 进入数据统计页面: http://localhost:5000/admin/statistics")

if __name__ == '__main__':
    check_data_display()
