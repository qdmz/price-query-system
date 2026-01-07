# GitHub 发布指南

## 发布步骤

### 1. 在GitHub上创建仓库

访问：https://github.com/new

仓库配置：
- Repository name: `price-query-system`
- Description: `日用产品批发零售系统 - 基于Flask的产品价格查询和订单管理系统`
- Public/Private: 根据需求选择
- ⚠️ **不要**勾选 "Initialize this repository with a README"
- ⚠️ **不要**添加 .gitignore 或 license

点击 "Create repository"

### 2. 在本地添加远程仓库

```bash
# 添加远程仓库（替换 YOUR_USERNAME 为你的GitHub用户名）
git remote add origin https://github.com/YOUR_USERNAME/price-query-system.git

# 查看远程仓库配置
git remote -v
```

### 3. 推送代码到GitHub

```bash
# 第一次推送，设置上游分支
git push -u origin main

# 之后的推送只需要
git push
```

### 4. 验证推送成功

访问你的GitHub仓库页面，确认所有文件都已上传：
- https://github.com/YOUR_USERNAME/price-query-system

## 常见问题

### 如果遇到推送失败

1. **认证失败**
   - 使用 SSH 方式（推荐）：
     ```bash
     git remote set-url origin git@github.com:YOUR_USERNAME/price-query-system.git
     ```
   - 或使用 Personal Access Token：
     - 生成 token: https://github.com/settings/tokens
     - 推送时使用 token 作为密码

2. **分支名称问题**
   - 如果默认分支是 master 而不是 main：
     ```bash
     git branch -M main
     git push -u origin main
     ```

### 如果本地有未提交的更改

```bash
# 查看状态
git status

# 添加所有更改
git add .

# 提交更改
git commit -m "feat: 完善项目功能"

# 推送
git push
```

## 后续维护

### 克隆仓库到其他机器

```bash
git clone https://github.com/YOUR_USERNAME/price-query-system.git
cd price-query-system
```

### 创建分支进行开发

```bash
# 创建新分支
git checkout -b feature/new-feature

# 在分支上开发
git add .
git commit -m "feat: 添加新功能"
git push origin feature/new-feature
```

### 合并分支

```bash
# 切换到主分支
git checkout main

# 合并分支
git merge feature/new-feature

# 推送到远程
git push
```

## GitHub Actions（可选）

如果需要自动化测试和部署，可以创建 `.github/workflows/ci.yml`：

```yaml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    - name: Run tests
      run: |
        pytest
```
