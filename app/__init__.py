from flask import Flask, send_from_directory
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from app.models import db, User
import os

# 初始化扩展
login_manager = LoginManager()
mail = Mail()
migrate = Migrate()

def create_app(config_name='default'):
    app = Flask(__name__)
    
    # 加载配置
    from config import config
    app.config.from_object(config[config_name])
    
    # 确保上传目录存在（处理只读文件系统）
    try:
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'orders'), exist_ok=True)
    except OSError as e:
        # 如果文件系统只读，使用临时目录
        if e.errno == 30:  # Read-only file system
            import tempfile
            temp_dir = tempfile.gettempdir()
            app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
            os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
            os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'orders'), exist_ok=True)
            print(f"[WARN] Using temporary directory for uploads: {app.config['UPLOAD_FOLDER']}")
        else:
            raise
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    
    # 配置登录管理器
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录'
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # 注册蓝图
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.api import api_bp
    from app.routes.admin import admin_bp
    from app.routes.system_settings import system_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(system_bp)
    
    # 添加上传文件的路由（处理临时目录）
    @app.route('/static/uploads/<path:filename>')
    def serve_upload_file(filename):
        """提供上传的文件（包括临时目录）"""
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
        # 创建默认管理员账户
        from app.services.init_service import create_default_admin
        create_default_admin()
    
    return app
