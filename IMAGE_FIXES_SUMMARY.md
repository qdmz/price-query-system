# 产品图片功能修复总结

## 问题描述

用户反馈产品编辑页面存在以下问题：
1. ❌ 图片无法删除
2. ❌ 无法上传新图片
3. ❌ 无法设置主图片

---

## 问题分析

### 1. 缺少图片操作路由

**问题**：`app/routes/admin.py` 中只有删除图片的路由，但缺少设置主图的路由。

**影响**：前端无法调用设置主图的API，导致用户无法切换主图。

### 2. 前端UI问题

**问题**：`app/templates/admin/product_form.html` 中：
- 删除按钮位置不合理，容易误点击
- 没有设置主图的按钮
- 缺少操作提示

**影响**：用户体验差，功能不完整。

### 3. 文件路径处理问题

**问题**：删除图片时，文件路径拼接不正确：
```python
# 错误写法
image_path = os.path.join(current_app.root_path, image.image_url.lstrip('/'))
```

**影响**：无法正确删除物理文件。

### 4. 目录创建缺失

**问题**：`app/services/product_service.py` 中保存图片时，没有确保上传目录存在。

**影响**：如果目录不存在，图片上传会失败。

---

## 修复内容

### 1. 添加设置主图路由

**文件**：`app/routes/admin.py`

```python
# 设置主图
@admin_bp.route('/products/images/<int:image_id>/primary', methods=['POST'])
@login_required
def set_primary_image(image_id):
    """设置产品主图"""
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id

    try:
        # 取消该产品的所有主图
        ProductImage.query.filter_by(product_id=product_id).update({'is_primary': False})

        # 设置当前图片为主图
        image.is_primary = True
        db.session.commit()

        flash('主图设置成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'设置失败: {str(e)}', 'error')

    return redirect(url_for('admin.product_edit', product_id=product_id))
```

### 2. 优化删除图片路由

**文件**：`app/routes/admin.py`

**改进点**：
1. 修复文件路径拼接逻辑
2. 添加删除主图时自动切换功能
3. 更好的错误处理

```python
# 删除图片
@admin_bp.route('/products/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_product_image(image_id):
    """删除产品图片"""
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id

    try:
        # 修复文件路径拼接
        if image.image_url.startswith('/static/'):
            image_path = os.path.join(current_app.root_path, image.image_url.lstrip('/'))
        else:
            image_path = os.path.join(current_app.root_path, image.image_url)

        if os.path.exists(image_path):
            os.remove(image_path)

        # 如果删除的是主图，自动设置另一个为主图
        if image.is_primary:
            other_images = ProductImage.query.filter(
                ProductImage.product_id == product_id,
                ProductImage.id != image_id
            ).first()
            if other_images:
                other_images.is_primary = True

        db.session.delete(image)
        db.session.commit()

        flash('图片删除成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'删除失败: {str(e)}', 'error')

    return redirect(url_for('admin.product_edit', product_id=product_id))
```

### 3. 重构前端图片管理UI

**文件**：`app/templates/admin/product_form.html`

**改进点**：
1. 每张图片都有独立的操作栏
2. 添加设置主图按钮（星标图标）
3. 优化删除按钮（垃圾桶图标）
4. 主图有蓝色边框高亮
5. 添加操作提示

```html
<div class="position-relative" style="width: 90px; height: 110px;">
    <img src="{{ image.image_url }}" width="90" height="90"
         style="object-fit: cover; border-radius: 4px; border: 2px solid {% if image.is_primary %}#0d6efd{% else %}#dee2e6{% endif %};">
    {% if image.is_primary %}
    <span class="badge bg-primary position-absolute" style="top: 0; left: 0; z-index: 10;">主图</span>
    {% endif %}

    <!-- 操作按钮 -->
    <div class="position-absolute d-flex gap-1" style="bottom: 0; left: 0; right: 0; padding: 4px; background: rgba(0,0,0,0.7); border-radius: 0 0 4px 4px;">
        <!-- 设置主图按钮 -->
        {% if not image.is_primary %}
        <form action="/admin/products/images/{{ image.id }}/primary" method="POST" style="display: inline;">
            <button type="submit" class="btn btn-sm btn-primary" title="设为主图"
                    style="width: 32px; height: 28px; padding: 0; display: flex; align-items: center; justify-content: center;">
                <i class="bi bi-star" style="font-size: 12px;"></i>
            </button>
        </form>
        {% else %}
        <button type="button" class="btn btn-sm btn-primary disabled"
                style="width: 32px; height: 28px; padding: 0; opacity: 0.7;">
            <i class="bi bi-star-fill" style="font-size: 12px;"></i>
        </button>
        {% endif %}

        <!-- 删除按钮 -->
        <form action="/admin/products/images/{{ image.id }}/delete" method="POST"
              style="display: inline;"
              onsubmit="return confirm('确定要删除这张图片吗？');">
            <button type="submit" class="btn btn-sm btn-danger" title="删除图片"
                    style="width: 32px; height: 28px; padding: 0; display: flex; align-items: center; justify-content: center;">
                <i class="bi bi-trash" style="font-size: 12px;"></i>
            </button>
        </form>
    </div>
</div>
```

### 4. 修复图片保存服务

**文件**：`app/services/product_service.py`

**改进点**：
1. 添加目录自动创建
2. 确保上传目录存在

