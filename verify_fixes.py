#!/usr/bin/env python
"""
验证修复功能
"""
import os
import sys

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if os.path.exists(filepath):
        print(f"✓ {description}: {filepath}")
        return True
    else:
        print(f"✗ {description}: {filepath} (不存在)")
        return False

def main():
    print("=" * 60)
    print("验证修复功能")
    print("=" * 60)
    
    results = []
    
    # 检查示例Excel文件
    print("\n1. 检查示例Excel文件:")
    results.append(check_file_exists(
        'app/static/files/product_import_template.xlsx',
        '产品导入示例文件'
    ))
    
    # 检查占位图片
    print("\n2. 检查占位图片:")
    results.append(check_file_exists(
        'app/static/images/product-placeholder.jpg',
        '产品占位图片'
    ))
    
    # 检查images目录
    print("\n3. 检查目录结构:")
    results.append(check_file_exists(
        'app/static/images',
        'images目录'
    ))
    results.append(check_file_exists(
        'app/static/files',
        'files目录'
    ))
    results.append(check_file_exists(
        '/tmp/uploads',
        '临时上传目录'
    ))
    
    # 检查代码中的路由
    print("\n4. 检查代码路由:")
    with open('app/routes/admin.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if "download_sample" in content:
            print("✓ 示例文件下载路由已添加")
            results.append(True)
        else:
            print("✗ 示例文件下载路由未找到")
            results.append(False)
    
    with open('app/__init__.py', 'r', encoding='utf-8') as f:
        content = f.read()
        if "serve_upload_file" in content:
            print("✓ 上传文件服务路由已添加")
            results.append(True)
        else:
            print("✗ 上传文件服务路由未找到")
            results.append(False)
    
    # 检查导入页面
    print("\n5. 检查导入页面:")
    with open('app/templates/admin/products_import.html', 'r', encoding='utf-8') as f:
        content = f.read()
        if "download_sample" in content:
            print("✓ 下载按钮链接已更新")
            results.append(True)
        else:
            print("✗ 下载按钮链接未更新")
            results.append(False)
    
    # 统计结果
    print("\n" + "=" * 60)
    passed = sum(results)
    total = len(results)
    if passed == total:
        print(f"✓ 所有检查通过！({passed}/{total})")
        print("=" * 60)
        print("\n修复验证成功！")
        print("\n下一步：")
        print("1. 重启Flask应用: python app.py")
        print("2. 访问产品导入页面测试下载功能")
        print("3. 访问产品管理页面测试图片显示")
        return 0
    else:
        print(f"✗ 部分检查失败！({passed}/{total})")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())
