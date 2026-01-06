# 部署与数据初始化指南

本文档详细说明如何部署日用产品批发零售系统，并初始化测试数据（产品图片和多个月份的订单数据）。

## 目录

- [首次部署](#首次部署)
- [数据初始化](#数据初始化)
- [重新部署](#重新部署)
- [数据管理](#数据管理)
- [故障排除](#故障排除)

## 首次部署

### 1. 准备工作

确保已安装以下软件：
- Docker 20.10+
- Docker Compose 2.0+

### 2. 克隆项目

```bash
git clone <repository-url>
cd price_query_system
```

### 3. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，修改必要的配置项：

```env
# 数据库配置
DATABASE_URL=postgresql://postgres:yourpassword@db:5432/price_query_db
POSTGRES_DB=price_query_db
POSTGRES_USER=postgres
POSTGRES_PASSWORD=yourpassword

# Flask 配置
FLASK_ENV=production
SECRET_KEY=your-secret-key-here

# 管理员账户
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
ADMIN_EMAIL=admin@example.com

# 邮件配置（可选）
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-email-password

# 短信配置（可选）
SMS_API_KEY=your-sms-api-key
SMS_API_URL=https://sms-api.example.com/send

# 对象存储配置（可选）
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_BUCKET_NAME=your-bucket
S3_ENDPOINT=https://s3.example.com
```

### 4. 启动服务

```bash
docker-compose up -d
```

系统会自动执行以下操作：
1. 创建并启动 PostgreSQL 数据库容器
2. 创建并启动 Flask 应用容器
3. 创建并启动 Nginx 容器
4. 首次启动时自动初始化数据

### 5. 验证部署

```bash
# 查看容器状态
docker-compose ps

# 查看应用日志
docker-compose logs -f web

# 测试访问
curl http://localhost:5000
```

### 6. 访问应用

- 前台页面: http://localhost:5000
- 后台管理: http://localhost:5000/admin/dashboard
- 默认管理员账号: `admin` / `admin123`

## 数据初始化

### 自动初始化

系统在首次启动时会自动执行数据初始化。初始化过程由 `docker-entrypoint.sh` 脚本控制，流程如下：

1. 检测是否存在 `.initialized` 标志文件
2. 如果不存在，等待数据库就绪
3. 运行 `init_data.py` 初始化脚本
4. 创建 `.initialized` 标志文件
5. 启动应用服务

### 初始化数据内容

`init_data.py` 脚本会自动执行以下初始化操作：

#### 1. 创建默认管理员

- 用户名: `admin`
- 密码: `admin123`
- 邮箱: `admin@example.com`
- 角色: 管理员

#### 2. 创建默认系统设置

- 邮件通知: 默认关闭
- 短信通知: 默认关闭
- 公司名称: 日用产品批发零售系统
- 其他基本配置

#### 3. 添加产品网络图片

系统会为每个产品自动添加 3 张网络图片，来源为 Unsplash 免费图库：

- **牙膏**: 3张
- **洗发水**: 3张
- **沐浴露**: 3张
- **洗衣液**: 3张
- **洗洁精**: 3张
- **拖把**: 3张
- **扫帚**: 3张
- **毛巾**: 3张
- **水杯**: 3张
- **菜板**: 3张
- **餐具**: 3张
- **湿巾**: 3张

共计: **54张图片**

#### 4. 生成测试订单数据

系统会生成过去 6 个月的测试订单数据：

- **第1个月（最早）**: 5-10个订单
- **第2个月**: 10-15个订单
- **第3个月**: 15-20个订单
- **第4个月**: 20-25个订单
- **第5个月**: 25-30个订单
- **第6个月（最近）**: 30-40个订单

共计: **约200个订单**

订单状态分布：
- 70% 已完成
- 20% 已确认
- 10% 已取消

订单数据包括：
- 随机客户姓名（50个中国姓名）
- 随机电话号码
- 随机收货地址
- 随机产品组合（2-5个产品）
- 随机下单时间（均匀分布在每月内）

### 手动运行初始化

如果需要在系统运行后重新初始化数据，可以手动运行初始化脚本：

```bash
# 在 Docker 容器中运行
docker-compose exec web python init_data.py

# 或本地运行
python init_data.py
```

### 单独初始化特定数据

#### 仅初始化产品图片

```bash
# 在 Docker 容器中运行
docker-compose exec web python add_product_images.py

# 或本地运行
python add_product_images.py
```

#### 仅生成订单数据

```bash
# 在 Docker 容器中运行
docker-compose exec web python generate_multi_month_orders.py

# 或本地运行
python generate_multi_month_orders.py
```

## 重新部署

### 完全重新部署（删除所有数据）

```bash
# 停止并删除容器和数据卷
docker-compose down -v

# 重新构建并启动（会自动触发首次初始化）
docker-compose up -d --build

# 查看初始化日志
docker-compose logs -f web
```

### 仅更新代码（保留数据）

```bash
# 拉取最新代码
git pull

# 重新构建并启动（不会重新初始化数据）
docker-compose up -d --build

# 查看日志
docker-compose logs -f web
```

### 强制重新初始化数据

如果需要强制重新初始化数据（保留代码，重置数据）：

```bash
# 进入容器
docker-compose exec web bash

# 删除初始化标志文件
rm -f /app/.initialized

# 运行初始化脚本
python init_data.py

# 退出容器
exit

# 重启容器
docker-compose restart web
```

## 数据管理

### 查看数据状态

```bash
# 连接到数据库
docker-compose exec db psql -U postgres -d price_query_db

# 查看产品数量
SELECT COUNT(*) FROM products;

# 查看产品图片数量
SELECT COUNT(*) FROM product_images;

# 查看订单数量
SELECT COUNT(*) FROM orders;

# 查看各月订单统计
SELECT
    EXTRACT(YEAR FROM created_at) AS year,
    EXTRACT(MONTH FROM created_at) AS month,
    COUNT(*) AS count,
    SUM(total_amount) AS total_amount
FROM orders
GROUP BY year, month
ORDER BY year, month;

# 退出数据库
\q
```

### 导出数据

```bash
# 导出数据库
docker-compose exec db pg_dump -U postgres price_query_db > backup.sql

# 导出产品图片（假设存储在容器内）
docker cp web:/app/app/static/uploads/products ./backups/products
```

### 导入数据

```bash
# 导入数据库
docker-compose exec -T db psql -U postgres price_query_db < backup.sql

# 导入产品图片
docker cp ./backups/products web:/app/app/static/uploads/
```

### 清空测试数据

```bash
# 进入容器
docker-compose exec web python

# 在 Python REPL 中执行
from app import create_app, db
from app.models import Order, OrderItem, ProductImage

app = create_app()
with app.app_context():
    # 删除所有订单和订单项
    OrderItem.query.delete()
    Order.query.delete()
    # 删除所有产品图片
    ProductImage.query.delete()
    # 提交更改
    db.session.commit()

# 退出 Python REPL
exit()
```

## 故障排除

### 初始化失败

**问题**: 首次启动后数据未初始化

**解决方案**:

1. 查看容器日志
```bash
docker-compose logs web
```

2. 手动运行初始化脚本
```bash
docker-compose exec web python init_data.py
```

3. 检查数据库连接
```bash
docker-compose exec web python -c "from app import create_app; app = create_app(); print('Database connected')"
```

### 图片下载失败

**问题**: 产品图片下载失败

**解决方案**:

1. 检查网络连接
```bash
docker-compose exec web ping -c 3 images.unsplash.com
```

2. 检查磁盘空间
```bash
docker exec web df -h
```

3. 手动重新添加图片
```bash
docker-compose exec web python add_product_images.py
```

### 订单生成失败

**问题**: 订单数据生成失败

**解决方案**:

1. 检查产品数据是否存在
```bash
docker-compose exec db psql -U postgres -d price_query_db -c "SELECT COUNT(*) FROM products;"
```

2. 查看错误日志
```bash
docker-compose logs web | grep -i error
```

3. 手动重新生成订单
```bash
docker-compose exec web python generate_multi_month_orders.py
```

### 数据持久化问题

**问题**: 重启容器后数据丢失

**解决方案**:

1. 检查 Docker 卷是否正常创建
```bash
docker volume ls
docker volume inspect price_query_system_db_data
```

2. 确保 `docker-compose.yml` 中正确配置了卷挂载
```yaml
volumes:
  db_data:
    driver: local
```

3. 如果数据丢失，可以从备份恢复
```bash
docker-compose exec -T db psql -U postgres price_query_db < backup.sql
```

## 附录

### 相关文件

- `init_data.py`: 主初始化脚本
- `add_product_images.py`: 产品图片添加脚本
- `generate_multi_month_orders.py`: 订单数据生成脚本
- `docker-entrypoint.sh`: Docker 入口脚本
- `Dockerfile`: Docker 镜像构建文件
- `docker-compose.yml`: Docker Compose 编排文件

### 初始化脚本详解

#### init_data.py

主要功能：
- 整合所有初始化流程
- 调用各个子初始化函数
- 错误处理和日志输出

#### add_product_images.py

主要功能：
- 从 Unsplash 下载网络图片
- 为产品匹配并添加图片
- 支持增量添加（跳过已有图片的产品）

#### generate_multi_month_orders.py

主要功能：
- 生成多个月的订单数据
- 模拟真实订单场景
- 随机分配订单状态和客户信息

### 自定义初始化

如果需要自定义初始化数据，可以修改 `init_data.py` 脚本：

1. 修改默认管理员信息
```python
admin = User(
    username='your_username',
    email='your_email@example.com',
    role='admin'
)
admin.set_password('your_password')
```

2. 修改产品图片 URL
```python
PRODUCT_IMAGES = {
    '产品名称': [
        'https://your-image-url-1.jpg',
        'https://your-image-url-2.jpg',
        'https://your-image-url-3.jpg'
    ]
}
```

3. 修改订单生成参数
```python
# 修改月份数量
for i in range(12):  # 改为12个月

# 修改每月订单数量
base_orders = 10  # 调整基础订单数
num_orders = random.randint(base_orders, base_orders + 10)
```

## 支持

如有问题，请提交 Issue 或联系维护者。
