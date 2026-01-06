#!/usr/bin/env python
"""
测试报表导出功能
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.services.statistics_service import StatisticsService

def test_export():
    """测试报表导出"""
    app = create_app()
    
    with app.app_context():
        from datetime import datetime
        now = datetime.now()
        
        print("=== 测试报表导出 ===")
        
        # 测试导出月报表
        print("\n1. 导出月报表...")
        try:
            file_path = StatisticsService.export_monthly_report(now.year, now.month)
            print(f"   ✓ 月报表导出成功: {file_path}")
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   文件大小: {size} bytes")
        except Exception as e:
            print(f"   ✗ 月报表导出失败: {e}")
        
        # 测试导出产品销售报表
        print("\n2. 导出产品销售报表...")
        try:
            file_path = StatisticsService.export_product_sales()
            print(f"   ✓ 产品销售报表导出成功: {file_path}")
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   文件大小: {size} bytes")
        except Exception as e:
            print(f"   ✗ 产品销售报表导出失败: {e}")
        
        # 测试导出客户排名报表
        print("\n3. 导出客户排名报表...")
        try:
            file_path = StatisticsService.export_customer_ranking()
            print(f"   ✓ 客户排名报表导出成功: {file_path}")
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   文件大小: {size} bytes")
        except Exception as e:
            print(f"   ✗ 客户排名报表导出失败: {e}")
        
        # 测试导出畅销品报表
        print("\n4. 导出畅销品报表...")
        try:
            data = StatisticsService.get_best_selling_products(limit=10)
            file_path = StatisticsService.export_to_excel(data, f'畅销品报表_{now.strftime("%Y%m%d")}.xlsx')
            print(f"   ✓ 畅销品报表导出成功: {file_path}")
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   文件大小: {size} bytes")
        except Exception as e:
            print(f"   ✗ 畅销品报表导出失败: {e}")
        
        # 测试导出滞销品报表
        print("\n5. 导出滞销品报表...")
        try:
            data = StatisticsService.get_slow_moving_products()
            file_path = StatisticsService.export_to_excel(data, f'滞销品报表_{now.strftime("%Y%m%d")}.xlsx')
            print(f"   ✓ 滞销品报表导出成功: {file_path}")
            if os.path.exists(file_path):
                size = os.path.getsize(file_path)
                print(f"   文件大小: {size} bytes")
        except Exception as e:
            print(f"   ✗ 滞销品报表导出失败: {e}")
        
        print("\n=== 所有导出测试完成 ===")

if __name__ == '__main__':
    test_export()
