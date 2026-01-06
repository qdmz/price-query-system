# 日用产品批发零售系统

一个基于 Python Flask 的产品价格查询和订单管理系统，支持产品查询、订单管理、批量导入、邮件/短信通知等功能。

## 功能特性

### 前台功能
- 产品查询：支持按货号、条码、产品名称、型号等多种方式搜索
- 产品详情：展示产品图片、规格、价格等详细信息
- 订单创建：购物车功能，支持批量下单
- 零售/批发价格：自动根据数量选择零售价或批发价

### 后台管理
- 产品管理：增删改查产品信息
- 图片管理：支持上传图片或从网络URL自动下载
- 批量导入：支持Excel批量导入产品数据
- 订单管理：查看和处理订单
- 分类管理：产品分类管理
- 系统设置：邮件/短信通知配置、公司信息等
- 数据统计：产品、订单、销售统计

### 通知系统
- 邮件通知：新订单自动发送邮件通知
- 短信通知：新订单自动发送短信通知
- 通知状态跟踪

## 技术栈

- **后端**: Python 3.11, Flask
- **数据库**: PostgreSQL 15
- **前端**: Bootstrap 5, jQuery
- **部署**: Docker, Docker Compose, Nginx
- **任务队列**: Celery（可扩展）

## 快速开始

### 方式一：使用 Docker Compose（推荐）

1. 克隆项目
```bash
git clone <repository-url>
cd price_query_system
```

2. 配置环境变量
```bash
cp .env.example .env
# 编辑 .env 文件，修改必要的配置
```

3. 启动服务
```bash
docker-compose up -d
```

4. 访问应用
- 前台页面: http://localhost:5000
- 后台管理: http://localhost:5000/admin/dashboard
- 默认管理员账号: admin / admin123

### 数据初始化

系统在首次启动时会自动执行数据初始化，包括：
- 创建默认管理员账户
- 创建默认系统设置
- 为产品添加网络图片（使用 Unsplash 免费图库）
- 生成 6 个月的测试订单数据（用于测试数据统计功能）

**手动运行初始化**（如需重新初始化数据）：

```bash
# 在 Docker 容器中运行
docker-compose exec web python init_data.py

# 或本地运行
python init_data.py
```

**重新部署并重新初始化**：

```bash
# 停止并删除容器和卷
docker-compose down -v

# 重新构建并启动（会自动触发首次初始化）
docker-compose up -d --build
```

#### 数据初始化详细说明

系统使用 `.initialized` 标志文件来判断是否为首次启动。初始化流程包括：

1. **等待数据库就绪**：确保 PostgreSQL 数据库连接正常
2. **创建默认管理员**：用户名 `admin`，密码 `admin123`
3. **创建系统设置**：默认公司名称、通知设置等
4. **添加产品图片**：
   - 从 Unsplash 免费图库下载网络图片
   - 为每个产品自动添加 3 张相关图片
   - 图片按产品名称关键词匹配（如"牙膏"、"洗发水"等）
5. **生成测试订单**：
   - 生成过去 6 个月的订单数据
   - 每月订单数量递增（5-40单不等）
   - 订单包含随机客户信息、产品组合和状态
   - 用于测试数据统计和月报功能

#### 仅重新初始化产品图片或订单数据

如果只想重新初始化产品图片或订单数据，而不重置整个系统，可以使用以下脚本：

```bash
# 仅添加产品图片
docker-compose exec web python add_product_images.py

# 仅生成订单数据
docker-compose exec web python generate_multi_month_orders.py
```

#### 初始化数据内容概览

- **产品图片**：54张网络图片（15个产品 × 3张/产品）
- **测试订单**：约 200 个订单，分布在 6 个月内
- **订单状态分布**：
  - 70% 已完成
  - 20% 已确认
  - 10% 已取消

### 方式二：本地开发

1. 安装依赖
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
```

2. 配置数据库
```bash
# 确保已安装 PostgreSQL
# 创建数据库
createdb price_query_db

# 配置环境变量
export DATABASE_URL=postgresql://postgres:yourpassword@localhost:5432/price_query_db
```

3. 初始化数据库
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

4. 启动应用
```bash
python app.py
```

## 目录结构

```
price_query_system/
├── app/                          # 应用主目录
│   ├── __init__.py              # 应用初始化
│   ├── models.py                 # 数据库模型
│   ├── routes/                   # 路由
│   │   ├── main.py              # 前台路由
│   │   ├── auth.py              # 认证路由
│   │   ├── api.py               # API路由
│   │   └── admin.py             # 后台管理路由
│   ├── services/                 # 业务逻辑
│   │   ├── init_service.py      # 初始化服务
│   │   ├── product_service.py   # 产品服务
│   │   ├── order_service.py     # 订单服务
│   │   └── notification_service.py  # 通知服务
│   ├── templates/                # 模板
│   │   ├── common/              # 通用模板
│   │   ├── auth/                # 认证模板
│   │   ├── admin/               # 后台模板
│   │   └── *.html               # 前台模板
│   └── static/                   # 静态文件
│       ├── css/
│       ├── js/
│       └── uploads/             # 上传文件
│           ├── products/        # 产品图片
│           └── orders/
├── config/                       # 配置
│   ├── __init__.py
│   └── config.py                # 配置文件
├── tests/                        # 测试
├── Dockerfile                    # Docker镜像
├── docker-compose.yml            # Docker编排
├── nginx.conf                    # Nginx配置
├── requirements.txt              # Python依赖
├── app.py                        # 应用入口
└── README.md                     # 说明文档
```

## API接口文档

### 产品相关

#### 搜索产品
```
GET /api/products/search
参数:
  - q: 搜索关键词（货号、条码、产品名称、型号）
  - category_id: 分类ID（可选）
  - page: 页码（默认1）

