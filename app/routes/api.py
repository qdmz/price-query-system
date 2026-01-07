from flask import Blueprint, request, jsonify, current_app
from app.models import db, Product, ProductImage, Order, OrderItem
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.services.notification_service import NotificationService
from datetime import datetime

api_bp = Blueprint('api', __name__)

# 产品相关API
@api_bp.route('/products/search', methods=['GET'])
def api_search_products():
    """搜索产品API"""
    query = request.args.get('q', '')
    category_id = request.args.get('category_id', type=int)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # 构建查询
    products_query = Product.query.filter_by(status='active')
    
    if query:
        products_query = products_query.filter(
            (Product.name.contains(query)) |
            (Product.product_code.contains(query)) |
            (Product.barcode.contains(query)) |
            (Product.model.contains(query))
        )
    
    if category_id:
        products_query = products_query.filter_by(category_id=category_id)
    
    # 分页
    pagination = products_query.order_by(Product.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    products_data = []
    for product in pagination.items:
        images = [img.image_url for img in product.images.order_by(ProductImage.sort_order)]
        primary_image = images[0] if images else None
        
        products_data.append({
            'id': product.id,
            'product_code': product.product_code,
            'barcode': product.barcode,
            'name': product.name,
            'model': product.model,
            'specification': product.specification,
            'unit': product.unit,
            'retail_price': product.retail_price,
            'wholesale_price': product.wholesale_price,
            'wholesale_min_qty': product.wholesale_min_qty,
            'stock': product.stock,
            'description': product.description,
            'primary_image': primary_image,
            'all_images': images
        })
    
    return jsonify({
        'success': True,
        'products': products_data,
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': page
    })

@api_bp.route('/products/<int:product_id>', methods=['GET'])
def api_get_product(product_id):
    """获取单个产品详情"""
    product = Product.query.get_or_404(product_id)
    images = [img.image_url for img in product.images.order_by(ProductImage.sort_order)]
    
    return jsonify({
        'success': True,
        'product': {
            'id': product.id,
            'product_code': product.product_code,
            'barcode': product.barcode,
            'name': product.name,
            'model': product.model,
            'specification': product.specification,
            'unit': product.unit,
            'retail_price': product.retail_price,
            'wholesale_price': product.wholesale_price,
            'wholesale_min_qty': product.wholesale_min_qty,
            'stock': product.stock,
            'description': product.description,
            'images': images,
            'category_id': product.category_id
        }
    })

# 订单相关API
@api_bp.route('/orders', methods=['POST'])
def api_create_order():
    """创建订单API"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('customer_name'):
            return jsonify({
                'success': False,
                'message': '客户姓名不能为空'
            }), 400
        
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({
                'success': False,
                'message': '订单商品不能为空'
            }), 400
        
        # 创建订单
        order = OrderService.create_order(data)
        
        # 构建返回数据
        items_data = []
        for item in order.items:
            items_data.append({
                'product_id': item.product_id,
                'product_name': item.product_name,
                'product_code': item.product_code,
                'quantity': item.quantity,
                'unit_price': item.unit_price,
                'subtotal': item.subtotal
            })
        
        return jsonify({
            'success': True,
            'order': {
                'id': order.id,
                'order_no': order.order_no,
                'customer_name': order.customer_name,
                'customer_phone': order.customer_phone,
                'customer_email': order.customer_email,
                'customer_address': order.customer_address,
                'total_amount': order.total_amount,
                'total_quantity': order.total_quantity,
                'status': order.status,
                'notes': order.notes,
                'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'items': items_data
            }
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'创建订单失败: {str(e)}'
        }), 500

@api_bp.route('/orders/<order_no>', methods=['GET'])
def api_get_order(order_no):
    """获取订单详情"""
    order = Order.query.filter_by(order_no=order_no).first_or_404()
    
    items_data = []
    for item in order.items:
        items_data.append({
            'product_id': item.product_id,
            'product_name': item.product_name,
            'product_code': item.product_code,
            'quantity': item.quantity,
            'unit_price': item.unit_price,
            'subtotal': item.subtotal
        })
    
    return jsonify({
        'success': True,
        'order': {
            'id': order.id,
            'order_no': order.order_no,
            'customer_name': order.customer_name,
            'customer_phone': order.customer_phone,
            'customer_email': order.customer_email,
            'customer_address': order.customer_address,
            'total_amount': order.total_amount,
            'total_quantity': order.total_quantity,
            'status': order.status,
            'notes': order.notes,
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'items': items_data
        }
    })

# 统计API
@api_bp.route('/statistics', methods=['GET'])
def api_statistics():
    """获取统计信息"""
    from app.services.order_service import OrderService
    
    # 产品统计
    total_products = Product.query.count()
    active_products = Product.query.filter_by(status='active').count()
    out_of_stock = Product.query.filter(Product.stock == 0).count()
    
    # 订单统计
    order_stats = OrderService.get_order_statistics()
    
    return jsonify({
        'success': True,
        'statistics': {
            'products': {
                'total': total_products,
                'active': active_products,
                'out_of_stock': out_of_stock
            },
            'orders': order_stats
        }
    })

# 测试通知API
@api_bp.route('/admin/test-notification/email', methods=['POST'])
def api_test_email_notification():
    """测试邮件通知"""
    try:
        data = request.get_json()
        
        to = data.get('to')
        subject = data.get('subject', '测试邮件')
        body = data.get('body', '')
        
        if not to:
            return jsonify({
                'success': False,
                'message': '收件人邮箱不能为空'
            }), 400
        
        # 发送测试邮件
        notification_service = NotificationService()
        result = notification_service.send_email(to, subject, body)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '测试邮件发送成功！请检查收件箱。'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'邮件发送失败: {result.get("message", "未知错误")}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送失败: {str(e)}'
        }), 500

@api_bp.route('/admin/test-notification/sms', methods=['POST'])
def api_test_sms_notification():
    """测试短信通知"""
    try:
        data = request.get_json()
        
        to = data.get('to')
        body = data.get('body', '')
        
        if not to:
            return jsonify({
                'success': False,
                'message': '收件人手机号不能为空'
            }), 400
        
        # 发送测试短信
        notification_service = NotificationService()
        result = notification_service.send_sms(to, body)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': '测试短信发送成功！'
            })
        else:
            return jsonify({
                'success': False,
                'message': f'短信发送失败: {result.get("message", "未知错误")}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'发送失败: {str(e)}'
        }), 500
