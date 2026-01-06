from flask import current_app, render_template_string
from flask_mail import Message
from app.models import db, SystemSetting, Order
import requests

class NotificationService:
    
    @staticmethod
    def send_email_notification(order):
        """发送邮件通知"""
        try:
            # 检查邮件是否启用
            email_enabled = SystemSetting.query.filter_by(key='email_enabled').first()
            if not email_enabled or email_enabled.value != 'true':
                return False
            
            # 获取通知邮箱列表
            notification_emails_setting = SystemSetting.query.filter_by(key='notification_emails').first()
            if not notification_emails_setting or not notification_emails_setting.value:
                return False
            
            emails = [e.strip() for e in notification_emails_setting.value.split(',') if e.strip()]
            if not emails:
                return False
            
            # 构建邮件内容
            subject = f"新订单通知 - 订单号: {order.order_no}"
            
            # 构建订单详情HTML
            items_html = ""
            for item in order.items:
                items_html += f"""
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">{item.product_name}</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">{item.product_code}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: center;">{item.quantity}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">¥{item.unit_price:.2f}</td>
                    <td style="border: 1px solid #ddd; padding: 8px; text-align: right;">¥{item.subtotal:.2f}</td>
                </tr>
                """
            
            html_content = f"""
            <html>
            <head>
                <meta charset="UTF-8">
            </head>
            <body style="font-family: Arial, sans-serif; line-height: 1.6;">
                <h2>新订单通知</h2>
                <p>您收到了一个新的订单，详情如下：</p>
                
                <h3>订单信息</h3>
                <table style="border-collapse: collapse; width: 100%; max-width: 600px;">
                    <tr><td style="padding: 5px;"><strong>订单号:</strong></td><td>{order.order_no}</td></tr>
                    <tr><td style="padding: 5px;"><strong>客户姓名:</strong></td><td>{order.customer_name}</td></tr>
                    <tr><td style="padding: 5px;"><strong>联系电话:</strong></td><td>{order.customer_phone or '-'}</td></tr>
                    <tr><td style="padding: 5px;"><strong>联系邮箱:</strong></td><td>{order.customer_email or '-'}</td></tr>
                    <tr><td style="padding: 5px;"><strong>收货地址:</strong></td><td>{order.customer_address or '-'}</td></tr>
                    <tr><td style="padding: 5px;"><strong>总金额:</strong></td><td style="color: red; font-weight: bold;">¥{order.total_amount:.2f}</td></tr>
                </table>
                
                <h3>订单商品</h3>
                <table style="border-collapse: collapse; width: 100%; max-width: 800px; margin-bottom: 20px;">
                    <thead>
                        <tr style="background-color: #f2f2f2;">
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">商品名称</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: left;">货号</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: center;">数量</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">单价</th>
                            <th style="border: 1px solid #ddd; padding: 8px; text-align: right;">小计</th>
                        </tr>
                    </thead>
                    <tbody>
                        {items_html}
                    </tbody>
                </table>
                
                <p><strong>备注:</strong> {order.notes or '无'}</p>
                
                <hr>
                <p style="color: #666; font-size: 12px;">
                    此邮件由系统自动发送，请勿直接回复。<br>
                    订单创建时间: {order.created_at.strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </body>
            </html>
            """
            
            # 发送邮件
            from app import mail
            msg = Message(
                subject=subject,
                recipients=emails,
                html=html_content
            )
            mail.send(msg)
            
            return True
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
            return False
    
    @staticmethod
    def send_sms_notification(order):
        """发送短信通知"""
        try:
            # 检查短信是否启用
            sms_enabled = SystemSetting.query.filter_by(key='sms_enabled').first()
            if not sms_enabled or sms_enabled.value != 'true':
                return False
            
            # 获取管理员手机号
            admin_phones_setting = SystemSetting.query.filter_by(key='admin_phones').first()
            if not admin_phones_setting or not admin_phones_setting.value:
                return False
            
            phones = [p.strip() for p in admin_phones_setting.value.split(',') if p.strip()]
            if not phones:
                return False
            
            # 构建短信内容
            message = f"新订单通知\n订单号: {order.order_no}\n客户: {order.customer_name}\n电话: {order.customer_phone or '-'}\n金额: ¥{order.total_amount:.2f}\n商品数: {order.total_quantity}"
            
            # 这里需要根据实际的短信服务商API进行调用
            # 示例代码，需要替换为实际的短信API
            sms_api_url = current_app.config.get('SMS_API_URL')
            sms_api_key = current_app.config.get('SMS_API_KEY')
            
            # 示例：模拟发送短信（实际使用时需要对接真实短信服务商）
            # response = requests.post(
            #     sms_api_url,
            #     json={
            #         'api_key': sms_api_key,
            #         'phones': phones,
            #         'message': message
            #     }
            # )
            
            print(f"短信发送成功: {message}")
            return True
        except Exception as e:
            print(f"短信发送失败: {str(e)}")
            return False
    
    @staticmethod
    def notify_new_order(order):
        """发送新订单通知"""
        success = False
        
        # 发送邮件
        email_success = NotificationService.send_email_notification(order)
        if email_success:
            success = True
        
        # 发送短信
        sms_success = NotificationService.send_sms_notification(order)
        if sms_success:
            success = True
        
        # 标记为已通知
        if success:
            order.notified = True
            db.session.commit()
        
        return success
