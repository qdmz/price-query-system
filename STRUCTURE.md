# 项目结构总览

## 目录树

```
price_query_system/
├── app/                                    # 应用主目录
│   ├── __init__.py                         # Flask应用工厂函数
│   ├── models.py                           # SQLAlchemy数据模型
│   ├── app.py                              # 应用入口
│   │
│   ├── routes/                             # 路由控制器
│   │   ├── __init__.py
│   │   ├── main.py                         # 前台路由（产品查询、购物车、订单）
│   │   ├── auth.py                         # 认证路由（登录、登出、修改密码）
│   │   ├── api.py                          # RESTful API接口
│   │   └── admin.py                        # 后台管理路由
│   │
│   ├── services/                           # 业务逻辑服务层
│   │   ├── __init__.py
│   │   ├── init_service.py                 # 系统初始化服务
│   │   ├── product_service.py              # 产品业务逻辑
│   │   ├── order_service.py                # 订单业务逻辑
│   │   └── notification_service.py         # 通知服务（邮件/短信）
│   │
│   ├── templates/                          # HTML模板
│   │   │
│   │   ├── common/                          # 通用模板
│   │   │   └── base.html                  # 前台基础模板
│   │   │
│   │   ├── auth/                            # 认证相关模板
│   │   │   ├── login.html                  # 登录页面
│   │   │   └── change_password.html        # 修改密码
│   │   │
│   │   ├── admin/                           # 后台管理模板
│   │   │   ├── base.html                  # 后台基础模板（带侧边栏）
│   │   │   ├── dashboard.html              # 仪表盘
│   │   │   ├── products.html               # 产品列表
│   │   │   ├── product_form.html           # 新增/编辑产品
│   │   │   ├── products_import.html        # 批量导入
│   │   │   ├── orders.html                 # 订单列表
│   │   │   ├── order_detail.html           # 订单详情
│   │   │   ├── categories.html             # 分类管理
│   │   │   └── settings.html               # 系统设置
│   │   │
│   │   ├── index.html                      # 前台首页（产品查询）
│   │   ├── order.html                      # 订单创建页面
│   │   └── order_success.html              # 订单成功页面
│   │
│   └── static/                             # 静态文件
│       ├── css/                            # 自定义CSS
│       ├── js/                             # 自定义JavaScript
│       └── uploads/                         # 上传文件目录
│           ├── products/                   # 产品图片
│           └── orders/                      # 订单文件
│
├── config/                                 # 配置目录
│   ├── __init__.py
│   └── config.py                           # 应用配置（数据库、邮件、上传等）
│
├── tests/                                  # 测试目录
│   └── __init__.py
│
├── Dockerfile                              # Docker镜像构建文件
├── docker-compose.yml                      # Docker编排文件
├── nginx.conf                              # Nginx配置文件
├── .dockerignore                           # Docker忽略文件
├── .env.example                            # 环境变量示例
├── requirements.txt                        # Python依赖包
├── start.sh                                # Linux/macOS启动脚本
├── start.bat                               # Windows启动脚本
├── app.py                                  # 应用启动入口
├── README.md                               # 项目说明文档
├── DEPLOY.md                               # 部署指南
└── VERIFICATION.md                         # 验证清单
```

## 文件说明

### 核心应用文件

| 文件 | 说明 |
|------|------|
| `app/__init__.py` | Flask应用工厂函数，初始化扩展、注册蓝图 |
| `app/models.py` | 所有数据库模型定义 |
| `app.py` | 应用启动入口 |

### 路由文件

| 文件 | 说明 | 主要功能 |
|------|------|----------|
| `routes/main.py` | 前台路由 | 产品查询、产品详情、购物车、订单 |
| `routes/auth.py` | 认证路由 | 登录、登出、修改密码 |
| `routes/api.py` | API路由 | RESTful API接口 |
| `routes/admin.py` | 后台路由 | 产品、订单、分类、设置管理 |

### 服务文件

| 文件 | 说明 | 主要功能 |
|------|------|----------|
| `services/init_service.py` | 初始化服务 | 创建默认管理员和系统设置 |
| `services/product_service.py` | 产品服务 | 产品CRUD、图片上传、批量导入 |
| `services/order_service.py` | 订单服务 | 订单创建、状态更新、统计 |
| `services/notification_service.py` | 通知服务 | 邮件通知、短信通知 |

### 模板文件

| 模板类型 | 说明 |
|----------|------|
| `common/base.html` | 前台基础模板（导航栏、页脚） |
| `admin/base.html` | 后台基础模板（侧边栏导航） |
| `auth/` | 认证相关页面 |
| `admin/` | 后台管理页面 |
| `index.html` | 前台首页（产品查询） |
| `order.html` | 订单创建页面 |
| `order_success.html` | 订单成功页面 |

### 配置文件

| 文件 | 说明 |
|------|------|
| `config/config.py` | 应用配置类（开发/生产/测试） |
| `.env.example` | 环境变量模板 |
| `nginx.conf` | Nginx反向代理配置 |

### 部署文件

| 文件 | 说明 |
|------|------|
| `Dockerfile` | Docker镜像构建配置 |
| `docker-compose.yml` | Docker服务编排配置 |
| `start.sh` | Linux/macOS启动脚本 |
| `start.bat` | Windows启动脚本 |
| `.dockerignore` | Docker构建忽略文件 |