返回:
{
  "success": true,
  "products": [...],
  "total": 100,
  "pages": 5,
  "current_page": 1
}
```

#### 获取产品详情
```
GET /api/products/{product_id}
```

### 订单相关

#### 创建订单
```
POST /api/orders
Content-Type: application/json

{
  "customer_name": "张三",
  "customer_phone": "13800138000",
  "customer_email": "test@example.com",
  "customer_address": "北京市xxx",
  "notes": "备注信息",
  "items": [
    {
      "product_id": 1,
      "quantity": 10
    }
  ]
}
```

#### 获取订单详情
```
GET /api/orders/{order_no}
```

### 统计接口

#### 获取统计数据
```
GET /api/statistics
```

## 批量导入

系统支持通过Excel批量导入产品数据。

### Excel格式要求

Excel文件必须包含以下列：

| 列名 | 必填 | 说明 |
|------|------|------|
| 货号 | 是 | 产品唯一编号 |
| 条码 | 否 | 产品条形码 |
| 产品名称 | 是 | 产品名称 |
| 型号 | 否 | 产品型号 |
| 规格 | 否 | 产品规格 |
| 单位 | 否 | 计量单位，默认"件" |
| 零售价 | 否 | 零售价格，默认0 |
| 批发价 | 否 | 批发价格，默认0 |
| 批发最小数量 | 否 | 批发起订数量，默认1 |
| 库存 | 否 | 库存数量，默认0 |
| 描述 | 否 | 产品描述 |

### 导入步骤

1. 登录后台管理系统
2. 进入"批量导入"页面
3. 下载示例Excel文件
4. 按照格式要求填写产品信息
5. 上传Excel文件
6. 查看导入结果

## 邮件/短信配置

### 邮件通知配置

在 `.env` 文件中配置：

```env
MAIL_SERVER=smtp.example.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@example.com
MAIL_PASSWORD=your-email-password
MAIL_DEFAULT_SENDER=noreply@example.com
```

在后台"系统设置"页面中：
1. 启用邮件通知
2. 添加接收通知的邮箱列表

### 短信通知配置

在 `.env` 文件中配置：

```env
SMS_API_URL=https://api.example.com/sms
SMS_API_KEY=your-sms-api-key
```

在后台"系统设置"页面中：
1. 启用短信通知
2. 添加接收通知的手机号列表

## 生产环境部署

### 使用 Docker Compose

```bash
# 构建并启动所有服务
docker-compose -f docker-compose.yml --profile production up -d

# 查看日志
docker-compose logs -f web

# 停止服务
docker-compose down
```

### 手动部署

1. 配置 Nginx 反向代理
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    location /static/ {
        alias /path/to/app/static/;
    }
}
```

2. 使用 Gunicorn 启动应用
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. 配置 Supervisor 或 Systemd 守护进程

### 环境变量

生产环境必须配置以下环境变量：

```env
SECRET_KEY=<随机字符串>
DATABASE_URL=postgresql://user:password@host:port/database
FLASK_ENV=production
```

## 数据备份

### 备份数据库

```bash
docker exec price_query_db pg_dump -U postgres price_query_db > backup.sql
```

### 恢复数据库

```bash
docker exec -i price_query_db psql -U postgres price_query_db < backup.sql
```

## 常见问题

### 1. 数据库连接失败

检查数据库是否正常运行：
```bash
docker-compose ps db
```

检查数据库连接配置：
```bash
docker-compose logs web | grep database
```

### 2. 上传图片失败

检查上传目录权限：
```bash
docker exec price_query_web ls -la /app/app/static/uploads/
```

### 3. 邮件发送失败

检查邮件配置是否正确，查看应用日志：
```bash
docker-compose logs web | grep mail
```

## 安全建议

1. 修改默认管理员密码
2. 使用强密码作为 `SECRET_KEY`
3. 启用 HTTPS
4. 定期备份数据
5. 限制后台管理访问IP
6. 使用环境变量存储敏感信息

## 开发说明

### 运行测试

```bash
pytest tests/
```

### 代码格式化

```bash
black app/
flake8 app/
```

## 许可证

MIT License

## 联系方式

如有问题或建议，请联系：
- 邮箱: support@example.com
- 官网: https://www.example.com
