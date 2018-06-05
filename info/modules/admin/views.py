#后台管理
from info.models import User
from  . import  admin_blue
from flask import request, render_template, current_app, session,redirect,url_for


@admin_blue.route('/')
def admin_index():
    return  render_template('admin/index.html')
#两种请求 一种渲染
#一种登录
@admin_blue.route('/login',methods = ['GET','POST'])
def admin_login():
    if request.method == 'GET':
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return  render_template('admin/login.html')
        return  render_template('admin/login.html')
    if request.method == 'POST':
        #获取参数
        username = request.form.get('username')
        password = request.form.get('password')

        #2.校验参数
        if not all([username,password]):
            return  render_template('admin/login.html',errmsg="缺少参数")
        #3.查询当前登录用户是否存在
        try:
            user = User.query.filter(User.nick_name==username).first()
        except Exception as e:
            current_app.logger.error(e)
            return  render_template('admin/login.html',errmsg ="查询失败")

        #4.对比当前要登录的用户密码
        if not user:
            return render_template('admin/login.html', errmsg='用户名或者密码错误')
        if not user.check_password(password):
            return render_template('admin/login.html',errmsg ='用户名或者密码错误')
        #5.将状态保持信息写入到session
        session['user_id'] = user.id
        session['nick_name'] = user.nick_name
        session['mobile'] = user.mobile
        session['is_admin'] = user.is_admin

        #6.响应登录结果
        # return  render_template('admin/index.html',errmsg="用户名或者密码错误")
        return  redirect(url_for('admin.admin_index'))