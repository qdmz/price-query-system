# 数据初始化问题修复说明

## 问题描述

用户反馈重新部署后，产品图片和订单数据都没有看到。

## 问题原因

### 1. 产品数据缺失

**原因**: 初始化脚本 `init_data.py` 中缺少创建产品数据的功能

**影响**:
- 产品图片添加失败（因为没有产品）
- 订单数据生成失败（因为没有产品）

### 2. 订单创建方法错误

**原因**: `generate_orders_for_month` 函数使用了 `OrderService.create_order` 方法

**问题**:
- 该方法依赖 Flask 的请求上下文 `g.user`
- 在初始化脚本中运行时没有请求上下文，导致 `AttributeError: user`

## 解决方案

### 1. 添加产品初始化功能

在 `init_data.py` 中新增 `create_default_products()` 函数：

- 创建 6 个产品分类（个护用品、清洁用品、清洁工具、家居用品、厨房用品、母婴用品）
- 创建 15 个默认产品（牙膏、洗发水、沐浴露、洗衣液、洗洁精、拖把、扫帚、毛巾、水杯、菜板、餐具、湿巾等）
- 每个产品包含完整信息：货号、条码、名称、型号、规格、单位、零售价、批发价、库存、描述

**产品数据示例**:
```python
DEFAULT_PRODUCTS = [
    {'code': 'P001', 'name': '牙膏 清爽薄荷味', 'category': '个护用品', 
     'retail': 12.8, 'wholesale': 10.0, 'stock': 500, ...},
    # ... 共 15 个产品
]
```

### 2. 修复订单创建逻辑

修改 `generate_orders_for_month` 函数：

- **不再使用** `OrderService.create_order()` 方法
- **直接创建** `Order` 和 `OrderItem` 对象
- **正确处理** 字段名称（使用 `unit_price` 而不是 `price`）

**关键修改**:
```python
# 创建订单
order = Order(
    order_no=order_no,
    customer_name=customer_name,
    customer_phone=customer_phone,
    # ... 其他字段
    created_at=order_date,
    updated_at=order_date
)

# 创建订单项（注意使用 unit_price）
order_item = OrderItem(
    order_id=order.id,
    product_id=item_data['product'].id,
    quantity=item_data['quantity'],
    unit_price=item_data['price'],  # 正确的字段名
    subtotal=item_data['subtotal']
)
```

## 验证结果

运行 `python init_data.py` 后，数据初始化成功：

```
产品数量: 15
产品图片数量: 49
订单数量: 119
订单项数量: 404
```

### 各月订单统计
- 2025年8月: 31单, 总金额: ¥21,289.90
- 2025年9月: 25单, 总金额: ¥17,725.50
- 2025年10月: 24单, 总金额: ¥15,289.00
- 2025年11月: 17单, 总金额: ¥10,796.40
- 2025年12月: 15单, 总金额: ¥7,907.60
- 2026年1月: 7单, 总金额: ¥4,685.00

## 部署说明

### Docker 首次部署

首次部署时，容器会自动运行 `docker-entrypoint.sh`，该脚本会：

1. 等待数据库就绪
2. 运行 `init_data.py` 初始化所有数据
3. 创建 `.initialized` 标志文件
4. 启动应用服务

### 手动运行初始化

如果需要重新初始化数据：

```bash
# 在 Docker 容器中运行
docker-compose exec web python init_data.py

# 或本地运行
python init_data.py
```

### 重新部署（重置数据）

```bash
# 停止并删除容器和数据卷
docker-compose down -v

# 重新构建并启动（会自动触发首次初始化）
docker-compose up -d --build
```

## 文件变更

### 修改的文件

1. **init_data.py**:
   - 添加 `Category` 导入
   - 新增 `DEFAULT_PRODUCTS` 数据（15个产品）
   - 新增 `create_default_products()` 函数
   - 修改 `generate_orders_for_month()` 函数（直接创建订单对象）
   - 更新 `init_all_data()` 函数（添加产品初始化步骤）

### 新增的数据

- **产品分类**: 6个
- **产品**: 15个
- **产品图片**: 49张（从 Unsplash 下载）
- **订单**: 119个（分布在6个月内）
- **订单项**: 404个

## 注意事项

1. **网络连接**: 图片下载需要访问 Unsplash，确保容器可以访问互联网
2. **磁盘空间**: 图片下载需要一定磁盘空间，建议预留至少 500MB
3. **初始化顺序**: 必须先创建产品，再添加图片，最后生成订单
4. **字段名称**: 注意 `OrderItem` 模型使用 `unit_price` 而不是 `price`

## 后续优化建议

1. **进度显示**: 添加进度条显示初始化进度
2. **错误重试**: 图片下载失败时自动重试
3. **数据验证**: 初始化完成后自动验证数据完整性
4. **配置化**: 将初始化参数（如月份数量、产品数量等）配置化
5. **日志输出**: 将初始化日志输出到独立文件

## 总结

通过修复这两个问题，系统现在可以正确地：
1. 创建默认产品数据和分类
2. 为产品添加网络图片
3. 生成多个月的测试订单数据

重新部署后，用户可以立即看到完整的产品和订单数据，无需手动操作。
