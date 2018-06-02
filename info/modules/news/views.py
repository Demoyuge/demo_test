#新闻详情：收藏，评论点赞
from info.response_code import RET
from info.utils.comment import user_login_data
from . import news_blue
from flask import render_template, session, current_app, abort, g, jsonify, request
from info.models import User, News, Comment
from info import  constants,db,response_code
from info.utils.comment import  user_login_data



@news_blue.route('/news_comment',methods=['POST'])
@user_login_data
def add_news_comment():

    user = g.user
    if not user:
        return jsonify(errno = RET.SESSIONERR, errmsg="用户未登录")


    # 2.获取请求参数
    news_id = request.json.get('news_id')
    comment_content = request.json.get('comment')
    # 没有parent_id表示评论信息；反之，是回复评论
    parent_id = request.json.get('parent_id')

    if not all([news_id,comment_content]):
        return jsonify(errno = RET.PARAMERR, errmsg = "参数不足")
    try:
        news_id = int(news_id)
        if parent_id:
            parent_id = int(parent_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

    try:
        news = News.query.get(news_id)
    except Exception as e :
        current_app.logger.error(e)
        return jsonify(errno = RET.DBERR, errmsg="查询数据失败")

    if not news:
        return  jsonify(errno=RET.NODATA,errmsg= "该新闻不存在")

    comment =  Comment()
    comment.user_id = user.id
    comment.news_id  = news_id
    comment.content = comment_content
    if parent_id:
        comment.parent_id = parent_id

    try:
        db.session.add(comment)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return  jsonify(errno = RET.DBERR, errmsg = "保存评论数据失败")

    return  jsonify(errno = RET.OK, errmsg = "评论成功",data=comment.to_dict())



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
    news_clicks = None
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
    comments = []
    try:
        comments = Comment.query.filter(Comment.news_id == news_id).order_by(Comment.create_time.desc()).all()
    except Exception as e:
        current_app.logger.error(e)
    comments_dict_list = []
    for comment in comments:

        comments_dict_list.append(comment.to_dict())



    context = {
        'user':user,
        'news_clicks':news_clicks,
        'news':news.to_dict(),
        'is_collected':is_collected,
        'comments':comments_dict_list 
    }
    return  render_template('news/detail.html',context =context )