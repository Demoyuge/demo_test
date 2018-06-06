#后台管理
import time,datetime
from info.models import User
from info.utils.comment import user_login_data
from  . import  admin_blue
from flask import request, render_template, current_app, session,redirect,url_for,g



@admin_blue.route('/user_count')
def user_count():

    # 用户总数
    total_count = 0
    try:
        total_count = User.query.filter(User.is_admin==False).count()
    except Exception as e:
        current_app.logger.error(e)
    # 月新增数
    month_count = 0
    # 计算每月开始时间 比如：2018-06-01 00：00：00
    t = time.localtime()
    # 计算每月开始时间字符串
    month_begin = '%d-%02d-01' %(t.tm_year, t.tm_mon)

    # 计算每月开始时间对象
    month_begin_data = datetime.datetime.strptime(month_begin,'%Y-%m-%d')
    try:
        month_count = User.query.filter(User.is_admin == False, User.create_time > month_begin_data).count()
    except Exception as e:
        current_app.logger.error(e)

    # 日新增数
    day_count = 0
    # 计算当天的开始时间 比如：2018-06-04 00：00：00
    t = time.localtime()
    day_begin = '%d-%02d-%02d' % (t.tm_year, t.tm_mon, t.tm_mday)
    day_begin_date = datetime.datetime.strptime(day_begin, '%Y-%m-%d')
    try:
        day_count = User.query.filter(User.is_admin == False, User.create_time > day_begin_date).count()
    except Exception as e:
        current_app.logger.error(e)

    context = {
        'total_count': total_count,
        'month_count': month_count,
        'day_count': day_count
    }

    return render_template('admin/user_count.html', context=context)



@admin_blue.route('/')
@user_login_data
def admin_index():
    user = g.user
    if not user:
        return  redirect(url_for('admin.admin_login'))
    context = {
        'user':user.to_dict() if user else None
    }
    return  render_template('admin/index.html' ,context = context)
#两种请求 一种渲染
#一种登录
@admin_blue.route('/login',methods = ['GET','POST'])
def admin_login():
    if request.method == 'GET':
        user_id = session.get('user_id', None)
        is_admin = session.get('is_admin', False)
        if user_id and is_admin:
            return redirect(url_for('admin.admin_index'))
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