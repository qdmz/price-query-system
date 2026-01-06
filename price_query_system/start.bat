@echo off
chcp 65001 >nul
echo ===================================
echo 日用产品批发零售系统
echo ===================================
echo.

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker 未安装，请先安装 Docker Desktop
    pause
    exit /b 1
)

REM 检查 Docker Compose 是否安装
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker Compose 未安装，请先安装 Docker Compose
    pause
    exit /b 1
)

REM 检查 .env 文件
if not exist .env (
    echo 创建 .env 文件...
    copy .env.example .env
    echo 已创建 .env 文件，请根据需要修改配置
)

REM 构建并启动服务
echo 构建并启动服务...
docker-compose up -d

REM 等待数据库启动
echo 等待数据库启动...
timeout /t 10 /nobreak >nul

REM 检查服务状态
echo.
echo ===================================
echo 服务状态
echo ===================================
docker-compose ps

echo.
echo ===================================
echo 访问信息
echo ===================================
echo 前台页面: http://localhost:5000
echo 后台管理: http://localhost:5000/admin/dashboard
echo 默认账号: admin
echo 默认密码: admin123
echo.
echo 查看日志: docker-compose logs -f web
echo 停止服务: docker-compose down
echo ===================================
pause
