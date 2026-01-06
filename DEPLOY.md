# 快速部署指南

## 前置要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 10GB 可用磁盘空间

## 一键启动（推荐）

### Linux/macOS

```bash
# 进入项目目录
cd price_query_system

# 执行启动脚本
./start.sh
```

### Windows

双击 `start.bat` 文件，或在命令行中执行：

```cmd
cd price_query_system
start.bat
```

## 手动部署

### 1. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，修改以下关键配置：
# - SECRET_KEY: 设置为随机字符串
# - DATABASE_URL: 数据库连接字符串（Docker部署保持默认）
# - ADMIN_PASSWORD: 管理员密码
```

### 2. 启动服务

```bash
# 构建镜像并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看应用日志
docker-compose logs -f web
```

### 3. 访问应用

- 前台页面: http://localhost:5000
- 后台管理: http://localhost:5000/admin/dashboard
- 默认账号: admin / admin123

## 数据库初始化

系统首次启动时会自动：
1. 创建数据库表结构
2. 创建默认管理员账户（admin/admin123）
3. 创建默认系统设置

如需手动初始化：

```bash
# 进入容器
docker-compose exec web bash

# 执行初始化脚本
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# 创建管理员
python -c "from app import create_app, db; from app.models import User; app = create_app(); app.app_context().push(); admin = User(username='admin', email='admin@example.com'); admin.set_password('admin123'); db.session.add(admin); db.session.commit()"
```

## 生产环境部署

### 1. 修改配置

编辑 `.env` 文件：

```env
# 安全配置
SECRET_KEY=<生成一个强随机字符串>

# 生产数据库
DATABASE_URL=postgresql://user:password@dbhost:5432/price_query_db

# 邮件配置
MAIL_SERVER=your-smtp-server.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@domain.com
MAIL_PASSWORD=your-email-password

# 短信配置（可选）
SMS_API_URL=your-sms-api-url
SMS_API_KEY=your-sms-api-key
```

### 2. 使用Nginx反向代理

```bash
# 启动完整服务栈（包含Nginx）
docker-compose --profile production up -d
```

访问地址变为: http://localhost

### 3. 配置HTTPS

使用 Let's Encrypt 免费证书：

```bash
# 安装 certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com
```

### 4. 配置防火墙

```bash
# 允许HTTP和HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable
```

## 常用命令

### 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看Web应用日志
docker-compose logs -f web

# 查看数据库日志
docker-compose logs -f db
```

### 数据备份

```bash
# 备份数据库
docker exec price_query_db pg_dump -U postgres price_query_db > backup_$(date +%Y%m%d).sql

# 恢复数据库
docker exec -i price_query_db psql -U postgres price_query_db < backup_20240101.sql
```

### 停止和重启

```bash
# 停止所有服务
docker-compose down

# 停止并删除数据卷（危险！）
docker-compose down -v

# 重启服务
docker-compose restart
```

### 更新应用

```bash
# 拉取最新代码
git pull

# 重新构建镜像
docker-compose build

# 重启服务
docker-compose up -d
```

### 进入容器

```bash
# 进入Web应用容器
docker-compose exec web bash

# 进入数据库容器
docker-compose exec db psql -U postgres price_query_db
```

## 性能优化

### 1. 增加Worker数量

编辑 `docker-compose.yml`:

```yaml
web:
  command: ["gunicorn", "-w", "8", "-b", "0.0.0.0:5000", "app:app"]
```

### 2. 配置数据库连接池

编辑 `config/config.py`:

```python
SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_size': 20,
    'pool_recycle': 3600,
    'pool_pre_ping': True
}
```

### 3. 启用静态文件CDN

将 `app/static/` 目录上传到CDN，并修改Nginx配置。

## 监控和日志

### 健康检查

```bash
# 检查Web服务
curl http://localhost:5000/

# 检查Nginx
curl http://localhost/health

# Docker健康检查
docker-compose ps
```

### 日志管理

配置日志轮转：

```bash
# 创建日志轮转配置
sudo vim /etc/logrotate.d/price_query
```

内容：

```
/path/to/price_query_system/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
    sharedscripts
    postrotate
        docker-compose restart web
    endscript
}
```

## 故障排查

### 问题1: 容器无法启动

```bash
# 查看详细日志
docker-compose logs web

# 检查端口占用
netstat -tlnp | grep 5000

# 清理并重新启动
docker-compose down -v
docker-compose up -d
```

### 问题2: 数据库连接失败

```bash
# 检查数据库状态
docker-compose ps db

# 测试数据库连接
docker-compose exec web python -c "from app import db; print(db.engine.url)"

# 查看数据库日志
docker-compose logs db
```

### 问题3: 上传文件失败

```bash
# 检查上传目录权限
docker-compose exec web ls -la /app/app/static/uploads/

# 修复权限
docker-compose exec web chmod -R 755 /app/app/static/uploads/
```

### 问题4: 邮件发送失败

```bash
# 查看邮件配置
docker-compose exec web env | grep MAIL

# 测试邮件发送
docker-compose exec web python -c "from app import mail; from flask_mail import Message; msg = Message('Test', recipients=['test@example.com']); mail.send(msg)"
```

## 安全加固

1. **修改默认密码**

```bash
docker-compose exec web python -c "
from app import create_app, db
from app.models import User
app = create_app()
app.app_context().push()
admin = User.query.filter_by(username='admin').first()
admin.set_password('your-new-strong-password')
db.session.commit()
"
```

2. **启用防火墙**

```bash
sudo ufw default deny incoming
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable
```

3. **配置自动备份**

添加到 crontab:

```bash
# 每天凌晨2点备份数据库
0 2 * * * cd /path/to/price_query_system && docker exec price_query_db pg_dump -U postgres price_query_db > backup_$(date +\%Y\%m\%d).sql
```

## 技术支持

如遇到问题，请：

1. 查看 README.md 获取更多信息
2. 检查应用日志: `docker-compose logs -f web`
3. 提交 Issue 到项目仓库

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 产品查询和管理
- 订单系统
- 批量导入
- 邮件/短信通知
- Docker部署支持
