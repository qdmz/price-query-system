"""
数据统计服务
提供销售额、产品比例、客户排名、畅销滞销品等统计功能
"""
from app.models import db, Order, OrderItem, Product
from datetime import datetime, timedelta
from sqlalchemy import func, desc, and_, or_
import pandas as pd


class StatisticsService:
    
    @staticmethod
    def get_sales_overview(start_date=None, end_date=None):
        """
        获取销售概况
        :param start_date: 开始日期 (datetime.date)
        :param end_date: 结束日期 (datetime.date)
        :return: dict
        """
        query = Order.query.filter(
            Order.status.in_(['confirmed', 'shipped', 'completed'])
        )
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        # 基础统计
        total_orders = query.count()
        total_sales = db.session.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.status.in_(['confirmed', 'shipped', 'completed']),
                Order.created_at >= start_date if start_date else True,
                Order.created_at <= end_date if end_date else True
            )
        ).scalar() or 0
        
        total_quantity = db.session.query(func.sum(Order.total_quantity)).filter(
            and_(
                Order.status.in_(['confirmed', 'shipped', 'completed']),
                Order.created_at >= start_date if start_date else True,
                Order.created_at <= end_date if end_date else True
            )
        ).scalar() or 0
        
        # 平均订单金额
        avg_order_amount = total_sales / total_orders if total_orders > 0 else 0
        
        return {
            'total_orders': total_orders,
            'total_sales': round(total_sales, 2),
            'total_quantity': int(total_quantity),
            'avg_order_amount': round(avg_order_amount, 2)
        }
    
    @staticmethod
    def get_product_sales_ratio(start_date=None, end_date=None, limit=10):
        """
        获取产品销售比例（按销售额排序）
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param limit: 返回数量限制
        :return: list of dict
        """
        # 查询每个产品的销售数据
        query = db.session.query(
            Product.id,
            Product.product_code,
            Product.name,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.subtotal).label('total_sales')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.status.in_(['confirmed', 'shipped', 'completed'])
        ).group_by(
            Product.id
        )
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        results = query.order_by(desc('total_sales')).limit(limit).all()
        
        return [
            {
                'product_id': r.id,
                'product_code': r.product_code,
                'product_name': r.name,
                'total_quantity': int(r.total_quantity),
                'total_sales': round(r.total_sales, 2)
            }
            for r in results
        ]
    
    @staticmethod
    def get_customer_ranking(start_date=None, end_date=None, limit=20):
        """
        获取客户消费排名
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param limit: 返回数量限制
        :return: list of dict
        """
        query = db.session.query(
            Order.customer_name,
            Order.customer_phone,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_amount'),
            func.sum(Order.total_quantity).label('total_quantity')
        ).filter(
            Order.status.in_(['confirmed', 'shipped', 'completed'])
        ).group_by(
            Order.customer_name,
            Order.customer_phone
        )
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        results = query.order_by(desc('total_amount')).limit(limit).all()
        
        return [
            {
                'customer_name': r.customer_name,
                'customer_phone': r.customer_phone,
                'order_count': r.order_count,
                'total_amount': round(r.total_amount, 2),
                'total_quantity': int(r.total_quantity),
                'avg_amount': round(r.total_amount / r.order_count, 2) if r.order_count > 0 else 0
            }
            for r in results
        ]
    
    @staticmethod
    def get_best_selling_products(start_date=None, end_date=None, limit=10):
        """
        获取畅销品（按销售数量排序）
        :param start_date: 开始日期
        :param end_date: 结束日期
        :param limit: 返回数量限制
        :return: list of dict
        """
        query = db.session.query(
            Product.id,
            Product.product_code,
            Product.name,
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.subtotal).label('total_sales'),
            func.count(func.distinct(Order.id)).label('order_count')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.status.in_(['confirmed', 'shipped', 'completed'])
        ).group_by(
            Product.id
        )
        
        if start_date:
            query = query.filter(Order.created_at >= start_date)
        if end_date:
            query = query.filter(Order.created_at <= end_date)
        
        results = query.order_by(desc('total_quantity')).limit(limit).all()
        
        return [
            {
                'product_id': r.id,
                'product_code': r.product_code,
                'product_name': r.name,
                'total_quantity': int(r.total_quantity),
                'total_sales': round(r.total_sales, 2),
                'order_count': r.order_count
            }
            for r in results
        ]
    
    @staticmethod
    def get_slow_moving_products(limit=20):
        """
        获取滞销品（长时间未售出的产品）
        :param limit: 返回数量限制
        :return: list of dict
        """
        # 获取所有有销售记录的产品
        sold_products = db.session.query(
            OrderItem.product_id,
            func.max(Order.created_at).label('last_sale_date')
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.status.in_(['confirmed', 'shipped', 'completed'])
        ).group_by(
            OrderItem.product_id
        ).subquery()
        
        # 30天前
        thirty_days_ago = datetime.now() - timedelta(days=30)
        
        # 查询30天前最后销售的产品（即滞销品）
        slow_moving = db.session.query(
            Product.id,
            Product.product_code,
            Product.name,
            Product.stock,
            sold_products.c.last_sale_date
        ).outerjoin(
            sold_products, Product.id == sold_products.c.product_id
        ).filter(
            or_(
                sold_products.c.last_sale_date < thirty_days_ago,
                sold_products.c.last_sale_date.is_(None)
            )
        ).order_by(
            sold_products.c.last_sale_date.asc().nullsfirst()
        ).limit(limit).all()
        
        return [
            {
                'product_id': r.id,
                'product_code': r.product_code,
                'product_name': r.name,
                'stock': r.stock,
                'last_sale_date': r.last_sale_date.strftime('%Y-%m-%d') if r.last_sale_date else '从未售出'
            }
            for r in slow_moving
        ]
    
    @staticmethod
    def get_monthly_statistics(year=None, month=None):
        """
        获取月报表
        :param year: 年份，不传则使用当前年份
        :param month: 月份，不传则使用当前月份
        :return: dict
        """
        now = datetime.now()
        year = year or now.year
        month = month or now.month
        
        # 计算月份的开始和结束日期
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            end_date = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # 销售概况
        overview = StatisticsService.get_sales_overview(
            start_date=start_date.date(),
            end_date=end_date.date()
        )
        
        # 每日销售趋势
        daily_sales = db.session.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_sales')
        ).filter(
            and_(
                Order.status.in_(['confirmed', 'shipped', 'completed']),
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).group_by(
            func.date(Order.created_at)
        ).order_by('date').all()
        
        # 畅销品
        best_selling = StatisticsService.get_best_selling_products(
            start_date=start_date.date(),
            end_date=end_date.date(),
            limit=10
        )
        
        # 客户排名
        customer_ranking = StatisticsService.get_customer_ranking(
            start_date=start_date.date(),
            end_date=end_date.date(),
            limit=10
        )
        
        return {
            'year': year,
            'month': month,
            'overview': overview,
            'daily_sales': [
                {
                    'date': r.date if isinstance(r.date, str) else r.date.strftime('%Y-%m-%d'),
                    'order_count': r.order_count,
                    'total_sales': round(r.total_sales, 2) if r.total_sales else 0
                }
                for r in daily_sales
            ],
            'best_selling': best_selling,
            'customer_ranking': customer_ranking
        }
    
    @staticmethod
    def get_yearly_summary(year=None):
        """
        获取年度汇总
        :param year: 年份，不传则使用当前年份
        :return: dict
        """
        now = datetime.now()
        year = year or now.year
        
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        
        # 月度销售趋势
        monthly_sales = db.session.query(
            func.extract('month', Order.created_at).label('month'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('total_sales')
        ).filter(
            and_(
                Order.status.in_(['confirmed', 'shipped', 'completed']),
                Order.created_at >= start_date,
                Order.created_at <= end_date
            )
        ).group_by(
            func.extract('month', Order.created_at)
        ).order_by('month').all()
        
        # 创建完整的12个月数据
        monthly_data = {m: {'order_count': 0, 'total_sales': 0} for m in range(1, 13)}
        for r in monthly_sales:
            month = int(r.month)
            monthly_data[month] = {
                'order_count': r.order_count,
                'total_sales': round(r.total_sales, 2) if r.total_sales else 0
            }
        
        return {
            'year': year,
            'monthly_sales': [
                {
                    'month': month,
                    'order_count': data['order_count'],
                    'total_sales': data['total_sales']
                }
                for month, data in sorted(monthly_data.items())
            ]
        }
    
    @staticmethod
    def export_to_excel(data, filename):
        """
        导出数据到Excel
        :param data: 要导出的数据（字典列表）
        :param filename: 文件名
        :return: 文件路径
        """
        df = pd.DataFrame(data)
        
        # 保存到临时目录
        import os
        temp_dir = '/tmp'
        file_path = os.path.join(temp_dir, filename)
        
        df.to_excel(file_path, index=False, engine='openpyxl')
        return file_path
    
    @staticmethod
    def export_monthly_report(year, month):
        """
        导出月报表
        :param year: 年份
        :param month: 月份
        :return: 文件路径
        """
        data = StatisticsService.get_monthly_statistics(year, month)
        
        # 创建多个工作表
        import os
        temp_dir = '/tmp'
        filename = f'monthly_report_{year}_{month:02d}.xlsx'
        file_path = os.path.join(temp_dir, filename)
        
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            # 概况
            overview_df = pd.DataFrame([data['overview']])
            overview_df.to_excel(writer, sheet_name='概况', index=False)
            
            # 每日销售
            daily_df = pd.DataFrame(data['daily_sales'])
            daily_df.to_excel(writer, sheet_name='每日销售', index=False)
            
            # 畅销品
            best_selling_df = pd.DataFrame(data['best_selling'])
            best_selling_df.to_excel(writer, sheet_name='畅销品', index=False)
            
            # 客户排名
            customer_df = pd.DataFrame(data['customer_ranking'])
            customer_df.to_excel(writer, sheet_name='客户排名', index=False)
        
        return file_path
    
    @staticmethod
    def export_product_sales(start_date=None, end_date=None):
        """
        导出产品销售报表
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 文件路径
        """
        data = StatisticsService.get_product_sales_ratio(start_date, end_date, limit=None)
        
        import os
        temp_dir = '/tmp'
        filename = f'product_sales_{datetime.now().strftime("%Y%m%d")}.xlsx'
        file_path = os.path.join(temp_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, engine='openpyxl')
        
        return file_path
    
    @staticmethod
    def export_customer_ranking(start_date=None, end_date=None):
        """
        导出客户消费排名报表
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return: 文件路径
        """
        data = StatisticsService.get_customer_ranking(start_date, end_date, limit=None)
        
        import os
        temp_dir = '/tmp'
        filename = f'customer_ranking_{datetime.now().strftime("%Y%m%d")}.xlsx'
        file_path = os.path.join(temp_dir, filename)
        
        df = pd.DataFrame(data)
        df.to_excel(file_path, index=False, engine='openpyxl')
        
        return file_path
