# 系统配置与测试数据说明

## 概述

本系统支持在后台管理界面配置邮件和短信通知，无需修改代码。配置信息存储在数据库中，可以随时更改。

## 功能特性

✅ **后台配置管理**
- 邮件通知设置（SMTP）
- 短信通知设置（SMS API）
- 系统基本设置
- 配置实时生效

✅ **测试数据生成**
- 一键生成测试分类、产品、订单
- 模拟真实业务场景
- 支持重复执行（不重复创建）

✅ **数据持久化**
- 数据库使用临时目录（FaaS 兼容）
- 上传文件自动处理只读环境
- 支持多种部署环境

## 快速开始

### 1. 生成测试数据

```bash
# 在项目根目录执行
python generate_test_data.py
```

**生成的数据包括**：
- 5个产品分类（洗护用品、清洁用品、家居用品、厨房用品、纸品）
- 20个日用产品（牙膏、洗发水、纸巾等）
- 20个订单（包含不同状态：pending、confirmed、completed、cancelled）

### 2. 登录系统

```
地址：http://localhost:5000/auth/login
用户名：admin
密码：admin123
```

### 3. 访问系统设置

登录后，在后台管理侧边栏点击"通知设置"，或直接访问：
```
http://localhost:5000/system/settings
```

## 系统设置指南

### 邮件通知配置

#### 配置项

| 配置项 | 说明 | 示例 |
|-------|------|------|
| SMTP 服务器 | 邮件服务器地址 | smtp.gmail.com |
| SMTP 端口 | 服务器端口 | 587 (TLS) 或 465 (SSL) |
| 启用 TLS | 是否使用加密 | true |
| SMTP 用户名 | 邮箱地址 | your-email@gmail.com |
| SMTP 密码 | 邮箱密码或授权码 | your-app-password |
| 发件人地址 | 发送通知的邮箱 | noreply@example.com |
| 启用邮件通知 | 是否启用邮件通知 | true/false |

#### 配置示例

**QQ 邮箱**：
```
SMTP 服务器: smtp.qq.com
SMTP 端口: 587
启用 TLS: true
SMTP 用户名: your-email@qq.com
SMTP 密码: [QQ邮箱授权码]
发件人地址: your-email@qq.com
```

**获取 QQ 邮箱授权码**：
1. 登录 QQ 邮箱网页版
2. 设置 -> 账户 -> POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务
3. 开启 POP3/SMTP 服务
4. 生成授权码（不是登录密码）

**Gmail**：
```
SMTP 服务器: smtp.gmail.com
SMTP 端口: 587
启用 TLS: true
SMTP 用户名: your-email@gmail.com
SMTP 密码: [应用专用密码]
发件人地址: your-email@gmail.com
```

**获取 Gmail 应用专用密码**：
1. 访问 Google 账户安全设置
2. 两步验证 -> 应用专用密码
3. 生成新密码用于此应用

**163 网易邮箱**：
```
SMTP 服务器: smtp.163.com
SMTP 端口: 465
启用 TLS: true
SMTP 用户名: your-email@163.com
SMTP 密码: [邮箱授权码]
发件人地址: your-email@163.com
```

#### 测试邮件

配置完成后，点击"测试邮件"按钮：
1. 输入测试邮箱地址
2. 点击"发送测试邮件"
3. 检查收件箱（可能需要在垃圾邮件中查找）

### 短信通知配置

#### 配置项

| 配置项 | 说明 | 示例 |
|-------|------|------|
| 短信 API 地址 | 短信服务商的 API 地址 | https://sms-api.example.com/send |
| API 密钥 | 访问密钥 | your-api-key |
| API 密钥 Secret | 密钥 Secret | your-api-secret |
| 启用短信通知 | 是否启用短信通知 | true/false |

#### 短信服务商

**支持的短信服务商**（需要对接）：
- 阿里云短信服务
- 腾讯云短信
- 网易云信
- 容联云通讯

**对接方法**：
修改 `app/services/notification_service.py` 中的短信发送逻辑，对接服务商 API。

#### 测试短信

配置完成后，点击"测试短信"按钮：
1. 输入测试手机号
2. 点击"发送测试短信"
3. 检查手机短信

### 系统基本设置

| 配置项 | 说明 | 示例 |
|-------|------|------|
| 网站名称 | 显示在标题中的名称 | 日用产品批发零售系统 |
| 管理员邮箱 | 接收系统通知的邮箱 | admin@example.com |
| 管理员电话 | 接收紧急通知的电话 | 13800000000 |

## 使用流程

### 正常业务流程

1. **前台产品查询**
   - 访问首页：http://localhost:5000/
   - 搜索产品、查看价格
   - 点击"订购"创建订单

2. **后台订单处理**
   - 访问订单管理：http://localhost:5000/admin/orders
   - 查看新订单（状态为 pending）
   - 确认订单、标记为 completed
   - 取消订单（标记为 cancelled）

3. **自动通知**
   - 订单创建时：发送新订单通知给管理员
   - 订单状态变更时：发送状态更新通知给客户
   - 邮件和短信同时发送（如果配置）

### 数据管理流程

1. **产品管理**
   - 添加新产品：/admin/products/add
   - 编辑产品信息
   - 上传产品图片
   - 调整库存和价格

