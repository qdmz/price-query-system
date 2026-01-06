from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, SystemSetting

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """登录"""
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password) and user.is_active:
            login_user(user)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('admin.dashboard'))
        else:
            flash('用户名或密码错误', 'error')
    
    return render_template('auth/login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """登出"""
    logout_user()
    flash('已退出登录', 'info')
    return redirect(url_for('main.index'))

@auth_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    """修改密码"""
    if request.method == 'POST':
        old_password = request.form.get('old_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        # 验证旧密码
        if not current_user.check_password(old_password):
            flash('旧密码错误', 'error')
            return redirect(url_for('auth.change_password'))
        
        # 验证新密码
        if new_password != confirm_password:
            flash('两次输入的新密码不一致', 'error')
            return redirect(url_for('auth.change_password'))
        
        if len(new_password) < 6:
            flash('密码长度至少6位', 'error')
            return redirect(url_for('auth.change_password'))
        
        # 更新密码
        current_user.set_password(new_password)
        from app.models import db
        db.session.commit()
        
        flash('密码修改成功', 'success')
        return redirect(url_for('admin.dashboard'))
    
    return render_template('auth/change_password.html')
