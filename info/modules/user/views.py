#个人中心
from . import  user_blue
from flask import render_template, g, redirect, url_for, request,jsonify,session
from  info.utils.comment import user_login_data
from  info import response_code,db
@user_blue.route('/base_info',methods =['GET','POST'])
@user_login_data
def base_info():

    user = g.user
    if not user:
        return  redirect(url_for('index.index'))
    if request.method =='GET':
        context = {
            'user':user
        }
        return render_template('news/user_base_info.html', context=context)

    if request.method == 'POST':
        #获取参数
        nick_name = request.json.get('nick_name')
        signature = request.json.get('signature')
        gender = request.json.get('gender')
        #校验参数
        if not all([nick_name,signature,gender]):
            return jsonify(errno=response_code.RET.PARAMERR,errmsg ="缺少参数")
        if gender not in['MAN','WOMAN']:
            return jsonify(errno=response_code.RET.PARAMERR,errmsg="参数错误")
        # 修改用户信息
            user.signature = signature
            user.nick_name = nick_name
            user.gender = gender

            try:
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                current_app.logger.error(e)
                return jsonify(errno=response_code.RET.DBERR, errmsg="修改用户资料错误")
        #保持状态
        session['nick_name'] = nick_name

        return jsonify(errno=response_code.RET.OK, errmsg="正确")

@user_blue.route('/info')
@user_login_data
def user_info():
    """个人中心入口"""
    user = g.user
    if not user:
      return  redirect(url_for('index.index'))
    context = {
        'user':user
    }
    return  render_template('news/user.html',context=context)