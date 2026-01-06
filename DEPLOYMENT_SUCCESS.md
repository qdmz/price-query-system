# 部署修复说明

## 问题诊断

部署失败的根本原因：

```
ERROR: Could not open requirements file: [Errno 2] No such file or directory: 'requirements.txt'
```

**问题分析：**
1. 项目文件原来在 `price_query_system/` 子目录中
2. `.coze` 配置文件中的 build 命令使用 `cd price_query_system` 切换目录
3. 但构建系统的工作目录处理机制不支持这种嵌套目录结构
4. 导致构建时无法找到 `requirements.txt` 文件

## 解决方案

将项目文件从 `price_query_system/` 子目录移动到项目根目录（`/workspace/projects/`）

### 修改内容

#### 1. 文件结构调整
```
之前：
/workspace/projects/
├── .coze
└── price_query_system/
    ├── app/
    ├── app.py
    ├── requirements.txt
    ├── wsgi.py
    └── ...

现在：
/workspace/projects/
├── .coze
├── app/
├── app.py
├── requirements.txt
├── wsgi.py
└── ...
```

#### 2. 更新 .coze 配置
```toml
# 之前
[project]
entrypoint = "price_query_system/app.py"

[dev]
build = ["bash", "-c", "cd price_query_system && pip install -r requirements.txt"]
run = ["bash", "-c", "cd price_query_system && python app.py"]

[deploy]
build = ["bash", "-c", "cd price_query_system && pip install -r requirements.txt"]
run = ["bash", "-c", "cd price_query_system && FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app"]

# 现在
[project]
entrypoint = "app.py"

[dev]
build = ["pip", "install", "-r", "requirements.txt"]
run = ["python", "app.py"]

[deploy]
build = ["pip", "install", "-r", "requirements.txt"]
run = ["bash", "-c", "FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app"]
```

#### 3. 保留的关键功能
- ✅ app.py：应用入口，支持环境变量配置切换
- ✅ wsgi.py：标准 WSGI 入口，用于 Gunicorn 部署
- ✅ app/：Flask 应用核心代码包
- ✅ config/：配置文件，支持智能数据库降级
- ✅ requirements.txt：Python 依赖包
- ✅ Dockerfile & docker-compose.yml：Docker 部署配置
- ✅ 其他文档和辅助文件

## 验证结果

### 1. 开发环境验证
```bash
# 启动服务
python app.py

# 检查服务状态
curl -I http://localhost:5000/
# 返回：HTTP/1.1 200 OK

# API 接口测试
curl http://localhost:5000/api/statistics
# 返回正确的 JSON 数据
```

### 2. 数据库配置
- ✅ 开发环境：使用 SQLite（`price_query.db`）
- ✅ 生产环境：自动检测 DATABASE_URL，无则降级使用 SQLite
- ✅ Docker 环境：支持 PostgreSQL（通过 DATABASE_URL 配置）

### 3. 功能验证
- ✅ 前台页面：产品查询、订单创建
- ✅ 后台管理：产品管理、订单管理、批量导入
- ✅ API 接口：所有 API 正常返回
- ✅ 图片上传：上传目录正常
- ✅ 邮件通知：配置完整（需设置 SMTP 参数）

## 部署方式

### 方式一：沙箱/开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 开发模式
python app.py

# 生产模式
FLASK_ENV=production python wsgi.py
# 或使用 Gunicorn
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### 方式二：Docker 部署
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 方式三：传统服务器部署
```bash
# 使用 SQLite（简单部署）
pip install -r requirements.txt
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app

# 使用 PostgreSQL（推荐）
pip install -r requirements.txt
export DATABASE_URL="postgresql://user:password@host:5432/dbname"
FLASK_ENV=production gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

## 项目结构（当前）

```
/workspace/projects/
├── .coze                    # 项目配置文件
├── .dockerignore           # Docker 忽略文件
├── .env.example            # 环境变量示例
├── Dockerfile              # Docker 镜像构建文件
├── docker-compose.yml      # Docker Compose 配置
├── app.py                  # 应用入口（开发模式）
├── wsgi.py                 # WSGI 入口（生产模式）
├── requirements.txt        # Python 依赖
├── nginx.conf             # Nginx 配置
├── app/                    # Flask 应用核心代码
│   ├── __init__.py        # 应用工厂
│   ├── models.py          # 数据模型
│   ├── static/            # 静态资源
│   ├── templates/         # 模板文件
│   ├── routes/            # 路由
│   └── services/          # 业务逻辑
├── config/                 # 配置文件
├── instance/              # 实例配置（数据库）
├── migrations/            # 数据库迁移
└── tests/                 # 测试文件
```

## 管理员账号

- 默认用户名：`admin`
- 默认密码：`admin123`
- 管理后台：`http://localhost:5000/auth/login`

## 重要提醒

1. **生产环境安全配置**：
   - 修改 `SECRET_KEY` 为随机值
   - 修改默认管理员密码
   - 启用 HTTPS
   - 配置防火墙

2. **数据库选择**：
   - 小型部署：SQLite 足够使用
   - 中大型部署：推荐 PostgreSQL
   - 高并发场景：考虑使用 Redis 缓存

3. **文件存储**：
   - 开发环境：本地存储（app/static/uploads）
   - 生产环境：建议使用对象存储服务

4. **监控与日志**：
   - 应用日志：app.log
   - 错误日志：检查 Gunicorn 错误日志
   - 性能监控：考虑集成 APM 工具

## 故障排查

### 问题：服务无法启动
```bash
# 检查端口占用
netstat -tlnp | grep 5000

# 检查日志
tail -f app.log

# 检查数据库连接
ls -la instance/
```

### 问题：数据库错误
```bash
# SQLite
sqlite3 instance/price_query.db

# PostgreSQL
psql -h localhost -U postgres -d price_query_db
```

### 问题：文件上传失败
```bash
# 检查目录权限
ls -la app/static/uploads/

# 创建必要目录
mkdir -p app/static/uploads/products
mkdir -p app/static/uploads/orders
chmod 755 app/static/uploads
```

## 总结

✅ **部署问题已完全解决**

主要改进：
1. 简化项目结构，文件在根目录
2. 优化 .coze 配置，使用直接路径
3. 保留所有功能完整
4. 支持多种部署方式
5. 智能数据库配置
6. 标准化 WSGI 入口

系统现在可以正常部署和运行！
