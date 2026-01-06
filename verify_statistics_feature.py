#!/usr/bin/env python
"""
验证数据统计功能完整性
"""
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath('.'))

def verify_statistics_feature():
    """验证数据统计功能"""
    print("=" * 60)
    print("数据统计功能验证")
    print("=" * 60)
    
    # 1. 验证文件是否存在
    print("\n[1/5] 验证文件是否存在...")
    files_to_check = [
        'app/services/statistics_service.py',
        'app/templates/admin/statistics.html',
        'app/routes/admin.py'
    ]
    
    all_files_exist = True
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"  ✓ {file_path}")
        else:
            print(f"  ✗ {file_path} 不存在")
            all_files_exist = False
    
    if not all_files_exist:
        print("\n❌ 部分文件缺失，请检查")
        return False
    
    # 2. 验证服务层功能
    print("\n[2/5] 验证服务层功能...")
    from app import create_app
    from app.services.statistics_service import StatisticsService
    
    app = create_app()
    
    with app.app_context():
        try:
            # 测试各个统计方法
            StatisticsService.get_sales_overview()
            print("  ✓ get_sales_overview()")
            
            StatisticsService.get_product_sales_ratio()
            print("  ✓ get_product_sales_ratio()")
            
            StatisticsService.get_customer_ranking()
            print("  ✓ get_customer_ranking()")
            
            StatisticsService.get_best_selling_products()
            print("  ✓ get_best_selling_products()")
            
            StatisticsService.get_slow_moving_products()
            print("  ✓ get_slow_moving_products()")
            
            from datetime import datetime
            now = datetime.now()
            StatisticsService.get_monthly_statistics(now.year, now.month)
            print("  ✓ get_monthly_statistics()")
            
            StatisticsService.get_yearly_summary(now.year)
            print("  ✓ get_yearly_summary()")
            
        except Exception as e:
            print(f"  ✗ 服务层功能测试失败: {e}")
            return False
    
    # 3. 验证路由注册
    print("\n[3/5] 验证路由注册...")
    with app.app_context():
        with app.test_request_context():
            from flask import url_for
            try:
                url_for('admin.statistics')
                print("  ✓ /admin/statistics")
                
                url_for('admin.export_monthly_report', year=2024, month=1)
                print("  ✓ /admin/statistics/export/monthly/<year>/<month>")
                
                url_for('admin.export_product_sales')
                print("  ✓ /admin/statistics/export/product-sales")
                
                url_for('admin.export_customer_ranking')
                print("  ✓ /admin/statistics/export/customer-ranking")
                
                url_for('admin.export_best_selling')
                print("  ✓ /admin/statistics/export/best-selling")
                
                url_for('admin.export_slow_moving')
                print("  ✓ /admin/statistics/export/slow-moving")
                
            except Exception as e:
                print(f"  ✗ 路由注册失败: {e}")
                return False
    
    # 4. 验证报表导出
    print("\n[4/5] 验证报表导出...")
    with app.app_context():
        try:
            from datetime import datetime
            now = datetime.now()
            
            file_path = StatisticsService.export_monthly_report(now.year, now.month)
            if os.path.exists(file_path):
                print("  ✓ 月报表导出成功")
            else:
                print("  ✗ 月报表导出失败")
                return False
            
            file_path = StatisticsService.export_product_sales()
            if os.path.exists(file_path):
                print("  ✓ 产品销售报表导出成功")
            else:
                print("  ✗ 产品销售报表导出失败")
                return False
            
            file_path = StatisticsService.export_customer_ranking()
            if os.path.exists(file_path):
                print("  ✓ 客户排名报表导出成功")
            else:
                print("  ✗ 客户排名报表导出失败")
                return False
            
        except Exception as e:
            print(f"  ✗ 报表导出失败: {e}")
            return False
    
    # 5. 验证模板文件
    print("\n[5/5] 验证模板文件...")
    try:
        with app.app_context():
            with app.test_request_context():
                from flask import render_template
                
                from datetime import datetime
                now = datetime.now()
                
                # 模拟统计数据
                stats = {
                    'overview': StatisticsService.get_sales_overview(),
                    'product_sales_ratio': StatisticsService.get_product_sales_ratio(),
                    'customer_ranking': StatisticsService.get_customer_ranking(),
                    'best_selling': StatisticsService.get_best_selling_products(),
                    'slow_moving': StatisticsService.get_slow_moving_products(),
                    'monthly_sales': StatisticsService.get_monthly_statistics(now.year, now.month).get('daily_sales', [])
                }
                
                html = render_template('admin/statistics.html', 
                                      stats=stats,
                                      current_year=now.year,
                                      current_month=now.month,
                                      start_date=None,
                                      end_date=None)
                
                if html and len(html) > 0:
                    print("  ✓ 模板渲染成功")
                else:
                    print("  ✗ 模板渲染失败")
                    return False
                
    except Exception as e:
        print(f"  ✗ 模板渲染失败: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("✅ 所有验证通过，数据统计功能完整可用！")
    print("=" * 60)
    
    return True

if __name__ == '__main__':
    success = verify_statistics_feature()
    sys.exit(0 if success else 1)
