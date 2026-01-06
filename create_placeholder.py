#!/usr/bin/env python
"""创建产品图片占位图"""
from PIL import Image, ImageDraw, ImageFont
import os

# 创建占位图目录
os.makedirs('app/static/images', exist_ok=True)

# 创建400x400的占位图
width, height = 400, 400
img = Image.new('RGB', (width, height), color='#f8f9fa')
draw = ImageDraw.Draw(img)

# 绘制边框
draw.rectangle([(10, 10), (width-10, height-10)], outline='#dee2e6', width=2)

# 绘制中间的图标（简单的相机图标）
draw.rectangle([(160, 140), (240, 220)], outline='#6c757d', width=3)
draw.rectangle([(170, 230), (230, 235)], fill='#6c757d')
draw.circle((200, 180), 10, outline='#6c757d', width=3)

# 添加文字
text = "产品图片"
font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
text_width = draw.textlength(text, font=font)
draw.text(((width - text_width) / 2, 260), text, fill='#6c757d', font=font)

# 保存图片
img.save('app/static/images/product-placeholder.jpg', 'JPEG', quality=90)
print("✓ 产品图片占位图已创建: app/static/images/product-placeholder.jpg")
