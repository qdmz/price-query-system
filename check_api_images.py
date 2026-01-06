#!/usr/bin/env python
"""检查API返回的产品图片信息"""
import requests
import json

# 测试API
url = "http://localhost:5000/api/products/search?page=1&per_page=5"
response = requests.get(url)
data = response.json()

print("=== API返回数据示例 ===")
print(json.dumps(data['products'][:3], indent=2, ensure_ascii=False))

print("\n=== 图片URL检查 ===")
for product in data['products'][:3]:
    print(f"\n产品: {product['name']}")
    print(f"  主图: {product['primary_image']}")
    print(f"  所有图片: {len(product['all_images'])} 张")
    
    # 测试图片URL
    img_url = f"http://localhost:5000{product['primary_image']}"
    try:
        img_response = requests.head(img_url, timeout=5)
        print(f"  状态码: {img_response.status_code}")
        print(f"  Content-Type: {img_response.headers.get('Content-Type', 'N/A')}")
        print(f"  Content-Length: {img_response.headers.get('Content-Length', 'N/A')}")
    except Exception as e:
        print(f"  访问失败: {e}")
