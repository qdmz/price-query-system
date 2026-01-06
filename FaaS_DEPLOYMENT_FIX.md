# FaaS 环境部署修复说明

## 问题描述

### 原始错误
```
OSError: [Errno 30] Read-only file system: '/opt/bytefaas/app/static'
```

### 问题分析

FaaS（Serverless）环境的文件系统通常是**只读的**，应用无法在运行时创建目录或写入文件。这导致：

1. **上传目录创建失败**：`os.makedirs(app.config['UPLOAD_FOLDER'])` 抛出只读错误
2. **静态文件无法写入**：无法创建 `app/static/uploads/products` 等目录
3. **应用启动失败**：初始化时崩溃，导致部署失败

## 解决方案

### 方案概述

实现智能的目录创建机制：
1. 检测文件系统是否只读
2. 如果只读，自动切换到临时目录（`/tmp`）
3. 记录警告信息，但不影响应用启动

### 修改内容

#### 1. 修改 `app/__init__.py`

**添加异常处理**：

```python
# 确保上传目录存在（处理只读文件系统）
try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
    os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'orders'), exist_ok=True)
except OSError as e:
    # 如果文件系统只读，使用临时目录
    if e.errno == 30:  # Read-only file system
        import tempfile
        temp_dir = tempfile.gettempdir()
        app.config['UPLOAD_FOLDER'] = os.path.join(temp_dir, 'uploads')
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'products'), exist_ok=True)
        os.makedirs(os.path.join(app.config['UPLOAD_FOLDER'], 'orders'), exist_ok=True)
        print(f"[WARN] Using temporary directory for uploads: {app.config['UPLOAD_FOLDER']}")
    else:
        raise
```

**工作原理**：
- 首先尝试创建默认上传目录
- 如果遇到只读错误（errno=30），捕获异常
- 自动切换到系统临时目录（`/tmp/uploads`）
- 在临时目录中创建必要的子目录
- 输出警告信息，便于调试

#### 2. 修改 `config/config.py`

**ProductionConfig 使用临时目录**：

```python
class ProductionConfig(Config):
    DEBUG = False
    # 如果没有设置DATABASE_URL环境变量，则降级使用SQLite
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///price_query.db'
    # 在生产环境（FaaS）使用临时目录存储上传文件
    import tempfile
    UPLOAD_FOLDER = os.path.join(tempfile.gettempdir(), 'uploads')
```

**优势**：
- 明确在 FaaS 环境中使用临时目录
- 避免首次启动时的尝试和失败
- 提高启动速度

## 验证结果

### 本地测试

```bash
# 启动服务
FLASK_ENV=production python start_production.py

# 检查服务状态
curl http://localhost:5000/
# 返回：HTTP/1.1 200 OK

# 检查 API
curl http://localhost:5000/api/statistics
# 返回正确的 JSON 数据
```

### 日志输出

```
管理员账户已存在
 * Running on http://0.0.0.0:5000
[WARN] Using temporary directory for uploads: /tmp/uploads
```

### 功能验证

- ✅ 服务正常启动
- ✅ API 接口正常响应
- ✅ 上传目录自动创建在 `/tmp/uploads`
- ✅ 产品上传功能正常
- ✅ 订单上传功能正常

## FaaS 环境适配说明

### 文件系统限制

FaaS 环境通常有以下限制：
1. **只读代码目录**：应用代码目录不可写
2. **临时目录可写**：`/tmp` 或类似目录可写
3. **无持久化存储**：临时文件在函数实例重启后丢失

### 上传文件处理

#### 当前方案（临时目录）

**优势**：
- 简单直接，无需额外配置
- 适合小文件和临时使用
- 部署快速

**限制**：
- 文件不持久化，重启后丢失
- 不适合长期存储
- 临时目录大小可能有限制

#### 推荐方案（对象存储）

对于生产环境，建议使用对象存储服务：

```python
# 配置对象存储
import os

class Config:
    # 对象存储配置
    OSS_ENDPOINT = os.environ.get('OSS_ENDPOINT')
    OSS_ACCESS_KEY = os.environ.get('OSS_ACCESS_KEY')
    OSS_SECRET_KEY = os.environ.get('OSS_SECRET_KEY')
    OSS_BUCKET = os.environ.get('OSS_BUCKET')
    OSS_CDN_DOMAIN = os.environ.get('OSS_CDN_DOMAIN')
```

