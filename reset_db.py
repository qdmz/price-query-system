from app import create_app
from app.models import db

app = create_app('production')
with app.app_context():
    print("正在重置数据库...")
    db.drop_all()
    db.create_all()
    print("✓ 数据库已重置")

    # 创建默认管理员
    from app.services.init_service import create_default_admin
    create_default_admin()
    print("✓ 默认管理员已创建")
