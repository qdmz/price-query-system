FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建上传目录
RUN mkdir -p app/static/uploads/products \
    && mkdir -p app/static/uploads/orders

# 暴露端口
EXPOSE 5000

# 设置环境变量
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# 启动命令
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "wsgi:app"]
