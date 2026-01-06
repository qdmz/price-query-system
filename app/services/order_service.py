from app.models import db, Order, OrderItem, Product
from app.services.notification_service import NotificationService
from datetime import datetime
import random
import string

class OrderService:
    
    @staticmethod
    def generate_order_no():
        """生成订单号"""
        date_str = datetime.now().strftime('%Y%m%d')
        random_str = ''.join(random.choices(string.digits, k=4))
        return f"ORD{date_str}{random_str}"
    
    @staticmethod
    def create_order(data):
        """创建订单"""
        from flask import g
        
        # 生成订单号
        order_no = OrderService.generate_order_no()
        
        # 计算总金额和总数量
        items = data.get('items', [])
        total_amount = 0
        total_quantity = 0
        
        # 验证商品并计算价格
        order_items = []
        for item in items:
            product = Product.query.get(item['product_id'])
            if not product:
                raise ValueError(f"商品ID {item['product_id']} 不存在")
            
            quantity = item['quantity']
            # 根据数量判断使用零售价还是批发价
            unit_price = product.wholesale_price if quantity >= product.wholesale_min_qty else product.retail_price
            subtotal = unit_price * quantity
            
            total_amount += subtotal
            total_quantity += quantity
            
            order_items.append({
                'product': product,
                'quantity': quantity,
                'unit_price': unit_price,
                'subtotal': subtotal
            })
        
        # 创建订单
        order = Order(
            order_no=order_no,
            customer_name=data.get('customer_name'),
            customer_phone=data.get('customer_phone'),
            customer_email=data.get('customer_email'),
            customer_address=data.get('customer_address'),
            total_amount=total_amount,
            total_quantity=total_quantity,
            notes=data.get('notes'),
            user_id=g.user.id if g.user.is_authenticated else None
        )
        
        db.session.add(order)
        db.session.flush()  # 获取order.id
        
        # 创建订单明细
        for item_data in order_items:
            item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                product_name=item_data['product'].name,
                product_code=item_data['product'].product_code,
                quantity=item_data['quantity'],
                unit_price=item_data['unit_price'],
                subtotal=item_data['subtotal']
            )
            db.session.add(item)
        
        db.session.commit()
        
        # 发送通知
        try:
            NotificationService.notify_new_order(order)
        except Exception as e:
            print(f"发送通知失败: {str(e)}")
        
        return order
    
    @staticmethod
    def update_order_status(order_id, status):
        """更新订单状态"""
        order = Order.query.get_or_404(order_id)
        order.status = status
        order.updated_at = datetime.utcnow()
        db.session.commit()
        return order
    
    @staticmethod
    def get_order_statistics():
        """获取订单统计信息"""
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='pending').count()
        confirmed_orders = Order.query.filter_by(status='confirmed').count()
        completed_orders = Order.query.filter_by(status='completed').count()
        cancelled_orders = Order.query.filter_by(status='cancelled').count()
        
        # 计算总销售额
        total_sales = db.session.query(db.func.sum(Order.total_amount)).filter(
            Order.status.in_(['confirmed', 'shipped', 'completed'])
        ).scalar() or 0
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'confirmed_orders': confirmed_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders,
            'total_sales': total_sales
        }
