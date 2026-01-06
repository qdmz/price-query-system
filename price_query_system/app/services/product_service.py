from app.models import db, Product, ProductImage, Category
from flask import current_app, request
import os
import requests
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

class ProductService:
    
    @staticmethod
    def allowed_file(filename):
        """检查文件扩展名是否允许"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']
    
    @staticmethod
    def save_product_image(file, product_id):
        """保存产品图片"""
        if file and ProductService.allowed_file(file.filename):
            # 生成唯一文件名
            filename = secure_filename(file.filename)
            ext = filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{product_id}_{uuid.uuid4().hex[:8]}.{ext}"
            
            # 保存文件
            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
            filepath = os.path.join(upload_dir, unique_filename)
            file.save(filepath)
            
            # 返回相对路径
            return f'/static/uploads/products/{unique_filename}'
        return None
    
    @staticmethod
    def download_image_from_url(url, product_id):
        """从URL下载图片"""
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                # 获取文件扩展名
                content_type = response.headers.get('content-type', '')
                ext_map = {
                    'image/jpeg': 'jpg',
                    'image/jpg': 'jpg',
                    'image/png': 'png',
                    'image/gif': 'gif',
                    'image/webp': 'webp'
                }
                ext = ext_map.get(content_type, 'jpg')
                
                # 生成唯一文件名
                unique_filename = f"{product_id}_{uuid.uuid4().hex[:8]}.{ext}"
                
                # 保存文件
                upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'products')
                filepath = os.path.join(upload_dir, unique_filename)
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                return f'/static/uploads/products/{unique_filename}'
        except Exception as e:
            print(f"下载图片失败: {str(e)}")
        return None
    
    @staticmethod
    def create_product(data):
        """创建产品"""
        product = Product(
            product_code=data.get('product_code'),
            barcode=data.get('barcode'),
            name=data.get('name'),
            model=data.get('model'),
            specification=data.get('specification'),
            unit=data.get('unit', '件'),
            retail_price=float(data.get('retail_price', 0)),
            wholesale_price=float(data.get('wholesale_price', 0)),
            wholesale_min_qty=int(data.get('wholesale_min_qty', 1)),
            stock=int(data.get('stock', 0)),
            description=data.get('description'),
            category_id=data.get('category_id')
        )
        db.session.add(product)
        db.session.commit()
        return product
    
    @staticmethod
    def update_product(product_id, data):
        """更新产品"""
        product = Product.query.get_or_404(product_id)
        
        product.product_code = data.get('product_code', product.product_code)
        product.barcode = data.get('barcode', product.barcode)
        product.name = data.get('name', product.name)
        product.model = data.get('model', product.model)
        product.specification = data.get('specification', product.specification)
        product.unit = data.get('unit', product.unit)
        product.retail_price = float(data.get('retail_price', product.retail_price))
        product.wholesale_price = float(data.get('wholesale_price', product.wholesale_price))
        product.wholesale_min_qty = int(data.get('wholesale_min_qty', product.wholesale_min_qty))
        product.stock = int(data.get('stock', product.stock))
        product.description = data.get('description', product.description)
        product.category_id = data.get('category_id', product.category_id)
        product.updated_at = datetime.utcnow()
        
        db.session.commit()
        return product
    
    @staticmethod
    def delete_product(product_id):
        """删除产品"""
        product = Product.query.get_or_404(product_id)
        # 删除产品图片
        for image in product.images:
            # 删除物理文件
            try:
                image_path = os.path.join(current_app.root_path, image.image_url.lstrip('/'))
                if os.path.exists(image_path):
                    os.remove(image_path)
            except:
                pass
        db.session.delete(product)
        db.session.commit()
        return True
    
    @staticmethod
    def search_products(query):
        """搜索产品"""
        return Product.query.filter(
            (Product.name.contains(query)) |
            (Product.product_code.contains(query)) |
            (Product.barcode.contains(query)) |
            (Product.model.contains(query))
        ).filter_by(status='active').all()
    
    @staticmethod
    def import_products_from_excel(file):
        """从Excel批量导入产品"""
        import pandas as pd
        
        # 读取Excel文件
        df = pd.read_excel(file)
        
        success_count = 0
        error_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                # 检查必填字段
                if not pd.notna(row.get('货号')) or not pd.notna(row.get('产品名称')):
                    errors.append(f"第{index+2}行: 缺少必填字段（货号或产品名称）")
                    error_count += 1
                    continue
                
                # 检查货号是否已存在
                if Product.query.filter_by(product_code=str(row['货号'])).first():
                    errors.append(f"第{index+2}行: 货号 {row['货号']} 已存在")
                    error_count += 1
                    continue
                
                # 创建产品
                product = Product(
                    product_code=str(row['货号']),
                    barcode=str(row.get('条码', '')) if pd.notna(row.get('条码')) else '',
                    name=str(row['产品名称']),
                    model=str(row.get('型号', '')) if pd.notna(row.get('型号')) else '',
                    specification=str(row.get('规格', '')) if pd.notna(row.get('规格')) else '',
                    unit=str(row.get('单位', '件')) if pd.notna(row.get('单位')) else '件',
                    retail_price=float(row.get('零售价', 0)) if pd.notna(row.get('零售价')) else 0,
                    wholesale_price=float(row.get('批发价', 0)) if pd.notna(row.get('批发价')) else 0,
                    wholesale_min_qty=int(row.get('批发最小数量', 1)) if pd.notna(row.get('批发最小数量')) else 1,
                    stock=int(row.get('库存', 0)) if pd.notna(row.get('库存')) else 0,
                    description=str(row.get('描述', '')) if pd.notna(row.get('描述')) else ''
                )
                
                db.session.add(product)
                success_count += 1
                
            except Exception as e:
                errors.append(f"第{index+2}行: {str(e)}")
                error_count += 1
        
        db.session.commit()
        
        return {
            'success_count': success_count,
            'error_count': error_count,
            'errors': errors
        }
