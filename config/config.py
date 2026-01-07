import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key-change-in-production'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'postgresql://postgres:postgres@localhost:5432/price_query_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 上传文件配置
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'app', 'static', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'xlsx', 'xls', 'csv'}
    
    # 邮件配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.example.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USE_SSL = os.environ.get('MAIL_USE_SSL', 'false').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'noreply@example.com'
    
    # 短信配置（示例配置，实际使用需要对接短信服务商）
    SMS_API_URL = os.environ.get('SMS_API_URL')
    SMS_API_KEY = os.environ.get('SMS_API_KEY')
    SMS_SIGN_NAME = os.environ.get('SMS_SIGN_NAME', '')  # 短信签名
    
    # 阿里云短信配置（可选）
    ALIYUN_ACCESS_KEY_ID = os.environ.get('ALIYUN_ACCESS_KEY_ID')
    ALIYUN_ACCESS_KEY_SECRET = os.environ.get('ALIYUN_ACCESS_KEY_SECRET')
    ALIYUN_SMS_SIGN_NAME = os.environ.get('ALIYUN_SMS_SIGN_NAME')
    ALIYUN_SMS_TEMPLATE_CODE = os.environ.get('ALIYUN_SMS_TEMPLATE_CODE')
    
    # 管理员配置
    ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME') or 'admin'
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') or 'admin123'
    ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL') or 'admin@example.com'
    
    # 分页配置
    PRODUCTS_PER_PAGE = 20
    ORDERS_PER_PAGE = 20
    
    # 会话配置
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///price_query.db'

class ProductionConfig(Config):
    DEBUG = False
    # 如果没有设置DATABASE_URL环境变量，则降级使用SQLite
    # 使用临时目录确保数据可以保存
    import tempfile
    temp_dir = tempfile.gettempdir()
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        f'sqlite:///{os.path.join(temp_dir, "price_query.db")}'
    # 在生产环境（FaaS）使用临时目录存储上传文件
    UPLOAD_FOLDER = os.path.join(temp_dir, 'uploads')

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
