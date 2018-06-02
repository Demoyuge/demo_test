#新闻详情：收藏，评论点赞
from info.utils.comment import user_login_data
from . import news_blue
from flask import render_template, session, current_app, abort, g, jsonify, request
from info.models import User,News
from info import  constants,db,response_code
from info.utils.comment import  user_login_data


@news_blue.route('/news_collect',methods=['POST'])
@user_login_data
def news_collect():
    """新闻收藏和取消收藏"""
    user = g.user
    if not user:
        return jsonify(errno = response_code.RET.SESSIONERR,errmsg = '用户未登陆')
    # 2接受参数
    json_dict = request.json
    news_id = json_dict.get('news_id')
    action = json_dict.get('action')
    #3校验参数
    if not all([news_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    # 4待收藏的新闻信息
    if action not in ['collect','cancel_collect']:
        return  jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询新闻数据失败')
    if not news:
        return jsonify(errno=response_code.RET.NODATA, errmsg='查询新闻不存在')

    # 5收藏新闻
    if action == 'collect':
        # 如果该新闻没有被收藏就设置到用户的收藏列表
        if news not in user.collection_news:
            user.collection_news.append(news)
    else:
        if news in user.collection_news:
           user.collection_news.remove(news)

    # user.collection_news.append(news)
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='操作失败')
    # 6.响应结果
    return jsonify(errno=response_code.RET.OK, errmsg='操作成功')

@news_blue.route('/detail/<int:news_id>')
@user_login_data
def news_detail(news_id):
    """
    新闻详情
    :return: 
    """
    # user_id = session.get('user_id', None)
    # user = None
    # if user_id:
    #     #     表示已经登陆
    #     try:
    #         user = User.query.get(user_id)
    #     except Exception as e:
    #         current_app.logger.error(e)
    # 使用函数封装获取用户信息
    user = g.user
    # 2.新闻的点击排行
    news_clicks = []
    try:
        news_clicks = News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)

    #     3
    news = None
    try:
        news = News.query.get(news_id)
    except Exception as e:
        current_app.logger.error(e)
    # 404异常的提示页面
    if not news:
        abort(404)
    # 累加点击量
    news.clicks += 1
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
    # 5收藏和取消收藏
    is_collected = False
    if user:
        if news in user.collection_news:
            is_collected = True
    context = {
        'user':user,
        'news_clicks':news_clicks,
        'news':news.to_dict(),
        'is_collected':is_collected
    }
    return  render_template('news/detail.html',context =context )