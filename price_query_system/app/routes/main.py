from flask import Blueprint, render_template, request, jsonify
from app.models import Product, Category, Order, SystemSetting

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    """首页 - 产品查询页面"""
    categories = Category.query.all()
    return render_template('index.html', categories=categories)

@main_bp.route('/search')
def search():
    """搜索产品"""
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
    
    # 返回JSON或HTML
    if request.headers.get('Content-Type') == 'application/json' or request.args.get('format') == 'json':
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
            'products': products_data,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        })
    
    return render_template('search_results.html', 
                         products=pagination.items,
                         pagination=pagination,
                         query=query,
                         category_id=category_id)

@main_bp.route('/product/<int:product_id>')
def product_detail(product_id):
    """产品详情页"""
    product = Product.query.get_or_404(product_id)
    images = product.images.order_by(ProductImage.sort_order).all()
    primary_image = images[0] if images else None
    
    return render_template('product_detail.html',
                         product=product,
                         images=images,
                         primary_image=primary_image)

@main_bp.route('/cart')
def cart():
    """购物车页面"""
    return render_template('cart.html')

@main_bp.route('/order')
def order():
    """订单页面"""
    return render_template('order.html')

@main_bp.route('/order/success/<order_no>')
def order_success(order_no):
    """订单成功页面"""
    order = Order.query.filter_by(order_no=order_no).first_or_404()
    return render_template('order_success.html', order=order)
