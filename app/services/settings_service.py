"""系统设置服务"""

from app.models import SystemSetting, db


class SettingsService:
    """系统设置服务类"""
    
    @staticmethod
    def get_setting(key, default=''):
        """
        获取单个设置值
        
        Args:
            key: 设置键
            default: 默认值
            
        Returns:
            设置值，如果不存在则返回默认值
        """
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            return setting.value
        return default
    
    @staticmethod
    def get_settings(keys, default=''):
        """
        批量获取设置值
        
        Args:
            keys: 设置键列表
            default: 默认值
            
        Returns:
            字典，键为设置键，值为对应的设置值
        """
        settings = {}
        for key in keys:
            settings[key] = SettingsService.get_setting(key, default)
        return settings
    
    @staticmethod
    def set_setting(key, value, description=''):
        """
        设置单个配置项
        
        Args:
            key: 设置键
            value: 设置值
            description: 描述
            
        Returns:
            设置对象
        """
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            setting.value = value
            if description:
                setting.description = description
        else:
            setting = SystemSetting(key=key, value=value, description=description)
            db.session.add(setting)
        return setting
    
    @staticmethod
    def set_settings(settings_dict):
        """
        批量设置配置项
        
        Args:
            settings_dict: 字典，键为设置键，值为设置值
        """
        for key, value in settings_dict.items():
            SettingsService.set_setting(key, value)
        db.session.commit()
    
    @staticmethod
    def get_site_info():
        """
        获取网站基本信息
        
        Returns:
            包含网站基本信息的字典
        """
        return {
            'site_name': SettingsService.get_setting('site_name', '日用产品批发零售系统'),
            'site_title': SettingsService.get_setting('site_title', '日用产品批发零售系统'),
            'company_name': SettingsService.get_setting('company_name', ''),
            'company_phone': SettingsService.get_setting('company_phone', ''),
            'company_email': SettingsService.get_setting('company_email', ''),
            'company_address': SettingsService.get_setting('company_address', ''),
            'copyright': SettingsService.get_setting('copyright', f'{SettingsService.get_setting("company_name", "日用产品批发零售系统")}'),
            'icp': SettingsService.get_setting('icp', ''),
        }
    
    @staticmethod
    def get_notification_settings():
        """
        获取通知设置
        
        Returns:
            包含通知设置的字典
        """
        return {
            'email_enabled': SettingsService.get_setting('email_enabled', 'false') == 'true',
            'sms_enabled': SettingsService.get_setting('sms_enabled', 'false') == 'true',
            'notification_emails': SettingsService.get_setting('notification_emails', ''),
            'admin_phones': SettingsService.get_setting('admin_phones', ''),
        }
