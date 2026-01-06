#!/usr/bin/env python
import os
os.environ['FLASK_ENV'] = 'production'

from app import create_app
from app.models import db, Product, Order

# 初始化标志文件路径
INIT_FLAG_FILE = ".initialized"

def check_and_init_data():
    """检查并执行数据初始化"""
    # 检查是否已经初始化
    if os.path.exists(INIT_FLAG_FILE):
        print("系统已初始化，跳过数据初始化步骤")
        return
    
    # 检查数据库中是否有产品和订单数据
    app = create_app()
    with app.app_context():
        product_count = Product.query.count()
        order_count = Order.query.count()
        
        if product_count > 0 or order_count > 0:
            print(f"数据库已有数据（产品: {product_count}, 订单: {order_count}），跳过初始化")
            # 创建初始化标志
            with open(INIT_FLAG_FILE, 'w') as f:
                f.write('initialized')
            return
        
        # 执行数据初始化
        print("检测到首次启动，正在初始化数据...")
        try:
            import init_data
            init_data.init_all_data()
            
            # 创建初始化标志
            with open(INIT_FLAG_FILE, 'w') as f:
                f.write('initialized')
            
            print("数据初始化完成！")
        except Exception as e:
            print(f"数据初始化失败: {e}")

# 在启动应用前执行数据初始化
try:
    check_and_init_data()
except Exception as e:
    print(f"数据初始化检查失败（不影响应用启动）: {e}")

# 启动应用
from wsgi import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
