#!/usr/bin/env python
"""
创建产品占位图片
"""
from PIL import Image, ImageDraw, ImageFont
import os

# 创建占位图片目录
images_dir = os.path.join(os.path.dirname(__file__), 'app', 'static', 'images')
os.makedirs(images_dir, exist_ok=True)

# 创建占位图片
width, height = 400, 400
image = Image.new('RGB', (width, height), color='#e0e0e0')
draw = ImageDraw.Draw(image)

# 绘制边框
draw.rectangle([(10, 10), (width-10, height-10)], outline='#cccccc', width=2)

# 绘制文字（居中）
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 30)
except:
    font = ImageFont.load_default()

text = "产品图片"
text_bbox = draw.textbbox((0, 0), text, font=font)
text_width = text_bbox[2] - text_bbox[0]
text_height = text_bbox[3] - text_bbox[1]
text_x = (width - text_width) / 2
text_y = (height - text_height) / 2
draw.text((text_x, text_y), text, fill='#666666', font=font)

# 保存图片
output_file = os.path.join(images_dir, 'product-placeholder.jpg')
image.save(output_file, 'JPEG', quality=90)

print("=" * 60)
print("占位图片创建成功！")
print("=" * 60)
print(f"文件路径: {output_file}")
print(f"尺寸: {width}x{height}")
print("=" * 60)