### 文档文件

| 文件 | 说明 |
|------|------|
| `README.md` | 项目概述、功能介绍、快速开始 |
| `DEPLOY.md` | 详细部署指南 |
| `VERIFICATION.md` | 功能验证清单 |

## 数据模型

### 核心表

| 表名 | 说明 | 主要字段 |
|------|------|----------|
| `users` | 用户表 | id, username, email, password_hash, role |
| `categories` | 分类表 | id, name, description, sort_order |
| `products` | 产品表 | id, product_code, barcode, name, model, specification, retail_price, wholesale_price, stock |
| `product_images` | 产品图片表 | id, product_id, image_url, is_primary, sort_order |
| `orders` | 订单表 | id, order_no, customer_name, customer_phone, total_amount, status |
| `order_items` | 订单明细表 | id, order_id, product_id, quantity, unit_price, subtotal |
| `system_settings` | 系统设置表 | id, key, value, description |

### 关系

- User (1) → Order (N)
- Category (1) → Product (N)
- Product (1) → ProductImage (N)
- Order (1) → OrderItem (N)
- Product (N) → OrderItem (N)

## API接口

### 产品相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/products/search` | GET | 搜索产品 |
| `/api/products/<id>` | GET | 获取产品详情 |

### 订单相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/orders` | POST | 创建订单 |
| `/api/orders/<order_no>` | GET | 获取订单详情 |

### 统计相关

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/statistics` | GET | 获取统计数据 |

## 环境变量

### 必需变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `SECRET_KEY` | Flask密钥 | 自动生成 |
| `DATABASE_URL` | 数据库连接字符串 | SQLite |

### 可选变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `MAIL_SERVER` | SMTP服务器 | smtp.example.com |
| `MAIL_PORT` | SMTP端口 | 587 |
| `MAIL_USERNAME` | 邮箱用户名 | - |
| `MAIL_PASSWORD` | 邮箱密码 | - |
| `SMS_API_URL` | 短信API地址 | - |
| `SMS_API_KEY` | 短信API密钥 | - |
| `ADMIN_USERNAME` | 管理员用户名 | admin |
| `ADMIN_PASSWORD` | 管理员密码 | admin123 |
| `ADMIN_EMAIL` | 管理员邮箱 | admin@example.com |

## 默认账户

| 用户名 | 密码 | 角色 | 说明 |
|--------|------|------|------|
| admin | admin123 | admin | 系统管理员 |

**重要**: 首次登录后请立即修改默认密码！

## 端口说明

| 端口 | 服务 | 说明 |
|------|------|------|
| 5000 | Flask应用 | Web服务主端口 |
| 5432 | PostgreSQL | 数据库端口（Docker） |
| 80 | Nginx | HTTP反向代理（生产环境） |

## 技术栈

### 后端

- **语言**: Python 3.11+
- **框架**: Flask 3.0.0
- **ORM**: SQLAlchemy
- **认证**: Flask-Login
- **表单**: Flask-WTF
- **邮件**: Flask-Mail
- **迁移**: Flask-Migrate

### 数据库

- **开发**: SQLite
- **生产**: PostgreSQL 15

### 前端

- **框架**: Bootstrap 5.3.0
- **图标**: Bootstrap Icons 1.11.0
- **库**: jQuery 3.7.0

### 部署

- **容器**: Docker
- **编排**: Docker Compose
- **代理**: Nginx Alpine
- **服务器**: Gunicorn 21.2.0

## 扩展开发

### 添加新功能

1. 在 `services/` 目录创建服务文件
2. 在 `routes/` 目录创建路由文件
3. 在 `templates/` 目录创建模板文件
4. 在 `app/__init__.py` 注册蓝图
5. 在 `models.py` 添加数据模型（如需要）

### 添加新API

1. 在 `routes/api.py` 添加路由
2. 在 `services/` 创建业务逻辑
3. 返回JSON格式数据

### 添加新页面

1. 在 `templates/` 创建HTML文件
2. 在 `routes/` 添加路由函数
3. 渲染模板

## 注意事项

1. **安全性**
   - 修改默认管理员密码
   - 使用强SECRET_KEY
   - 启用HTTPS
   - 配置防火墙

2. **性能**
   - 使用分页查询
   - 添加数据库索引
   - 配置静态文件缓存
   - 使用CDN（生产环境）

3. **备份**
   - 定期备份数据库
   - 备份上传文件
   - 备份配置文件

4. **日志**
   - 配置日志级别
   - 日志轮转
   - 监控日志

## 常见问题

**Q: 如何修改默认密码？**
A: 登录后台后，在"修改密码"页面修改，或使用命令行修改。

**Q: 如何配置邮件通知？**
A: 在 `.env` 文件配置SMTP信息，在后台"系统设置"中启用邮件通知。

**Q: 如何批量导入产品？**
A: 准备Excel文件，登录后台，进入"批量导入"页面上传文件。

**Q: 如何备份数据？**
A: 使用 `pg_dump` 命令备份数据库，或使用Docker命令备份数据卷。

---

**最后更新**: 2024-01-06
**版本**: 1.0.0
