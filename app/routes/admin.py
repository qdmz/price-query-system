from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, send_file
from flask_login import login_required, current_user
from app.models import db, Product, ProductImage, Category, Order, OrderItem, SystemSetting
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.services.statistics_service import StatisticsService
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta
import os

admin_bp = Blueprint('admin', __name__)

# 仪表盘
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    """后台管理首页"""
    from app.services.order_service import OrderService
    
    # 统计数据
    stats = {
        'products': {
            'total': Product.query.count(),
            'active': Product.query.filter_by(status='active').count(),
            'out_of_stock': Product.query.filter(Product.stock == 0).count()
        },
        'orders': OrderService.get_order_statistics(),
        'categories': Category.query.count()
    }
    
    # 最近订单
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders)

# 产品管理
@admin_bp.route('/products')
@login_required
def products():
    """产品列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 搜索条件
    query = request.args.get('q', '')
    category_id = request.args.get('category_id', type=int)
    
    products_query = Product.query
    
    if query:
        products_query = products_query.filter(
            (Product.name.contains(query)) |
            (Product.product_code.contains(query)) |
            (Product.barcode.contains(query))
        )
    
    if category_id:
        products_query = products_query.filter_by(category_id=category_id)
    
    pagination = products_query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    categories = Category.query.all()
    
    return render_template('admin/products.html',
                         products=pagination.items,
                         pagination=pagination,
                         categories=categories,
                         query=query,
                         category_id=category_id)

@admin_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
def product_new():
    """新增产品"""
    if request.method == 'POST':
        try:
            # 创建产品
            data = {
                'product_code': request.form.get('product_code'),
                'barcode': request.form.get('barcode'),
                'name': request.form.get('name'),
                'model': request.form.get('model'),
                'specification': request.form.get('specification'),
                'unit': request.form.get('unit', '件'),
                'retail_price': request.form.get('retail_price', 0),
                'wholesale_price': request.form.get('wholesale_price', 0),
                'wholesale_min_qty': request.form.get('wholesale_min_qty', 1),
                'stock': request.form.get('stock', 0),
                'description': request.form.get('description'),
                'category_id': request.form.get('category_id')
            }

            product = ProductService.create_product(data)

            # 处理图片上传
            if 'images' in request.files:
                files = request.files.getlist('images')
                for idx, file in enumerate(files):
                    if file and file.filename:
                        image_url = ProductService.save_product_image(file, product.id)
                        if image_url:
                            is_primary = (idx == 0)
                            image = ProductImage(
                                product_id=product.id,
                                image_url=image_url,
                                is_primary=is_primary,
                                sort_order=idx
                            )
                            db.session.add(image)

            # 处理网络图片
            image_urls = request.form.get('image_urls', '').strip()
            if image_urls:
                existing_count = product.images.count()
                urls = [url.strip() for url in image_urls.split('\n') if url.strip()]
                for idx, url in enumerate(urls):
                    downloaded_url = ProductService.download_image_from_url(url, product.id)
                    if downloaded_url:
                        is_primary = (existing_count + idx == 0)
                        image = ProductImage(
                            product_id=product.id,
                            image_url=downloaded_url,
                            is_primary=is_primary,
                            sort_order=existing_count + idx
                        )
                        db.session.add(image)

            db.session.commit()

            # 判断是否是AJAX请求
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '产品创建成功'})
            else:
                flash('产品创建成功', 'success')
                return redirect(url_for('admin.products'))

        except Exception as e:
            db.session.rollback()

            # 判断是否是AJAX请求
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': str(e)}), 500
            else:
                flash(f'创建产品失败: {str(e)}', 'error')

    categories = Category.query.all()
    return render_template('admin/product_form.html', categories=categories)

@admin_bp.route('/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def product_edit(product_id):
    """编辑产品"""
    product = Product.query.get_or_404(product_id)

    if request.method == 'POST':
        try:
            # 更新产品信息
            data = {
                'product_code': request.form.get('product_code'),
                'barcode': request.form.get('barcode'),
                'name': request.form.get('name'),
                'model': request.form.get('model'),
                'specification': request.form.get('specification'),
                'unit': request.form.get('unit', '件'),
                'retail_price': request.form.get('retail_price', 0),
                'wholesale_price': request.form.get('wholesale_price', 0),
                'wholesale_min_qty': request.form.get('wholesale_min_qty', 1),
                'stock': request.form.get('stock', 0),
                'description': request.form.get('description'),
                'category_id': request.form.get('category_id')
            }

            ProductService.update_product(product_id, data)

            # 处理新图片上传
            if 'images' in request.files:
                files = request.files.getlist('images')
                existing_count = product.images.count()
                for idx, file in enumerate(files):
                    if file and file.filename:
                        image_url = ProductService.save_product_image(file, product.id)
                        if image_url:
                            image = ProductImage(
                                product_id=product.id,
                                image_url=image_url,
                                is_primary=False,
                                sort_order=existing_count + idx
                            )
                            db.session.add(image)

            # 处理网络图片
            image_urls = request.form.get('image_urls', '').strip()
            if image_urls:
                existing_count = product.images.count()
                urls = [url.strip() for url in image_urls.split('\n') if url.strip()]
                for idx, url in enumerate(urls):
                    downloaded_url = ProductService.download_image_from_url(url, product.id)
                    if downloaded_url:
                        image = ProductImage(
                            product_id=product.id,
                            image_url=downloaded_url,
                            is_primary=False,
                            sort_order=existing_count + idx
                        )
                        db.session.add(image)

            db.session.commit()

            # 判断是否是AJAX请求
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': True, 'message': '产品更新成功'})
            else:
                flash('产品更新成功', 'success')
                return redirect(url_for('admin.products'))

        except Exception as e:
            db.session.rollback()

            # 判断是否是AJAX请求
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({'success': False, 'message': str(e)}), 500
            else:
                flash(f'更新产品失败: {str(e)}', 'error')

    categories = Category.query.all()
    return render_template('admin/product_form.html', product=product, categories=categories)

@admin_bp.route('/products/<int:product_id>/delete', methods=['POST'])
@login_required
def product_delete(product_id):
    """删除产品"""
    try:
        ProductService.delete_product(product_id)
        flash('产品删除成功', 'success')
    except Exception as e:
        flash(f'删除产品失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.products'))

# 批量导入
@admin_bp.route('/products/import', methods=['GET', 'POST'])
@login_required
def products_import():
    """批量导入产品"""
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('请选择文件', 'error')
            return redirect(url_for('admin.products_import'))
        
        file = request.files['file']
        if file.filename == '':
            flash('请选择文件', 'error')
            return redirect(url_for('admin.products_import'))
        
        if not ProductService.allowed_file(file.filename):
            flash('不支持的文件格式', 'error')
            return redirect(url_for('admin.products_import'))
        
        try:
            result = ProductService.import_products_from_excel(file)
            
            if result['success_count'] > 0:
                flash(f'成功导入 {result["success_count"]} 个产品', 'success')
            if result['error_count'] > 0:
                for error in result['errors'][:10]:  # 只显示前10个错误
                    flash(error, 'error')
                if result['error_count'] > 10:
                    flash(f'还有 {result["error_count"] - 10} 个错误未显示', 'error')
            
            return redirect(url_for('admin.products'))
            
        except Exception as e:
            flash(f'导入失败: {str(e)}', 'error')
    
    return render_template('admin/products_import.html')

# 示例文件下载
@admin_bp.route('/products/import/sample')
@login_required
def download_sample():
    """下载示例Excel文件"""
    import os
    from flask import send_file, current_app
    
    sample_file = os.path.join(current_app.root_path, 'static', 'files', 'product_import_template.xlsx')
    
    if os.path.exists(sample_file):
        return send_file(sample_file, 
                         as_attachment=True, 
                         download_name='产品导入模板.xlsx',
                         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    else:
        flash('示例文件不存在', 'error')
        return redirect(url_for('admin.products_import'))

# 订单管理
@admin_bp.route('/orders')
@login_required
def orders():
    """订单列表"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 筛选条件
    status = request.args.get('status', '')
    query_text = request.args.get('q', '')
    
    orders_query = Order.query
    
    if status:
        orders_query = orders_query.filter_by(status=status)
    
    if query_text:
        orders_query = orders_query.filter(
            (Order.order_no.contains(query_text)) |
            (Order.customer_name.contains(query_text)) |
            (Order.customer_phone.contains(query_text))
        )
    
    pagination = orders_query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/orders.html',
                         orders=pagination.items,
                         pagination=pagination,
                         status=status,
                         query=query_text)

