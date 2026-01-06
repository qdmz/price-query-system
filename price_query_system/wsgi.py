import os
from app import create_app

# 根据环境变量自动选择配置
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    app.run()