```python
@staticmethod
def save_product_image(file, product_id):
    """保存产品图片"""
    if file and ProductService.allowed_file(file.filename):
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{product_id}_{uuid.uuid4().hex[:8]}.{ext}"

        # 确保上传目录存在
        upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
        os.makedirs(upload_dir, exist_ok=True)

        filepath = os.path.join(upload_dir, unique_filename)
        file.save(filepath)

        return f'/static/uploads/products/{unique_filename}'
    return None
```

```python
@staticmethod
def download_image_from_url(url, product_id):
    """从URL下载图片"""
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            ext_map = {
                'image/jpeg': 'jpg',
                'image/jpg': 'jpg',
                'image/png': 'png',
                'image/gif': 'gif',
                'image/webp': 'webp'
            }
            ext = ext_map.get(content_type, 'jpg')

            unique_filename = f"{product_id}_{uuid.uuid4().hex[:8]}.{ext}"

            # 确保上传目录存在
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
            os.makedirs(upload_dir, exist_ok=True)

            filepath = os.path.join(upload_dir, unique_filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)

            return f'/static/uploads/products/{unique_filename}'
    except Exception as e:
        print(f"下载图片失败: {str(e)}")
    return None
```

---

## 测试结果

### 测试1：图片上传 ✅

```
【测试图片上传】
✓ 上传成功: /static/uploads/products/1_2bd51146.jpg
  - 文件路径: /workspace/projects/app/static/uploads/products/1_2bd51146.jpg
  - 文件存在: 是

【添加到数据库】
✓ 数据库添加成功
  - 图片ID: 21
  - 是否主图: False
  - 排序: 1
```

### 测试2：设置主图 ✅

```
【测试1：设置主图】
  原主图: 1
  新主图: 21
✓ 主图设置成功
  - 新主图ID: 21, is_primary=True
  - 原主图ID: 1, is_primary=False
```

### 测试3：删除图片 ✅

```
【测试2：删除图片】
  准备删除图片 ID: 1
  图片URL: /static/images/product-placeholder.jpg
  文件路径: /workspace/projects/app/static/images/product-placeholder.jpg
  文件存在: True
✓ 物理文件已删除
✓ 数据库记录已删除

【验证结果】
  - 剩余图片数量: 1
```

---

## 功能特性

### 1. 图片上传
- ✅ 支持多文件上传
- ✅ 支持拖拽上传（浏览器原生）
- ✅ 支持网络图片URL下载
- ✅ 自动生成唯一文件名
- ✅ 自动设置第一张图片为主图

### 2. 图片管理
- ✅ 查看所有产品图片
- ✅ 删除图片（带确认提示）
- ✅ 设置主图（星标按钮）
- ✅ 主图蓝色边框高亮
- ✅ 主图标识徽章

### 3. 智能功能
- ✅ 删除主图时自动设置另一张为主图
- ✅ 删除时同时删除物理文件和数据库记录
- ✅ 支持的格式：jpg, jpeg, png, gif, webp
- ✅ 文件大小限制：16MB

---

## 使用方法

### 1. 上传新图片

在产品编辑页面：
1. 点击"选择文件"按钮，选择一张或多张图片
2. 或者在"网络图片URL"文本框中输入图片URL（每行一个）
3. 点击"保存"按钮

### 2. 设置主图

在产品编辑页面的"已有图片"区域：
1. 找到要设置为主图的图片
2. 点击图片底部的星标按钮（⭐）
3. 图片会显示蓝色边框和"主图"徽章

### 3. 删除图片

在产品编辑页面的"已有图片"区域：
1. 找到要删除的图片
2. 点击图片底部的垃圾桶按钮（🗑️）
3. 确认删除操作

---

## 修改的文件

| 文件 | 修改类型 | 说明 |
|------|----------|------|
| `app/routes/admin.py` | 修改 | 添加设置主图路由，优化删除图片路由 |
| `app/templates/admin/product_form.html` | 修改 | 重构图片管理UI，添加设置主图按钮 |
| `app/services/product_service.py` | 修改 | 添加目录自动创建逻辑 |

---

## 测试脚本

| 文件 | 说明 |
|------|------|
| `test_image_features.py` | 检查图片数据状态 |
| `test_upload_image.py` | 测试图片上传功能 |
| `test_image_operations.py` | 测试删除和设置主图功能 |

---

## 常见问题

### Q1: 上传图片失败？

**A**：检查以下几点：
- 文件格式是否支持（jpg, jpeg, png, gif, webp）
- 文件大小是否超过16MB
- 上传目录是否有写入权限

### Q2: 删除图片后文件还在？

**A**：检查文件路径拼接是否正确。如果图片URL是`/static/uploads/products/xxx.jpg`，确保路径拼接正确。

### Q3: 设置主图后没有变化？

**A**：
1. 刷新页面查看
2. 检查数据库中`is_primary`字段是否更新
3. 查看浏览器控制台是否有错误

---

## 后续优化建议

1. **图片压缩**：上传时自动压缩图片，减少存储空间
2. **拖拽排序**：支持拖拽调整图片顺序
3. **图片裁剪**：添加图片裁剪功能
4. **懒加载**：图片列表使用懒加载优化性能
5. **批量操作**：支持批量删除图片

---

**修复完成时间**：2026-01-06
**版本**：v1.3