@admin_bp.route('/orders/<int:order_id>')
@login_required
def order_detail(order_id):
    """订单详情"""
    order = Order.query.get_or_404(order_id)
    return render_template('admin/order_detail.html', order=order)

@admin_bp.route('/orders/<int:order_id>/status', methods=['POST'])
@login_required
def order_update_status(order_id):
    """更新订单状态"""
    status = request.form.get('status')
    if status:
        try:
            OrderService.update_order_status(order_id, status)
            flash('订单状态更新成功', 'success')
        except Exception as e:
            flash(f'更新失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.order_detail', order_id=order_id))

# 分类管理
@admin_bp.route('/categories')
@login_required
def categories():
    """分类列表"""
    categories = Category.query.order_by(Category.sort_order).all()
    return render_template('admin/categories.html', categories=categories)

@admin_bp.route('/categories/new', methods=['POST'])
@login_required
def category_new():
    """新增分类"""
    name = request.form.get('name')
    description = request.form.get('description')
    sort_order = request.form.get('sort_order', 0)
    
    if name:
        try:
            category = Category(
                name=name,
                description=description,
                sort_order=int(sort_order)
            )
            db.session.add(category)
            db.session.commit()
            flash('分类创建成功', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'创建失败: {str(e)}', 'error')
    
    return redirect(url_for('admin.categories'))

