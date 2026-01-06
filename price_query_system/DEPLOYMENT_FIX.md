# 部署问题排查与修复说明

## 问题描述

部署失败的主要原因：

1. **生产环境数据库配置问题**：原始配置中，ProductionConfig 默认使用 PostgreSQL，但在非 Docker 环境下没有 PostgreSQL 服务
2. **Gunicorn 启动入口问题**：Dockerfile 使用 `app:app` 作为启动入口，但 app.py 无法被 Gunicorn 正确导入
3. **配置管理不够灵活**：开发环境和生产环境的配置切换不够智能

## 已修复的问题

### 1. 智能数据库配置降级

**修改文件**：`config/config.py`

**修改内容**：
```python
class ProductionConfig(Config):
    DEBUG = False
    # 如果没有设置DATABASE_URL环境变量，则降级使用SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///price_query.db'
```

**效果**：
- 在 Docker 环境中（有 DATABASE_URL）：使用 PostgreSQL
- 在非 Docker 环境中（无 DATABASE_URL）：自动降级使用 SQLite
- 确保应用在任何环境下都能正常运行

### 2. 创建 WSGI 入口文件

**新建文件**：`wsgi.py`

**内容**：
```python
import os
from app import create_app

# 根据环境变量自动选择配置
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
```

**作用**：
- 提供标准的 WSGI 入口点
- 根据 FLASK_ENV 环境变量自动选择配置
- 兼容 Gunicorn 和其他 WSGI 服务器

### 3. 更新部署配置

**修改文件**：`.coze`

**修改内容**：
```toml
[deploy]
build = ["bash", "-c", "cd price_query_system && pip install -r requirements.txt"]
run = ["bash", "-c", "cd price_query_system && FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app"]
deps = ["git"]
```

**效果**：
- 使用 wsgi.py 作为启动入口
- 明确设置 FLASK_ENV=production
- 使用 4 个 worker 进程提高并发性能

### 4. 更新 Dockerfile

**修改文件**：`Dockerfile`

**修改内容**：
```dockerfile
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
```

**效果**：
- 使用正确的 WSGI 入口点
- 在 Docker 环境中也能正常启动

### 5. 智能配置选择

**修改文件**：`app.py`

**修改内容**：
```python
import os
from app import create_app

# 根据环境变量自动选择配置
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=config_name == 'development')
```

**效果**：
- 根据环境变量自动切换开发/生产配置
- debug 模式与配置环境保持一致

## 部署方式说明

### 方式一：沙箱环境部署（当前使用）

```bash
# 开发环境
cd price_query_system
python app.py
# 访问 http://localhost:5000

# 生产环境
FLASK_ENV=production python wsgi.py
# 或者使用 Gunicorn
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### 方式二：Docker 部署

```bash
# 构建镜像
docker-compose build

# 启动服务（包含 PostgreSQL 数据库）
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式三：传统部署

```bash
# 安装依赖
pip install -r requirements.txt

# 使用 SQLite 数据库（简单部署）
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# 使用 PostgreSQL 数据库（需要先安装并启动 PostgreSQL）
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## 验证部署

### 1. 健康检查

```bash
# 检查服务是否运行
curl -I http://localhost:5000/

# 检查 API 接口
curl http://localhost:5000/api/statistics
```

### 2. 数据库验证

```bash
# SQLite（开发环境或无 DATABASE_URL）
cd price_query_system
sqlite3 price_query.db
.tables

# PostgreSQL（Docker 环境或有 DATABASE_URL）
docker exec -it price_query_db psql -U postgres -d price_query_db
\dt
```

### 3. 日志查看

```bash
# 应用日志
tail -f price_query_system/app.log

# Docker 日志
docker-compose logs -f web
```

## 常见问题

### Q1: 服务启动后无法访问

**检查**：
```bash
# 检查端口是否被占用
netstat -tlnp | grep 5000

# 检查进程是否运行
ps aux | grep gunicorn
```

**解决**：
- 如果端口被占用，停止占用进程或更换端口
- 如果进程未运行，查看错误日志

### Q2: 数据库连接失败

**错误信息**：
```
psycopg2.OperationalError: connection to server at "localhost" failed
```

**解决**：
- 在 Docker 环境中：确保 `docker-compose up -d` 已启动
- 在非 Docker 环境中：
  - 方案1：不设置 DATABASE_URL，使用 SQLite
  - 方案2：安装并启动 PostgreSQL，设置正确的 DATABASE_URL

### Q3: 文件上传失败

**检查**：
```bash
# 检查上传目录权限
ls -la price_query_system/app/static/uploads/
```

**解决**：
```bash
# 确保目录存在且有写权限
mkdir -p price_query_system/app/static/uploads/products
mkdir -p price_query_system/app/static/uploads/orders
chmod 755 price_query_system/app/static/uploads
```

### Q4: 静态文件 404

**检查**：
- 确保 `app/static` 目录存在
- 确保 Flask 应用正确注册了 static 路由

**解决**：
```bash
# 检查目录结构
ls -R price_query_system/app/static/
```

## 性能优化建议

### 1. 数据库优化

- 使用连接池：SQLAlchemy 默认使用连接池
- 添加索引：为常用查询字段添加数据库索引
- 考虑使用 Redis 缓存热点数据

### 2. 应用优化

- 使用更多 worker：`gunicorn -w 8 -b 0.0.0.0:5000 wsgi:app`
- 使用异步 worker：`gunicorn -k gevent -w 4 -b 0.0.0.0:5000 wsgi:app`
- 启用 gzip 压缩

### 3. 文件存储优化

- 使用对象存储（如 AWS S3、阿里云 OSS）替代本地文件存储
- 配置 CDN 加速静态资源访问

## 监控与日志

### 1. 应用监控

- 监控进程：`ps aux | grep gunicorn`
- 监控端口：`netstat -tlnp | grep 5000`
- 监控日志：`tail -f price_query_system/app.log`

### 2. 日志级别

开发环境：DEBUG
生产环境：INFO 或 WARNING

修改配置文件调整日志级别。

## 安全建议

1. **修改 SECRET_KEY**：生产环境必须设置随机密钥
2. **数据库密码**：使用强密码
3. **启用 HTTPS**：生产环境必须使用 SSL/TLS
4. **限制访问**：配置防火墙规则
5. **定期备份**：定期备份数据库和上传文件

## 总结

经过以上修复，系统现在支持：

✅ 开发环境（SQLite + Flask 开发服务器）
✅ 生产环境（SQLite 或 PostgreSQL + Gunicorn）
✅ Docker 部署（PostgreSQL + Gunicorn + Nginx）
✅ 传统部署（支持多种数据库）
✅ 智能配置切换（根据环境变量自动选择）
✅ 灵活的数据库配置（自动降级机制）

部署问题已完全解决！
