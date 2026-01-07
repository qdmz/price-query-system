# 通知配置指南

本文档介绍如何配置邮件和短信通知功能，以及如何进行测试。

## 目录
- [邮件通知配置](#邮件通知配置)
- [短信通知配置](#短信通知配置)
- [测试方法](#测试方法)
- [常见问题](#常见问题)

---

## 邮件通知配置

### 1. 配置文件设置

在 `config.py` 文件中添加以下邮件配置：

```python
# 邮件配置
MAIL_SERVER = 'smtp.qq.com'        # SMTP服务器地址
MAIL_PORT = 465                    # SMTP端口
MAIL_USE_SSL = True                # 使用SSL加密
MAIL_USERNAME = 'your_email@qq.com'  # 发件邮箱
MAIL_PASSWORD = 'your_password'    # 邮箱授权码（非登录密码）
MAIL_DEFAULT_SENDER = 'your_email@qq.com'  # 默认发件人
```

### 2. 常用邮箱SMTP配置

#### QQ邮箱
- **SMTP服务器**: smtp.qq.com
- **端口**: 465 (SSL) 或 587 (TLS)
- **加密**: SSL
- **获取授权码方法**:
  1. 登录QQ邮箱网页版
  2. 点击"设置" -> "账户"
  3. 找到"POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务"
  4. 开启"POP3/SMTP服务"或"IMAP/SMTP服务"
  5. 按照提示发送短信验证
  6. 获取授权码（16位字符）
  7. 在配置文件中使用授权码，不是QQ密码

**示例配置**:
```python
MAIL_SERVER = 'smtp.qq.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = '123456789@qq.com'
MAIL_PASSWORD = 'abcdefghijklmnop'  # 授权码
```

#### 163邮箱
- **SMTP服务器**: smtp.163.com
- **端口**: 465 (SSL) 或 994 (SSL)
- **加密**: SSL
- **获取授权码方法**:
  1. 登录163邮箱
  2. 点击"设置" -> "POP3/SMTP/IMAP"
  3. 开启"IMAP/SMTP服务"
  4. 按照提示验证
  5. 获取授权码
  6. 使用授权码配置

**示例配置**:
```python
MAIL_SERVER = 'smtp.163.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'your_email@163.com'
MAIL_PASSWORD = 'your_auth_code'  # 授权码
```

#### Gmail
- **SMTP服务器**: smtp.gmail.com
- **端口**: 465 (SSL) 或 587 (TLS)
- **加密**: SSL
- **获取密码方法**:
  1. 登录Google账户
  2. 进入"安全性"设置
  3. 开启"两步验证"
  4. 生成"应用专用密码"
  5. 使用应用专用密码（16位字符）

**示例配置**:
```python
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_SSL = True
MAIL_USERNAME = 'your_email@gmail.com'
MAIL_PASSWORD = 'abcdefghijklmnop'  # 应用专用密码
```

#### Outlook/Hotmail
- **SMTP服务器**: smtp.office365.com
- **端口**: 587 (TLS)
- **加密**: TLS
- **获取密码方法**:
  1. 如果开启了两步验证，需要生成应用专用密码
  2. 否则使用常规密码

**示例配置**:
```python
MAIL_SERVER = 'smtp.office365.com'
MAIL_PORT = 587
MAIL_USE_SSL = False
MAIL_USE_TLS = True
MAIL_USERNAME = 'your_email@outlook.com'
MAIL_PASSWORD = 'your_password'  # 或应用专用密码
```

### 3. 在后台设置通知邮箱

1. 登录后台管理系统
2. 进入"系统设置" -> "通知设置"
3. 启用"邮件通知"
4. 输入"通知邮箱列表"（多个邮箱用逗号分隔）
5. 点击"保存设置"

---

## 短信通知配置

### 1. 使用阿里云短信服务（推荐）

#### 前置条件
1. 注册阿里云账号
2. 开通短信服务
3. 创建签名和模板
4. 获取AccessKey

#### 配置步骤

**步骤1: 创建签名和模板**

1. 登录阿里云控制台
2. 进入"短信服务"
3. 创建签名（需要审核）
   - 签名名称：如"您的公司名"
   - 适用场景：验证码、通知等
4. 创建短信模板（需要审核）
   - 模板内容示例：`【${签名}】您有新订单：${order_no}，金额：¥${amount}，请及时处理。`
   - 变量说明：order_no（订单号）、amount（金额）

**步骤2: 配置应用**

在 `config.py` 中添加以下配置：

```python
# 阿里云短信配置
SMS_ACCESS_KEY_ID = 'your_access_key_id'
SMS_ACCESS_KEY_SECRET = 'your_access_key_secret'
SMS_SIGN_NAME = '您的公司名'
SMS_TEMPLATE_CODE = 'SMS_123456789'  # 短信模板CODE
```

**步骤3: 安装SDK**

```bash
pip install aliyun-python-sdk-core aliyun-python-sdk-dysmsapi
```

### 2. 使用腾讯云短信服务

#### 前置条件
1. 注册腾讯云账号
2. 开通短信服务
3. 创建签名和模板
4. 获取SecretId和SecretKey

#### 配置步骤

在 `config.py` 中添加以下配置：

```python
# 腾讯云短信配置
SMS_SECRET_ID = 'your_secret_id'
SMS_SECRET_KEY = 'your_secret_key'
SMS_SIGN_NAME = '您的公司名'
SMS_TEMPLATE_ID = '123456'  # 短信模板ID
SMS_SDK_APP_ID = '12345678'  # 短信应用ID
```

### 3. 自定义短信服务商

如果您使用其他短信服务商，可以自定义实现。

创建 `app/services/custom_sms_service.py`:

```python
class CustomSmsService:
    def __init__(self):
        self.api_url = current_app.config.get('SMS_API_URL')
        self.api_key = current_app.config.get('SMS_API_KEY')
        self.sign_name = current_app.config.get('SMS_SIGN_NAME', '')
    
    def send_sms(self, phone_number, message):
        """发送短信"""
        # 实现您的短信发送逻辑
        import requests
        
        params = {
            'phone': phone_number,
            'message': f'【{self.sign_name}】{message}',
            'api_key': self.api_key
        }
        
        response = requests.post(self.api_url, json=params)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                return {'success': True, 'message': '发送成功'}
        
        return {'success': False, 'message': '发送失败'}
```

然后在 `config.py` 中配置：

```python
# 自定义短信配置
SMS_API_URL = 'https://your-sms-provider.com/api/send'
SMS_API_KEY = 'your_api_key'
SMS_SIGN_NAME = '您的公司名'
```

### 4. 在后台设置通知手机号

1. 登录后台管理系统
2. 进入"系统设置" -> "通知设置"
3. 启用"短信通知"
4. 输入"管理员手机号"（多个手机号用逗号分隔）
5. 点击"保存设置"

---

## 测试方法

### 1. 访问测试页面

1. 登录后台管理系统
2. 点击左侧菜单"通知测试"
3. 进入测试页面

### 2. 测试邮件通知

1. 在"邮件通知测试"区域填写：
   - 收件人邮箱：填写您要测试的邮箱地址
   - 邮件主题：填写测试主题，如"测试邮件"
   - 邮件内容：填写测试内容
2. 点击"发送测试邮件"按钮
3. 查看测试结果
4. 检查收件箱是否收到测试邮件

### 3. 测试短信通知

1. 在"短信通知测试"区域填写：
   - 收件人手机号：填写您要测试的手机号
   - 短信内容：填写测试内容（最多70字符）
2. 点击"发送测试短信"按钮
3. 查看测试结果
4. 检查手机是否收到测试短信

### 4. 查看常用邮箱SMTP配置

测试页面底部提供了常用邮箱的SMTP配置参考，包括：
- QQ邮箱
- 163邮箱
- Gmail
- Outlook

---

## 常见问题

### Q1: QQ邮箱发送失败，提示认证错误

**A:** 请确认使用的是"授权码"而不是QQ密码。
- 登录QQ邮箱 -> 设置 -> 账户 -> 开启SMTP服务 -> 获取授权码

### Q2: 163邮箱发送失败

**A:**
1. 确认已开启IMAP/SMTP服务
2. 使用授权码而非密码
3. 检查端口配置是否正确（465 for SSL, 994 for SSL）

### Q3: Gmail发送失败

**A:** Gmail必须使用"应用专用密码"：
1. 开启两步验证
2. 生成应用专用密码
3. 使用应用专用密码配置

### Q4: 邮件发送慢

**A:** 检查网络连接和SMTP服务器响应速度。可以尝试更换邮箱服务商或使用本地SMTP服务器。

### Q5: 短信发送失败，提示签名未通过审核

**A:** 签名需要经过服务商审核，通常需要1-3个工作日。请使用已审核通过的签名。

### Q6: 短信模板审核不通过

**A:** 检查模板内容是否符合规范：
- 不要包含敏感词
- 格式要规范
- 变量使用正确
- 签名正确

### Q7: 收不到测试邮件/短信

**A:**
1. 检查垃圾箱/垃圾邮件
2. 确认配置信息正确
3. 查看测试页面的错误提示
4. 检查服务商配额是否用完
5. 查看系统日志

### Q8: 配置后不生效

**A:**
1. 重启应用：`flask run`
2. 检查配置文件是否正确
3. 确认配置文件被正确加载
4. 查看控制台错误日志

### Q9: FaaS环境如何配置邮件？

**A:** FaaS环境可能限制SMTP端口，建议：
1. 使用支持HTTP API的邮件服务（如SendGrid、Mailgun）
2. 使用Webhook方式发送邮件
3. 使用云函数的邮件集成功能

---

## 安全建议

1. **不要将密码明文存储在代码中**
   - 使用环境变量
   - 使用配置文件（不要提交到Git）
   - 使用密钥管理服务

2. **环境变量配置示例**:
```bash
export MAIL_USERNAME='your_email@example.com'
export MAIL_PASSWORD='your_password_or_auth_code'
```

3. **创建 `.env` 文件**（记得添加到 `.gitignore`）:
```env
MAIL_USERNAME=your_email@example.com
MAIL_PASSWORD=your_password_or_auth_code
```

4. **配置文件使用环境变量**:
```python
import os

MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'default@example.com')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
```

---

## 联系支持

如有其他问题，请联系系统管理员或查看项目文档。
