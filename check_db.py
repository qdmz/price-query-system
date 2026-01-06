from app import create_app
from app.models import db, Product, Order, Category

app = create_app('development')
with app.app_context():
    print("=" * 60)
    print("数据库统计")
    print("=" * 60)
    print(f"分类数量: {Category.query.count()}")
    print(f"产品数量: {Product.query.count()}")
    print(f"订单数量: {Order.query.count()}")
    print("=" * 60)
