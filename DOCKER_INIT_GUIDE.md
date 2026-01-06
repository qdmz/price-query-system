# Docker 数据初始化指南

## 概述

本指南说明如何在Docker环境中初始化日用产品批发零售系统的数据。

## 数据初始化流程

### 1. 首次启动自动初始化

当Docker容器首次启动时，`docker-entrypoint.sh` 脚本会自动执行以下操作：

1. 等待PostgreSQL数据库就绪
2. 运行 `docker_init_data.py` 脚本初始化数据
3. 创建 `.initialized` 标志文件
4. 启动应用服务

### 2. 手动初始化

如果需要在运行中的容器中手动初始化数据，可以执行：

```bash
# 进入容器
docker exec -it price_query_web bash

# 运行初始化脚本
python docker_init_data.py

# 退出容器
exit
```

## 初始化数据内容

初始化脚本会创建以下数据：

### 1. 管理员账户
- 用户名: `admin`
- 密码: `admin123`
- 邮箱: `admin@example.com`

### 2. 产品分类（5个）
- 个人护理
- 清洁用品
- 纸品湿巾
- 厨房用品
- 家居纺织

### 3. 产品数据（10个产品，每个3张图片）
- SP001: 牙膏-薄荷味
- SP002: 洗发水-去屑型
- SP003: 洗衣液-薰衣草
- SP004: 毛巾-纯棉
- SP005: 纸巾-抽纸-3层
- SP006: 沐浴露-海洋香
- SP007: 洗洁精-柠檬
- SP008: 卫生纸-卷纸
- SP009: 垃圾袋-大号
- SP010: 护手霜-滋润型

### 4. 产品图片（30张）
使用Unsplash的高质量图片，每个产品3张图片（1张主图 + 2张副图）

### 5. 测试订单（约90个）
- 最近3个月的订单数据
- 每个月30个订单
- 随机订单状态（完成、已确认、已取消）
- 总订单金额约 ¥40,000

### 6. 系统设置（7条）
- 邮件通知配置
- 短信通知配置
- 公司信息配置

## 重置数据

如果需要重新初始化数据：

### 方法1: 删除初始化标志并重启容器
```bash
docker exec -it price_query_web rm /app/.initialized
docker-compose restart web
```

### 方法2: 直接运行初始化脚本
```bash
docker exec -it price_query_web python docker_init_data.py
```

### 方法3: 完全重置（删除数据库）
```bash
# 停止容器
docker-compose down

# 删除数据库卷
docker volume rm price_query_system_postgres_data

# 重新启动
docker-compose up -d
```

## 验证数据

登录系统后，可以验证以下数据：

### 前台页面
访问 `http://localhost:5000` 查看产品列表和图片

### 后台管理
访问 `http://localhost:5000/admin/dashboard` 使用管理员账户登录
- 产品管理: 查看所有产品和图片
- 订单管理: 查看订单数据
- 统计分析: 查看销售统计

### 命令行验证
```bash
docker exec -it price_query_web python -c "
from app.models import db, User, Category, Product, ProductImage, Order
from app import create_app

app = create_app('production')
with app.app_context():
    print(f'用户数: {User.query.count()}')
    print(f'分类数: {Category.query.count()}')
    print(f'产品数: {Product.query.count()}')
    print(f'产品图片数: {ProductImage.query.count()}')
    print(f'订单数: {Order.query.count()}')
"
```

## 常见问题

### 1. 图片无法显示
- 检查网络连接是否能访问Unsplash
- 检查 `app/static/uploads` 目录权限
- 查看容器日志: `docker-compose logs -f web`

### 2. 初始化失败
- 检查数据库连接: `docker-compose logs db`
- 检查磁盘空间: `docker system df`
- 查看详细错误: `docker-compose logs web`

### 3. 数据没有显示
- 确认初始化完成: `docker exec -it price_query_web cat /app/.initialized`
- 重启容器: `docker-compose restart web`
- 清除浏览器缓存

## 技术细节

### 初始化脚本文件
- `docker_init_data.py`: Docker专用初始化脚本
- `init_data.py`: 通用初始化脚本
- `fix_sp_images.py`: SP系列产品图片修复脚本

### 初始化标志
- 文件位置: `/app/.initialized`
- 作用: 防止重复初始化

### 数据持久化
- PostgreSQL数据存储在Docker卷 `postgres_data` 中
- 上传文件存储在 `./app/static/uploads` 目录中

## 联系支持

如遇到问题，请查看：
- 系统日志: `docker-compose logs -f`
- 应用日志: `docker-compose logs -f web`
- 数据库日志: `docker-compose logs -f db`