@admin_bp.route('/categories/<int:category_id>/delete', methods=['POST'])
@login_required
def category_delete(category_id):
    """删除分类"""
    category = Category.query.get_or_404(category_id)
    
    # 检查是否有产品使用此分类
    if category.products.count() > 0:
        flash('该分类下还有产品，无法删除', 'error')
    else:
        db.session.delete(category)
        db.session.commit()
        flash('分类删除成功', 'success')
    
    return redirect(url_for('admin.categories'))

# 系统设置
@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    """系统设置"""
    if request.method == 'POST':
        try:
            # 更新设置
            settings_data = {
                'email_enabled': request.form.get('email_enabled', 'false'),
                'sms_enabled': request.form.get('sms_enabled', 'false'),
                'notification_emails': request.form.get('notification_emails', ''),
                'admin_phones': request.form.get('admin_phones', ''),
                'site_name': request.form.get('site_name', '日用产品批发零售系统'),
                'site_title': request.form.get('site_title', '日用产品批发零售系统'),
                'company_name': request.form.get('company_name', ''),
                'company_phone': request.form.get('company_phone', ''),
                'company_email': request.form.get('company_email', ''),
                'company_address': request.form.get('company_address', ''),
                'copyright': request.form.get('copyright', ''),
                'icp': request.form.get('icp', ''),
            }
            
            for key, value in settings_data.items():
                setting = SystemSetting.query.filter_by(key=key).first()
                if setting:
                    setting.value = value
                else:
                    setting = SystemSetting(key=key, value=value)
                    db.session.add(setting)
            
            db.session.commit()
            flash('设置保存成功', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'保存失败: {str(e)}', 'error')
    
    # 获取设置
    settings = {}
    for setting in SystemSetting.query.all():
        settings[setting.key] = setting.value
    
    return render_template('admin/settings.html', settings=settings)

# 通知测试页面
@admin_bp.route('/notification-test')
@login_required
def notification_test():
    """通知测试页面"""
    return render_template('admin/notification_test.html')

# 删除图片
@admin_bp.route('/products/images/<int:image_id>/delete', methods=['POST'])
@login_required
def delete_product_image(image_id):
    """删除产品图片"""
    image = ProductImage.query.get_or_404(image_id)
    product_id = image.product_id

    try:
        # 删除物理文件
        # image.image_url 格式: /static/uploads/products/xxx.jpg
        # 需要构建完整路径
        if image.image_url.startswith('/static/'):
            # static文件
            image_path = os.path.join(current_app.root_path, image.image_url.lstrip('/'))
        else:
            # 相对路径
            image_path = os.path.join(current_app.root_path, image.image_url)

        if os.path.exists(image_path):
            os.remove(image_path)

        # 如果删除的是主图，需要设置另一个为主图
        if image.is_primary:
            other_images = ProductImage.query.filter(
                ProductImage.product_id == product_id,
                ProductImage.id != image_id
            ).first()
            if other_images:
                other_images.is_primary = True

        # 删除数据库记录
        db.session.delete(image)
        db.session.commit()

        # 判断是否是AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '图片删除成功'})
        else:
            flash('图片删除成功', 'success')
            return redirect(url_for('admin.product_edit', product_id=product_id))
    except Exception as e:
        db.session.rollback()

        # 判断是否是AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        else:
            flash(f'删除失败: {str(e)}', 'error')
            return redirect(url_for('admin.product_edit', product_id=product_id))

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

        # 判断是否是AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'message': '主图设置成功'})
        else:
            flash('主图设置成功', 'success')
            return redirect(url_for('admin.product_edit', product_id=product_id))
    except Exception as e:
        db.session.rollback()

        # 判断是否是AJAX请求
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': str(e)}), 500
        else:
            flash(f'设置失败: {str(e)}', 'error')
            return redirect(url_for('admin.product_edit', product_id=product_id))

