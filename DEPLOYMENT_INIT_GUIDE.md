# 部署与初始化指南

本文档介绍如何部署系统并初始化测试数据。

## 目录
- [快速开始](#快速开始)
- [初始化测试数据](#初始化测试数据)
- [测试数据说明](#测试数据说明)
- [重新初始化数据](#重新初始化数据)
- [Docker部署](#docker部署)

---

## 快速开始

### 1. 环境准备

确保已安装以下软件：
- Python 3.11+
- PostgreSQL 15+（生产环境）或 SQLite（开发环境）
- Git

### 2. 克隆项目

```bash
git clone <your-repo-url>
cd <project-directory>
```

### 3. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4. 配置环境变量

创建 `.env` 文件（开发环境可选）：

```env
SECRET_KEY=your-secret-key-change-in-production
DATABASE_URL=sqlite:///price_query.db

# 邮件配置（可选）
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=your_email@qq.com
MAIL_PASSWORD=your_auth_code
```

### 5. 启动应用

```bash
# 开发环境
flask run --port=5000

# 或使用Python
python -m flask run --port=5000
```

应用启动后会自动初始化测试数据。

---

## 初始化测试数据

系统会在首次启动时自动初始化以下测试数据：

### 自动初始化内容

1. **管理员账户**
   - 用户名：`admin`
   - 密码：`admin123`
   - 邮箱：`admin@example.com`

2. **系统设置**
   - 网站名称：日用产品批发零售系统
   - 联系电话：400-888-8888
   - 联系邮箱：service@example.com
   - 公司地址：北京市朝阳区XXX街道XXX号
   - 版权信息和ICP备案号

3. **产品分类**（5个）
   - 个人护理
   - 清洁用品
   - 纸品湿巾
   - 厨房用品
   - 家居纺织

4. **测试产品**（15个）
   - 每个产品包含详细的产品信息
   - 每个产品配有1-2张网络图片（来自Unsplash）
   - 包含零售价和批发价
   - 库存数量合理分配

5. **测试订单**（4个）
   - 不同状态的订单：待处理、已确认、已发货、已完成
   - 包含多个商品的订单项
   - 模拟真实客户信息

---

## 测试数据说明

### 产品图片说明

初始化的产品图片使用网络URL（Unsplash），优点：
- 无需下载和存储图片文件
- 图片质量高，视觉效果好
- 部署后立即可以看到完整效果

图片示例：
```
https://images.unsplash.com/photo-1556228453-efd6c1ff04f6?w=400&h=400&fit=crop
```

### 测试账户

| 用户名 | 密码 | 角色 | 邮箱 |
|--------|------|------|------|
| admin | admin123 | 管理员 | admin@example.com |

**重要提示：** 部署后请立即修改默认密码！

---

## 重新初始化数据

### 方法一：使用初始化脚本（推荐）

```bash
# 重新初始化所有数据（会删除现有数据）
python scripts/init_data.py --force

# 只初始化缺失的数据（不删除现有数据）
python scripts/init_data.py
```

### 方法二：删除数据库文件

开发环境（SQLite）：

```bash
# 删除数据库文件
rm price_query.db

# 重启应用，系统会自动创建新的数据库并初始化测试数据
flask run --port=5000
```

生产环境（PostgreSQL）：

```bash
# 进入PostgreSQL
psql -U postgres -d price_query_db

# 删除所有表
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

# 退出
\q

# 重启应用
flask run --port=5000
```

---

## Docker部署

### 1. 构建镜像

```bash
# 构建Docker镜像
docker build -t price-query-system .
```

### 2. 运行容器

开发环境：

```bash
docker run -d \
  --name price-query \
  -p 5000:5000 \
  -e SECRET_KEY=your-secret-key \
  -e DATABASE_URL=postgresql://postgres:postgres@postgres:5432/price_query_db \
  price-query-system
```

生产环境（使用docker-compose）：

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 3. 数据持久化

使用docker-compose会自动创建数据卷，数据会持久化保存。

---

## 环境变量配置

### 开发环境

在 `.env` 文件中配置：

```env
# 应用配置
FLASK_ENV=development
FLASK_DEBUG=1
SECRET_KEY=dev-secret-key

# 数据库配置（开发环境使用SQLite）
# DATABASE_URL=sqlite:///price_query.db

# 邮件配置（可选）
MAIL_SERVER=smtp.qq.com
MAIL_PORT=465
MAIL_USE_SSL=True
MAIL_USERNAME=your_email@qq.com
MAIL_PASSWORD=your_auth_code
```

### 生产环境

通过环境变量或配置文件设置：

```bash
export FLASK_ENV=production
export SECRET_KEY=$(openssl rand -hex 32)
export DATABASE_URL=postgresql://user:password@host:5432/dbname

# 邮件配置
export MAIL_SERVER=smtp.qq.com
export MAIL_PORT=465
export MAIL_USE_SSL=True
export MAIL_USERNAME=your_email@qq.com
export MAIL_PASSWORD=your_auth_code
```

---

## 常见问题

### Q1: 如何查看初始化的数据？

A: 访问以下页面查看初始化的数据：
- 产品列表：http://localhost:5000/admin/products
- 订单列表：http://localhost:5000/admin/orders
- 分类列表：http://localhost:5000/admin/categories
- 系统设置：http://localhost:5000/admin/settings

### Q2: 产品图片无法显示怎么办？

A: 检查以下几点：
1. 确认网络连接正常（使用的是Unsplash网络图片）
2. 检查图片URL是否正确
3. 如果无法访问外网，可以：
   - 下载图片到本地
   - 在产品管理中上传本地图片
   - 使用占位图片（`app/static/images/product-placeholder.jpg`）

### Q3: 如何修改默认管理员密码？

A: 部署后请立即修改密码：

1. 登录后台：http://localhost:5000/admin
2. 点击右上角用户名 → 修改密码
3. 输入新密码并保存

或在命令行修改：

```bash
python -c "from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); admin = User.query.filter_by(username='admin').first(); admin.set_password('new_password'); db.session.commit();"
```

### Q4: 如何添加更多测试数据？

A: 有以下几种方法：

1. **使用后台管理界面**：
   - 手动添加产品、订单等

2. **修改初始化脚本**：
   - 编辑 `app/services/init_service.py`
   - 在 `products_data` 和 `orders_data` 中添加更多数据
   - 运行重新初始化命令

3. **批量导入**：
   - 使用Excel批量导入产品
   - 访问：http://localhost:5000/admin/products_import

### Q5: 生产环境需要删除测试数据吗？

A: 建议删除测试数据，使用生产数据：

```bash
# 方法1：使用初始化脚本清空数据
python scripts/init_data.py --force

# 然后在后台手动添加真实数据
```

或者在初始化脚本中注释掉测试数据部分。

### Q6: 数据库文件位置？

A:
- 开发环境（SQLite）：项目根目录 `price_query.db`
- 生产环境：PostgreSQL数据库服务器
- Docker环境：Docker数据卷

### Q7: 如何备份数据？

A: 开发环境：

```bash
# 备份SQLite数据库
cp price_query.db price_query.db.backup
```

生产环境（PostgreSQL）：

```bash
# 备份PostgreSQL数据库
pg_dump -U postgres price_query_db > backup.sql

# 恢复
psql -U postgres price_query_db < backup.sql
```

---

## 安全建议

1. **修改默认密码**：部署后立即修改admin密码
2. **使用强SECRET_KEY**：生产环境使用随机生成的密钥
3. **启用HTTPS**：生产环境使用SSL证书
4. **定期备份**：定期备份数据库
5. **限制访问**：限制后台管理访问IP
6. **使用环境变量**：敏感信息使用环境变量，不要硬编码

---

## 下一步

初始化完成后，可以：

1. 访问前台查看产品：http://localhost:5000/
2. 登录后台管理数据：http://localhost:5000/admin（admin/admin123）
3. 配置邮件和短信通知：http://localhost:5000/admin/notification-test
4. 测试产品搜索和订单创建功能
5. 查看数据统计：http://localhost:5000/admin/statistics

---

## 技术支持

如有问题，请查看：
- 项目README.md
- 配置指南：NOTIFICATION_CONFIG_GUIDE.md
- Docker文档（如使用Docker部署）
