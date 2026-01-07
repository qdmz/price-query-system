#!/usr/bin/env python
"""
数据初始化脚本

用法：
    python scripts/init_data.py --force  # 强制重新初始化所有数据（会删除现有数据）
    python scripts/init_data.py         # 只初始化缺失的数据（不删除现有数据）
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import click
from app import create_app, db
from app.models import User, Product, Order, Category, SystemSetting, ProductImage, OrderItem
from app.services.init_service import init_sample_data

@click.command()
@click.option('--force', is_flag=True, help='强制重新初始化所有数据（会删除现有数据）')
def init_data(force):
    """初始化示例数据"""

    app = create_app()

    with app.app_context():
        if force:
            click.echo(click.style('⚠️  警告：将删除所有现有数据！', fg='red', bold=True))

            if click.confirm('确认要删除所有数据并重新初始化吗？'):
                click.echo('正在删除现有数据...')

                # 删除数据（按照依赖关系顺序）
                OrderItem.query.delete()
                Order.query.delete()
                ProductImage.query.delete()
                Product.query.delete()
                Category.query.delete()
                SystemSetting.query.delete()

                # 保留管理员账户，重新初始化
                db.session.commit()

                click.echo('✓ 现有数据已删除')
            else:
                click.echo('操作已取消')
                return

        click.echo('\n' + '=' * 60)
        click.echo('开始初始化示例数据...')
        click.echo('=' * 60 + '\n')

        # 初始化示例数据
        init_sample_data()

        # 显示统计信息
        click.echo('\n' + '=' * 60)
        click.echo('数据统计')
        click.echo('=' * 60)
        click.echo(f'用户数量: {User.query.count()}')
        click.echo(f'分类数量: {Category.query.count()}')
        click.echo(f'产品数量: {Product.query.count()}')
        click.echo(f'产品图片数量: {ProductImage.query.count()}')
        click.echo(f'订单数量: {Order.query.count()}')
        click.echo(f'订单项数量: {OrderItem.query.count()}')
        click.echo(f'系统设置数量: {SystemSetting.query.count()}')
        click.echo('=' * 60 + '\n')

        click.echo(click.style('✓ 初始化完成！', fg='green', bold=True))
        click.echo('\n默认登录信息：')
        click.echo('  用户名: admin')
        click.echo('  密码: admin123')
        click.echo('\n提示：请在系统设置中修改管理员密码！')

if __name__ == '__main__':
    init_data()
