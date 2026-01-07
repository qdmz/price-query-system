from flask import current_app, render_template_string
from flask_mail import Message
from app.models import db, SystemSetting, Order
import requests

class NotificationService:

    @staticmethod
    def get_setting(key, default=''):
        """获取系统设置"""
        setting = SystemSetting.query.filter_by(key=key).first()
        return setting.value if setting else default

    @staticmethod
    def send_email_notification(order):
        """发送邮件通知"""
        try:
            # 检查邮件是否启用
            enabled = NotificationService.get_setting('MAIL_NOTIFICATION_ENABLED', 'false')
            if enabled != 'true':
                return False

            # 获取邮件配置
            mail_server = NotificationService.get_setting('MAIL_SERVER')
            mail_port = NotificationService.get_setting('MAIL_PORT', '587')
            mail_username = NotificationService.get_setting('MAIL_USERNAME')
            mail_password = NotificationService.get_setting('MAIL_PASSWORD')
            mail_use_tls = NotificationService.get_setting('MAIL_USE_TLS', 'true')
            mail_from = NotificationService.get_setting('MAIL_DEFAULT_SENDER', mail_username)

            if not mail_server or not mail_username:
                print("邮件配置不完整")
                return False

            # 获取通知邮箱列表
            notification_emails = NotificationService.get_setting('ADMIN_EMAIL')
            if not notification_emails:
                return False

            emails = [e.strip() for e in notification_emails.split(',') if e.strip()]
            
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
            
            # 更新邮件配置（从数据库读取）
            from app import mail
            current_app.config['MAIL_SERVER'] = mail_server
            current_app.config['MAIL_PORT'] = int(mail_port)
            current_app.config['MAIL_USERNAME'] = mail_username
            current_app.config['MAIL_PASSWORD'] = mail_password
            current_app.config['MAIL_USE_TLS'] = mail_use_tls.lower() in ['true', '1', 'on']
            current_app.config['MAIL_DEFAULT_SENDER'] = mail_from

            # 发送邮件
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
            enabled = NotificationService.get_setting('SMS_NOTIFICATION_ENABLED', 'false')
            if enabled != 'true':
                return False

            # 获取短信配置
            sms_api_url = NotificationService.get_setting('SMS_API_URL')
            sms_api_key = NotificationService.get_setting('SMS_API_KEY')
            sms_api_secret = NotificationService.get_setting('SMS_API_SECRET')

            if not sms_api_url or not sms_api_key:
                print("短信配置不完整")
                return False

            # 获取管理员手机号
            admin_phone = NotificationService.get_setting('ADMIN_PHONE')
            if not admin_phone:
                return False

            # 构建短信内容
            message = f"新订单通知\n订单号: {order.order_no}\n客户: {order.customer_name}\n电话: {order.customer_phone or '-'}\n金额: ¥{order.total_amount:.2f}\n商品数: {order.total_quantity}"

            # 这里需要根据实际的短信服务商API进行调用
            # 示例代码，需要替换为实际的短信API
            # response = requests.post(
            #     sms_api_url,
            #     json={
            #         'api_key': sms_api_key,
            #         'api_secret': sms_api_secret,
            #         'phones': admin_phone,
            #         'message': message
            #     }
            # )

            print(f"[SMS] 将发送到 {admin_phone}: {message}")
            return True
        except Exception as e:
            print(f"短信发送失败: {str(e)}")
            return False
    
    @staticmethod
    def send_email(to, subject, body):
        """发送单封测试邮件"""
        try:
            from app import mail

            msg = Message(
                subject=subject,
                recipients=[to],
                body=body,
                html=body  # 支持HTML格式
            )

            mail.send(msg)
            return {'success': True, 'message': '邮件发送成功'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def send_sms(to, body):
        """发送单条测试短信"""
        try:
            # 获取短信配置
            sms_api_url = current_app.config.get('SMS_API_URL')
            sms_api_key = current_app.config.get('SMS_API_KEY')
            sms_sign_name = current_app.config.get('SMS_SIGN_NAME', '')

            # 如果配置了短信API，则发送
            if sms_api_url and sms_api_key:
                # 构建带签名的短信内容
                full_message = f"【{sms_sign_name}】{body}" if sms_sign_name else body
                
                # 示例：使用requests发送（需要根据实际API调整）
                # response = requests.post(
                #     sms_api_url,
                #     json={
                #         'api_key': sms_api_key,
                #         'phone': to,
                #         'message': full_message
                #     }
                # )
                # if response.status_code == 200 and response.json().get('code') == 0:
                #     return {'success': True, 'message': '短信发送成功'}
                # else:
                #     return {'success': False, 'message': response.json().get('message', '发送失败')}
                
                print(f"[SMS Test] To: {to}, Message: {full_message}")
                return {'success': True, 'message': '短信发送成功（模拟）'}
            else:
                return {'success': False, 'message': '短信服务未配置，请在config.py中设置SMS_API_URL和SMS_API_KEY'}
        except Exception as e:
            return {'success': False, 'message': str(e)}
    
    @staticmethod
    def notify_new_order(order):
        """发送新订单通知"""
        success = False
        errors = []

        # 发送邮件
        try:
            email_success = NotificationService.send_email_notification(order)
            if email_success:
                success = True
                print("✓ 邮件通知发送成功")
            else:
                errors.append("邮件通知发送失败")
        except Exception as e:
            errors.append(f"邮件通知异常: {str(e)}")

        # 发送短信
        try:
            sms_success = NotificationService.send_sms_notification(order)
            if sms_success:
                success = True
                print("✓ 短信通知发送成功")
            else:
                errors.append("短信通知发送失败")
        except Exception as e:
            errors.append(f"短信通知异常: {str(e)}")

        # 标记为已通知（至少有一个通知成功）
        if success:
            order.notified = True
            db.session.commit()
        elif errors:
            print(f"[通知服务] 所有通知失败: {', '.join(errors)}")

        return success

    @staticmethod
    def send_order_notification(to_email, customer_name, order_no, pending_items, completed_items, cancelled_items):
        """发送订单状态变更通知"""
        try:
            # 获取邮件配置
            mail_server = NotificationService.get_setting('MAIL_SERVER')
            mail_username = NotificationService.get_setting('MAIL_USERNAME')
            mail_password = NotificationService.get_setting('MAIL_PASSWORD')
            mail_port = NotificationService.get_setting('MAIL_PORT', '587')
            mail_use_tls = NotificationService.get_setting('MAIL_USE_TLS', 'true')
            mail_from = NotificationService.get_setting('MAIL_DEFAULT_SENDER', mail_username)

            if not mail_server or not mail_username:
                return False

            # 更新邮件配置
            from app import mail
            current_app.config['MAIL_SERVER'] = mail_server
            current_app.config['MAIL_PORT'] = int(mail_port)
            current_app.config['MAIL_USERNAME'] = mail_username
            current_app.config['MAIL_PASSWORD'] = mail_password
            current_app.config['MAIL_USE_TLS'] = mail_use_tls.lower() in ['true', '1', 'on']
            current_app.config['MAIL_DEFAULT_SENDER'] = mail_from

            # 构建邮件内容
            subject = f"订单状态通知 - {order_no}"

            items_html = ""
            if pending_items:
                items_html += "<h3>待处理商品:</h3><ul>" + "".join(f"<li>{item}</li>" for item in pending_items) + "</ul>"
            if completed_items:
                items_html += "<h3>已完成商品:</h3><ul>" + "".join(f"<li>{item}</li>" for item in completed_items) + "</ul>"
            if cancelled_items:
                items_html += "<h3>已取消商品:</h3><ul>" + "".join(f"<li>{item}</li>" for item in cancelled_items) + "</ul>"

            html_content = f"""
            <html>
            <body style="font-family: Arial, sans-serif;">
                <h2>订单状态通知</h2>
                <p>尊敬的 {customer_name}：</p>
                <p>您的订单 <strong>{order_no}</strong> 状态已更新。</p>
                {items_html}
                <hr>
                <p style="color: #666; font-size: 12px;">此邮件由系统自动发送。</p>
            </body>
            </html>
            """

            msg = Message(
                subject=subject,
                recipients=[to_email],
                html=html_content
            )
            mail.send(msg)

            return True
        except Exception as e:
            print(f"邮件发送失败: {str(e)}")
            return False

    @staticmethod
    def send_sms_notification_test(to_phone, message):
        """发送短信（测试用）"""
        try:
            # 获取短信配置
            sms_api_url = NotificationService.get_setting('SMS_API_URL')
            sms_api_key = NotificationService.get_setting('SMS_API_KEY')
            sms_api_secret = NotificationService.get_setting('SMS_API_SECRET')

            if not sms_api_url or not sms_api_key:
                print("短信配置不完整")
                return False

            print(f"[SMS Test] 将发送到 {to_phone}: {message}")
            # 实际对接短信API
            # response = requests.post(sms_api_url, json={...})
            return True
        except Exception as e:
            print(f"短信发送失败: {str(e)}")
            return False