# ==================== 数据统计 ====================

@admin_bp.route('/statistics')
@login_required
def statistics():
    """数据统计页面"""
    from datetime import datetime
    
    # 获取筛选参数
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    year = request.args.get('year', type=int, default=datetime.now().year)
    month = request.args.get('month', type=int)
    
    # 转换日期
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
    
    # 如果没有指定日期范围，默认显示本年或本月数据
    if not start_date and not end_date:
        if month:
            # 显示指定月份数据
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        else:
            # 显示本年数据
            start_date = datetime(year, 1, 1).date()
            end_date = datetime(year, 12, 31).date()
    
    # 获取统计数据
    stats = {
        'overview': StatisticsService.get_sales_overview(start_date, end_date),
        'product_sales_ratio': StatisticsService.get_product_sales_ratio(start_date, end_date),
        'customer_ranking': StatisticsService.get_customer_ranking(start_date, end_date),
        'best_selling': StatisticsService.get_best_selling_products(start_date, end_date),
        'slow_moving': StatisticsService.get_slow_moving_products(),
        'monthly_sales': StatisticsService.get_monthly_statistics(year, month).get('daily_sales', [])
    }
    
    return render_template('admin/statistics.html', 
                         stats=stats, 
                         current_year=year,
                         current_month=month or datetime.now().month,
                         start_date=start_date_str,
                         end_date=end_date_str)

# ==================== 报表下载 ====================

@admin_bp.route('/statistics/export/monthly/<int:year>/<int:month>')
@login_required
def export_monthly_report(year, month):
    """导出月报表"""
    try:
        file_path = StatisticsService.export_monthly_report(year, month)
        return send_file(file_path,
                        as_attachment=True,
                        download_name=f'月报表_{year}年{month}月.xlsx',
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'error')
        return redirect(url_for('admin.statistics'))

@admin_bp.route('/statistics/export/product-sales')
@login_required
def export_product_sales():
    """导出产品销售报表"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        file_path = StatisticsService.export_product_sales(start_date, end_date)
        return send_file(file_path,
                        as_attachment=True,
                        download_name=f'产品销售报表_{datetime.now().strftime("%Y%m%d")}.xlsx',
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'error')
        return redirect(url_for('admin.statistics'))

@admin_bp.route('/statistics/export/customer-ranking')
@login_required
def export_customer_ranking():
    """导出客户消费排名报表"""
    try:
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date() if start_date_str else None
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date() if end_date_str else None
        
        file_path = StatisticsService.export_customer_ranking(start_date, end_date)
        return send_file(file_path,
                        as_attachment=True,
                        download_name=f'客户消费排名_{datetime.now().strftime("%Y%m%d")}.xlsx',
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'error')
        return redirect(url_for('admin.statistics'))

@admin_bp.route('/statistics/export/best-selling')
@login_required
def export_best_selling():
    """导出畅销品报表"""
    try:
        from datetime import timedelta
        
        year = request.args.get('year', type=int)
        month = request.args.get('month', type=int)
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        # 根据参数确定日期范围
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        elif year and month:
            start_date = datetime(year, month, 1).date()
            if month == 12:
                end_date = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(year, month + 1, 1).date() - timedelta(days=1)
        else:
            # 默认当前月份
            now = datetime.now()
            start_date = datetime(now.year, now.month, 1).date()
            if now.month == 12:
                end_date = datetime(now.year + 1, 1, 1).date() - timedelta(days=1)
            else:
                end_date = datetime(now.year, now.month + 1, 1).date() - timedelta(days=1)
        
        data = StatisticsService.get_best_selling_products(start_date, end_date)
        file_path = StatisticsService.export_to_excel(data, f'畅销品报表_{datetime.now().strftime("%Y%m%d")}.xlsx')
        
        return send_file(file_path,
                        as_attachment=True,
                        download_name=f'畅销品报表_{datetime.now().strftime("%Y%m%d")}.xlsx',
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'error')
        return redirect(url_for('admin.statistics'))

@admin_bp.route('/statistics/export/slow-moving')
@login_required
def export_slow_moving():
    """导出滞销品报表"""
    try:
        data = StatisticsService.get_slow_moving_products()
        file_path = StatisticsService.export_to_excel(data, f'滞销品报表_{datetime.now().strftime("%Y%m%d")}.xlsx')
        
        return send_file(file_path,
                        as_attachment=True,
                        download_name=f'滞销品报表_{datetime.now().strftime("%Y%m%d")}.xlsx',
                        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    except Exception as e:
        flash(f'导出失败: {str(e)}', 'error')
        return redirect(url_for('admin.statistics'))

