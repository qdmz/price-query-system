from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_required
from app.models import db, SystemSetting

system_bp = Blueprint('system', __name__, url_prefix='/system')

@system_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """系统设置页面"""
    
    # 定义配置项
    settings_config = {
        'mail': {
            'title': '邮件通知设置',
            'icon': 'bi-envelope',
            'fields': [
                {
                    'key': 'MAIL_SERVER',
                    'label': 'SMTP 服务器',
                    'type': 'text',
                    'placeholder': 'smtp.example.com',
                    'description': '例如：smtp.gmail.com, smtp.qq.com'
                },
                {
                    'key': 'MAIL_PORT',
                    'label': 'SMTP 端口',
                    'type': 'number',
                    'placeholder': '587',
                    'description': '通常为 587 (TLS) 或 465 (SSL)'
                },
                {
                    'key': 'MAIL_USE_TLS',
                    'label': '启用 TLS',
                    'type': 'select',
                    'options': ['true', 'false'],
                    'description': '大多数现代 SMTP 服务器需要 TLS'
                },
                {
                    'key': 'MAIL_USERNAME',
                    'label': 'SMTP 用户名',
                    'type': 'text',
                    'placeholder': 'your-email@example.com',
                    'description': '通常是完整的邮箱地址'
                },
                {
                    'key': 'MAIL_PASSWORD',
                    'label': 'SMTP 密码/授权码',
                    'type': 'password',
                    'description': '注意：QQ邮箱等需要使用授权码，不是登录密码'
                },
                {
                    'key': 'MAIL_DEFAULT_SENDER',
                    'label': '发件人地址',
                    'type': 'text',
                    'placeholder': 'noreply@example.com',
                    'description': '通知邮件的发送者地址'
                },
                {
                    'key': 'MAIL_NOTIFICATION_ENABLED',
                    'label': '启用邮件通知',
                    'type': 'select',
                    'options': ['true', 'false'],
                    'description': '是否在订单状态变更时发送邮件通知'
                }
            ]
        },
        'sms': {
            'title': '短信通知设置',
            'icon': 'bi-phone',
            'fields': [
                {
                    'key': 'SMS_API_URL',
                    'label': '短信 API 地址',
                    'type': 'text',
                    'placeholder': 'https://sms-api.example.com/send',
                    'description': '短信服务提供商的 API 地址'
                },
                {
                    'key': 'SMS_API_KEY',
                    'label': 'API 密钥',
                    'type': 'password',
                    'description': '短信服务的访问密钥'
                },
                {
                    'key': 'SMS_API_SECRET',
                    'label': 'API 密钥 Secret',
                    'type': 'password',
                    'description': '短信服务的密钥 Secret'
                },
                {
                    'key': 'SMS_NOTIFICATION_ENABLED',
                    'label': '启用短信通知',
                    'type': 'select',
                    'options': ['true', 'false'],
                    'description': '是否在订单状态变更时发送短信通知'
                }
            ]
        },
        'system': {
            'title': '系统设置',
            'icon': 'bi-gear',
            'fields': [
                {
                    'key': 'SITE_NAME',
                    'label': '网站名称',
                    'type': 'text',
                    'placeholder': '日用产品批发零售系统',
                    'description': '显示在网站标题和页面中的名称'
                },
                {
                    'key': 'ADMIN_EMAIL',
                    'label': '管理员邮箱',
                    'type': 'email',
                    'placeholder': 'admin@example.com',
                    'description': '接收系统通知的邮箱'
                },
                {
                    'key': 'ADMIN_PHONE',
                    'label': '管理员电话',
                    'type': 'text',
                    'placeholder': '13800000000',
                    'description': '接收紧急通知的电话号码'
                }
            ]
        }
    }
    
    if request.method == 'POST':
        # 保存设置
        for category, config in settings_config.items():
            for field in config['fields']:
                key = field['key']
                value = request.form.get(key, '')
                
                # 保存到数据库
                setting = SystemSetting.query.filter_by(key=key).first()
                if setting:
                    setting.value = value
                else:
                    setting = SystemSetting(key=key, value=value, description=field.get('description', ''))
                    db.session.add(setting)
        
        db.session.commit()
        flash('系统设置已保存', 'success')
        return redirect(url_for('system.settings'))
    
    # 获取当前设置值
    settings_data = {}
    for setting in SystemSetting.query.all():
        settings_data[setting.key] = setting.value
    
    return render_template('system/settings.html', 
                         settings_config=settings_config,
                         settings_data=settings_data)


@system_bp.route('/settings/test/<setting_type>', methods=['POST'])
@login_required
def test_setting(setting_type):
    """测试配置"""
    from app.services.notification_service import NotificationService
    
    try:
        notification = NotificationService()
        
        if setting_type == 'mail':
            to_email = request.form.get('test_email')
            if to_email:
                success = notification.send_order_notification(
                    to_email,
                    '测试订单',
                    'test-001',
                    pending_items=[],
                    completed_items=[],
                    cancelled_items=[]
                )
                
                if success:
                    flash('邮件测试成功！请检查收件箱。', 'success')
                else:
                    flash('邮件测试失败，请检查配置。', 'error')
        
        elif setting_type == 'sms':
            to_phone = request.form.get('test_phone')
            if to_phone:
                success = notification.send_sms_notification_test(
                    to_phone,
                    '这是一条测试短信。'
                )
                
                if success:
                    flash('短信测试成功！', 'success')
                else:
                    flash('短信测试失败，请检查配置。', 'error')
    
    except Exception as e:
        flash(f'测试失败：{str(e)}', 'error')
    
    return redirect(url_for('system.settings'))
