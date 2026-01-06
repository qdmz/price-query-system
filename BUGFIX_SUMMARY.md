# Bug修复总结

## 问题1：上传产品图片无法显示

### 问题原因
1. **FaaS环境只读文件系统**：在FaaS环境中，`app/static/uploads`目录不可写，应用自动切换到`/tmp/uploads`目录
2. **静态文件路由缺失**：Flask默认只提供`app/static`目录下的文件，无法提供`/tmp/uploads`目录的文件
3. **占位图片缺失**：测试数据生成的图片URL指向`/static/images/product-placeholder.jpg`，但该文件不存在

### 解决方案
1. **添加临时目录静态文件路由** (`app/__init__.py:57-60`)
   ```python
   @app.route('/static/uploads/<path:filename>')
   def serve_upload_file(filename):
       """提供上传的文件（包括临时目录）"""
       return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
   ```

2. **创建占位图片** (`create_placeholder.py`)
   - 创建`app/static/images`目录
   - 生成400x400像素的JPEG占位图片

### 验证
- 占位图片可访问：`http://localhost:5000/static/images/product-placeholder.jpg`
- 图片上传后会保存到`/tmp/uploads/products/`目录
- 访问URL格式：`http://localhost:5000/static/products/{filename}`

---

## 问题2：导入产品页面的示例文件无法下载

### 问题原因
1. **示例Excel文件不存在**：系统没有创建示例Excel文件
2. **下载链接无效**：导入页面的下载按钮使用`href="#"`，没有实际的路由
3. **缺少下载路由**：没有处理示例文件下载的路由

### 解决方案
1. **创建示例Excel文件** (`create_sample_excel.py`)
   - 包含5条示例产品数据
   - 保存到`app/static/files/product_import_template.xlsx`
   - 字段包括：货号、条码、产品名称、型号、规格、单位、零售价、批发价、批发最小数量、库存、描述

2. **添加示例文件下载路由** (`app/routes/admin.py:142-153`)
   ```python
   @admin_bp.route('/products/import/sample')
   @login_required
   def download_sample():
       """下载示例Excel文件"""
       sample_file = os.path.join(current_app.root_path, 'static', 'files', 'product_import_template.xlsx')
       if os.path.exists(sample_file):
           return send_file(sample_file, ...)
   ```

3. **更新导入页面下载按钮** (`app/templates/admin/products_import.html:78`)
   ```html
   <a href="{{ url_for('admin.download_sample') }}" class="btn btn-outline-success">
   ```

### 验证
- 示例文件路径：`app/static/files/product_import_template.xlsx`
- 下载路由：`/admin/products/import/sample`（需要登录）
- 文件名：产品导入模板.xlsx

---

## 测试数据导入问题

### 问题原因
- `check_db.py`和`generate_test_data.py`使用不同的配置
  - `check_db.py`使用`production`配置 → SQLite: `/tmp/price_query.db`
  - `generate_test_data.py`使用`development`配置 → SQLite: `price_query.db`

### 解决方案
- 修改`check_db.py`使用`development`配置，与生成脚本保持一致

---

## 文件变更清单

### 新建文件
1. `create_sample_excel.py` - 创建示例Excel文件脚本
2. `create_placeholder.py` - 创建占位图片脚本
3. `app/static/images/product-placeholder.jpg` - 产品占位图片
4. `app/static/files/product_import_template.xlsx` - 产品导入示例文件

### 修改文件
1. `app/__init__.py` - 添加临时目录静态文件路由
2. `app/routes/admin.py` - 添加示例文件下载路由
3. `app/templates/admin/products_import.html` - 更新下载按钮链接
4. `check_db.py` - 修改配置为development

---

## 使用说明

### 1. 测试图片显示
访问以下URL查看占位图片：
```
http://localhost:5000/static/images/product-placeholder.jpg
```

### 2. 测试示例文件下载
1. 访问：`http://localhost:5000/auth/login`
2. 使用管理员账户登录：`admin / admin123`
3. 访问产品导入页面：`http://localhost:5000/admin/products/import`
4. 点击"下载示例Excel文件"按钮

### 3. 上传产品图片
1. 在产品创建或编辑页面，选择图片文件上传
2. 图片会保存到`/tmp/uploads/products/`目录
3. 图片URL格式：`/static/uploads/products/{product_id}_{uuid}.{ext}`

### 4. 批量导入产品
1. 下载示例Excel文件
2. 按照格式填写产品数据
3. 上传Excel文件进行导入

---

## 注意事项

1. **FaaS环境**：在FaaS环境中，所有上传文件会保存到`/tmp/uploads`目录
2. **文件持久化**：`/tmp`目录在重启后会被清空，生产环境建议使用对象存储
3. **图片格式**：支持JPG、JPEG、PNG、GIF、WEBP格式
4. **Excel格式**：支持.xlsx、.xls、.csv格式，最大文件大小10MB
5. **示例数据**：如果需要重新生成测试数据，运行：
   ```bash
   python generate_test_data.py
   ```

---

## 技术栈依赖更新

需要安装以下Python包：
- `openpyxl` - 用于处理Excel文件
- `Pillow` - 用于创建占位图片

已在`requirements.txt`中包含。