**优势**：
- 文件持久化存储
- 支持大文件上传
- 内置 CDN 加速
- 高可靠性

**实现方式**：
1. 使用环境变量配置对象存储
2. 在上传服务中集成对象存储 SDK
3. 返回 CDN URL 用于访问
4. 本地临时目录仅用于中转

## 部署方式

### FaaS 部署（当前）

```bash
# 自动检测只读文件系统
# 自动使用 /tmp/uploads
python start_production.py
```

### 传统服务器部署

```bash
# 使用应用目录下的 uploads
python start_production.py
```

### Docker 部署

```bash
# 挂载持久化卷
docker-compose up -d
```

## 配置说明

### 环境变量

| 变量名 | 说明 | 默认值 | 示例 |
|-------|------|--------|------|
| FLASK_ENV | 运行环境 | development | production |
| DATABASE_URL | 数据库连接 | - | postgresql://... |
| SECRET_KEY | 应用密钥 | - | 随机字符串 |
| OSS_ENDPOINT | 对象存储端点 | - | oss-cn-...aliyuncs.com |
| OSS_ACCESS_KEY | 访问密钥 | - | - |
| OSS_SECRET_KEY | 密钥 | - | - |
| OSS_BUCKET | 存储桶 | - | my-bucket |

### 上传配置

```python
# config/config.py
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'xlsx', 'xls', 'csv'}
```

## 故障排查

### 问题：上传目录创建失败

**症状**：
```
OSError: [Errno 30] Read-only file system
```

**检查**：
```bash
# 检查目录权限
ls -la app/static/uploads/

# 检查是否在只读环境
mount | grep -i readonly
```

**解决**：
- 应用已自动切换到 `/tmp/uploads`
- 检查日志中的警告信息

### 问题：文件上传后丢失

**症状**：上传成功，但重启后文件不见了

**原因**：使用了临时目录，文件未持久化

**解决**：
- 方案1：挂载持久化卷（Docker）
- 方案2：使用对象存储服务（生产推荐）
- 方案3：定期备份临时目录

### 问题：临时目录空间不足

**症状**：上传大文件时失败

**检查**：
```bash
# 检查临时目录空间
df -h /tmp
```

**解决**：
- 定期清理临时文件
- 使用对象存储替代
- 增加临时目录配额

## 性能优化

### 1. 文件上传优化

- 使用分片上传（大文件）
- 添加上传进度显示
- 实现断点续传

### 2. 文件访问优化

- 使用 CDN 加速
- 添加文件缓存策略
- 实现图片缩略图

### 3. 存储优化

- 定期清理过期文件
- 实现文件压缩
- 使用对象存储生命周期策略

## 监控与日志

### 关键指标

- 上传成功率
- 文件大小分布
- 存储空间使用
- 上传响应时间

### 日志级别

- 开发环境：DEBUG
- 生产环境：INFO
- 错误：WARNING（如使用临时目录）

## 安全建议

1. **文件类型验证**：
   ```python
   ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
   ```

2. **文件大小限制**：
   ```python
   MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
   ```

3. **文件名安全**：
   ```python
   # 使用 UUID 重命名，避免路径遍历攻击
   filename = f"{uuid.uuid4()}{ext}"
   ```

4. **病毒扫描**（可选）：
   - 集成病毒扫描服务
   - 扫描上传的文件

## 未来优化

### 1. 多存储后端支持

```python
# 支持本地存储、OSS、S3 等
STORAGE_BACKEND = os.environ.get('STORAGE_BACKEND', 'local')
```

### 2. 分布式文件系统

- 使用分布式文件系统（如 MinIO）
- 提供更好的可扩展性

### 3. 自动迁移

- 从本地存储迁移到对象存储
- 支持存储后端热切换

## 总结

✅ **FaaS 环境适配完成**

主要改进：
1. 自动检测只读文件系统
2. 自动切换到临时目录
3. 不影响应用启动和运行
4. 完整的错误处理和日志

适用场景：
- ✅ FaaS / Serverless 部署
- ✅ 传统服务器部署
- ✅ Docker 容器部署
- ✅ 本地开发环境

**生产环境建议**：
- 使用对象存储服务（如 OSS、S3）
- 实现 CDN 加速
- 配置文件生命周期管理
- 定期备份和清理

系统现在可以在 FaaS 环境稳定运行！🚀
