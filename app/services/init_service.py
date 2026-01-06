from app.models import db, User, SystemSetting
from flask import current_app

def create_default_admin():
    """创建默认管理员账户"""
    admin = User.query.filter_by(username=current_app.config['ADMIN_USERNAME']).first()
    
    if not admin:
        admin = User(
            username=current_app.config['ADMIN_USERNAME'],
            email=current_app.config['ADMIN_EMAIL'],
            role='admin'
        )
        admin.set_password(current_app.config['ADMIN_PASSWORD'])
        db.session.add(admin)
        db.session.commit()
        print(f"默认管理员账户已创建 - 用户名: {admin.username}, 密码: {current_app.config['ADMIN_PASSWORD']}")
    else:
        print("管理员账户已存在")

def create_default_settings():
    """创建默认系统设置"""
    default_settings = {
        'email_enabled': 'false',
        'sms_enabled': 'false',
        'notification_emails': '',
        'admin_phones': '',
        'company_name': '日用产品批发零售系统',
        'company_phone': '',
        'company_address': '',
    }
    
    for key, value in default_settings.items():
        setting = SystemSetting.query.filter_by(key=key).first()
        if not setting:
            setting = SystemSetting(key=key, value=value)
            db.session.add(setting)
    
    db.session.commit()
