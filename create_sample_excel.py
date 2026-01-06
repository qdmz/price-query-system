#!/usr/bin/env python
"""
创建产品导入示例Excel文件
"""
import pandas as pd
import os

# 示例数据
sample_data = [
    {
        '货号': 'SP001',
        '条码': '6901234567890',
        '产品名称': '牙膏-薄荷味',
        '型号': 'Model-1001',
        '规格': '120g',
        '单位': '支',
        '零售价': 12.5,
        '批发价': 10.0,
        '批发最小数量': 2,
        '库存': 500,
        '描述': '清新薄荷味牙膏，有效清洁口腔'
    },
    {
        '货号': 'SP002',
        '条码': '6901234567891',
        '产品名称': '洗发水-去屑型',
        '型号': 'Model-2001',
        '规格': '400ml',
        '单位': '瓶',
        '零售价': 38.0,
        '批发价': 32.0,
        '批发最小数量': 3,
        '库存': 200,
        '描述': '去屑洗发水，适用于所有发质'
    },
    {
        '货号': 'SP003',
        '条码': '6901234567892',
        '产品名称': '洗衣液-薰衣草',
        '型号': 'Model-3001',
        '规格': '2L',
        '单位': '瓶',
        '零售价': 25.0,
        '批发价': 20.0,
        '批发最小数量': 5,
        '库存': 300,
        '描述': '薰衣草香洗衣液，温和不伤手'
    },
    {
        '货号': 'SP004',
        '条码': '6901234567893',
        '产品名称': '毛巾-纯棉',
        '型号': 'Model-4001',
        '规格': '30x70cm',
        '单位': '条',
        '零售价': 8.5,
        '批发价': 7.0,
        '批发最小数量': 10,
        '库存': 600,
        '描述': '纯棉毛巾，柔软舒适'
    },
    {
        '货号': 'SP005',
        '条码': '6901234567894',
        '产品名称': '纸巾-抽纸-3层',
        '型号': 'Model-5001',
        '规格': '120抽x3包',
        '单位': '提',
        '零售价': 12.0,
        '批发价': 10.0,
        '批发最小数量': 2,
        '库存': 500,
        '描述': '3层加厚抽纸，纸质柔软'
    }
]

# 创建DataFrame
df = pd.DataFrame(sample_data)

# 确保app/static/files目录存在
files_dir = os.path.join(os.path.dirname(__file__), 'app', 'static', 'files')
os.makedirs(files_dir, exist_ok=True)

# 保存为Excel文件
output_file = os.path.join(files_dir, 'product_import_template.xlsx')
df.to_excel(output_file, index=False, engine='openpyxl')

print("=" * 60)
print("示例Excel文件创建成功！")
print("=" * 60)
print(f"文件路径: {output_file}")
print(f"文件名: product_import_template.xlsx")
print(f"包含示例数据: {len(sample_data)} 条")
print("=" * 60)
