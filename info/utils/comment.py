from flask import  session,current_app,g
from  info.models import  User
from functools import wraps

def do_rank(index):
    """根据index返回first second third"""
    if index == 1:
        return 'first'
    elif index == 2:
        return 'second'
    elif index ==3:
        return 'third'
    else:
        return ''


# view_func == news_detail
def user_login_data(view_func):
    # 提示：wrapper函数会拦截到传给被装饰的函数的参数
    # 提示 装饰器会修改被装饰的函数__name__属性
    # 解决 @wraps(view_func):会还原被装饰的函数
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        user_id = session.get('user_id', None)
        user = None
        if user_id:
            #     表示已经登陆
            try:
                user = User.query.get(user_id)
            except Exception as e:
                current_app.logger.error(e)
        g.user = user
        return  view_func(*args, **kwargs)
    return wrapper

# def user_login_data():
#
#     user_id = session.get('user_id', None)
#     user = None
#     if user_id:
#         #     表示已经登陆
#         try:
#             user = User.query.get(user_id)
#         except Exception as e:
#             current_app.logger.error(e)
#     return  user