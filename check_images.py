from app import create_app
from app.models import ProductImage

app = create_app()
with app.app_context():
    images = ProductImage.query.limit(5).all()
    print('图片URL示例:')
    if images:
        for img in images:
            print(f'  {img.id}: {img.image_url}')
    else:
        print('  暂无图片数据')