2. **批量导入**
   - 准备 Excel 文件（参考 EXCEL_IMPORT_GUIDE.md）
   - 访问批量导入：/admin/products/import
   - 上传文件并预览
   - 确认导入

3. **分类管理**
   - 创建分类：/admin/categories
   - 编辑分类信息
   - 调整排序

## 数据库位置

### 开发环境
```
/workspace/projects/price_query.db
```

### 生产环境（FaaS）
```
/tmp/price_query.db
```

### 查看数据库
```bash
# SQLite
sqlite3 /tmp/price_query.db
.tables
SELECT * FROM products LIMIT 5;
.quit

# 查看所有表
.schema
```

## 上传文件位置

### 正常环境
```
app/static/uploads/products/    # 产品图片
app/static/uploads/orders/     # 订单文件
```

### 只读环境（FaaS）
```
/tmp/uploads/products/         # 产品图片
/tmp/uploads/orders/          # 订单文件
```

## 故障排查

### 问题：配置保存后不生效

**检查**：
```bash
# 查看数据库中的配置
sqlite3 /tmp/price_query.db
SELECT * FROM system_settings;
```

**解决**：
- 确认配置已保存到数据库
- 重启应用使配置生效

### 问题：邮件发送失败

**检查**：
1. 邮箱是否开启了 SMTP 服务
2. 授权码是否正确
3. SMTP 端口是否正确
4. 防火墙是否阻止了 SMTP 连接

**解决**：
- 使用测试功能验证配置
- 检查邮箱的垃圾邮件文件夹
- 查看应用日志获取详细错误

### 问题：短信发送失败

**检查**：
1. API 地址是否正确
2. API 密钥是否有效
3. 账户余额是否充足
4. 手机号格式是否正确

**解决**：
- 使用测试功能验证配置
- 查看短信服务商控制台的发送记录
- 对接真实短信服务商 API

### 问题：测试数据生成失败

**检查**：
```bash
# 检查数据库是否可写
ls -la /tmp/price_query.db
```

**解决**：
- 确保数据库文件可写
- 检查磁盘空间是否充足
- 重新运行生成脚本

## API 端点

### 统计数据
```
GET /api/statistics
```

返回订单和产品统计信息。

### 产品搜索
```
GET /api/products/search?page=1&per_page=10&keyword=牙膏
```

搜索产品，支持分页。

### 产品详情
```
GET /api/products/<product_id>
```

获取单个产品详情。

### 创建订单
```
POST /api/orders
```

创建新订单。

## 安全建议

1. **修改默认密码**
   - 登录后立即修改 admin 密码
   - 密码长度至少 8 位

2. **保护配置信息**
   - SMTP 密码使用授权码，不是登录密码
   - API 密钥定期更换

3. **启用 HTTPS**
   - 生产环境使用 SSL/TLS
   - 配置防火墙规则

4. **定期备份**
   - 定期备份数据库
   - 备份上传文件

## 性能优化

1. **数据库优化**
   - 为常用查询字段添加索引
   - 定期清理过期数据

2. **缓存策略**
   - 考虑使用 Redis 缓存热点数据
   - 实现静态资源 CDN

3. **文件存储**
   - 大文件使用对象存储（OSS、S3）
   - 启用图片压缩和缩略图

## 监控与日志

### 查看日志
```bash
# 应用日志
tail -f app.log

# 系统日志
journalctl -u flask
```

### 关键指标
- 订单创建数量
- 邮件发送成功率
- 短信发送成功率
- 产品浏览量

## 常见问题

**Q: 配置保存在哪里？**
A: 所有配置保存在数据库 `system_settings` 表中。

**Q: 如何重置配置？**
A: 在系统设置页面清空配置项，或直接修改数据库。

**Q: 支持多个管理员吗？**
A: 支持，可以创建多个管理员账号。

**Q: 数据可以导出吗？**
A: 可以使用 SQLite 工具导出数据库，或使用 Excel 导出功能。

**Q: 如何部署到生产环境？**
A: 参考 DEPLOYMENT_FINAL.md，支持 Docker 和 FaaS 部署。

## 技术支持

遇到问题？
1. 查看相关文档：
   - README.md - 项目概述
   - DEPLOYMENT_FINAL.md - 部署指南
   - EXCEL_IMPORT_GUIDE.md - 批量导入指南
   - FaaS_DEPLOYMENT_FIX.md - FaaS 环境适配

2. 检查日志文件

3. 查看 API 文档和代码注释

## 更新日志

### v1.2.0 (2026-01-06)
- ✅ 添加后台系统设置管理
- ✅ 支持邮件和短信配置
- ✅ 创建测试数据生成脚本
- ✅ 修复 FaaS 只读文件系统问题
- ✅ 优化数据库存储路径

### v1.1.0 (2026-01-06)
- ✅ 添加 Excel 批量导入功能
- ✅ 支持产品多图片管理
- ✅ 实现订单状态管理
- ✅ 添加邮件和短信通知

### v1.0.0 (2026-01-05)
- ✅ 基础产品查询功能
- ✅ 订单创建和管理
- ✅ 后台管理界面
- ✅ 用户认证系统

---

**系统版本**: v1.2.0
**更新时间**: 2026-01-06
**技术支持**: 查看项目文档
