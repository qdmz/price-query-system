# 快速参考卡

## 系统信息

| 项目 | 内容 |
|-----|------|
| 系统名称 | 日用产品批发零售系统 |
| 前台地址 | http://localhost:5000 |
| 后台地址 | http://localhost:5000/admin/dashboard |
| 管理员账号 | admin |
| 管理员密码 | admin123 |

## 数据概览

| 数据类型 | 数量 |
|---------|------|
| 用户 | 1 |
| 分类 | 5 |
| 产品 | 10 |
| 产品图片 | 30 |
| 订单 | 110 |
| 系统设置 | 7 |

## 产品分类

- 个人护理 (4个产品)
- 清洁用品 (2个产品)
- 纸品湿巾 (2个产品)
- 厨房用品 (1个产品)
- 家居纺织 (1个产品)

## 订单统计

- 总金额: ¥40,324.00
- 已完成: 74个
- 已确认: 28个
- 已取消: 8个

## 常用命令

### Docker操作
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f web

# 重启服务
docker-compose restart

# 停止服务
docker-compose down

# 进入容器
docker exec -it price_query_web bash
```

### 数据初始化
```bash
# 手动初始化数据
docker exec -it price_query_web python docker_init_data.py

# 重新初始化（删除标志后重启）
docker exec -it price_query_web rm /app/.initialized
docker-compose restart web
```

### 数据验证
```bash
# 查看数据统计
docker exec -it price_query_web python -c "
from app.models import db, User, Product, Order
from app import create_app
app = create_app('production')
with app.app_context():
    print(f'用户: {User.query.count()}, 产品: {Product.query.count()}, 订单: {Order.query.count()}')
"
```

## 产品清单（前5个）

1. **SP001** - 牙膏-薄荷味 ¥12.50
2. **SP002** - 洗发水-去屑型 ¥38.00
3. **SP003** - 洗衣液-薰衣草 ¥25.00
4. **SP004** - 毛巾-纯棉 ¥8.50
5. **SP005** - 纸巾-抽纸-3层 ¥12.00

## 重要文件

| 文件 | 说明 |
|-----|------|
| `docker_init_data.py` | Docker数据初始化脚本 |
| `init_data.py` | 通用数据初始化脚本 |
| `fix_sp_images.py` | 产品图片修复脚本 |
| `docker-entrypoint.sh` | 容器启动脚本 |
| `DOCKER_INIT_GUIDE.md` | 详细初始化指南 |

## 常见问题

### Q: 图片无法显示？
A: 检查网络连接是否能访问Unsplash，运行 `python fix_sp_images.py` 重新添加图片

### Q: 订单数据为空？
A: 运行 `python init_data.py` 或 `python docker_init_data.py` 重新初始化

### Q: 如何重置所有数据？
A:
```bash
docker-compose down
docker volume rm price_query_system_postgres_data
docker-compose up -d
```

## 技术支持

- 详细文档: 查看 `DOCKER_INIT_GUIDE.md`
- 系统日志: `docker-compose logs -f web`
- 数据库日志: `docker-compose logs -f db`

---
**数据初始化已完成 | 日期: 2025-01-07**
