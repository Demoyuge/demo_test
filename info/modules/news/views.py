#新闻详情：收藏，评论点赞
from info.response_code import RET
from info.utils.comment import user_login_data
from . import news_blue
from flask import render_template, session, current_app, abort, g, jsonify, request
from info.models import User, News, Comment,CommentLike
from info import  constants,db,response_code
from info.utils.comment import  user_login_data

@news_blue.route('/followed_user', methods=['POST'])
@user_login_data
def followed_user():
    """关注和取消关注"""

    # 1.获取登录用户信息
    login_user = g.user
    if not login_user:
        return jsonify(errno=response_code.RET.SESSIONERR, errmsg='用户未登录')

    # 2.接受参数
    user_id = request.json.get('user_id')
    action = request.json.get('action')

    # 3.校验参数
    if not all([user_id,action]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if action not in ['follow','unfollow']:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    # 4.查询要关注的人是否存在
    try:
        other = User.query.get(user_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户失败')
    if not other:
        return jsonify(errno=response_code.RET.NODATA, errmsg='用户不存在')

    # 5.实现关注和取消关注
    if action == 'follow':
        # 关注
        if other not in login_user.followed:
            login_user.followed.append(other)
        else:
            return jsonify(errno=response_code.RET.DATAEXIST, errmsg='已关注')
    else:
        # 取消关注
        if other in login_user.followed:
            login_user.followed.remove(other)
        else:
            return jsonify(errno=response_code.RET.DATAEXIST, errmsg='未关注')

    # 6.同步到数据库
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存到数据库失败')

    # 7.响应结果
    return jsonify(errno=response_code.RET.OK, errmsg='OK')

@news_blue.route('/comment_like',methods=['POST'])
@user_login_data
def comment_like():
    """新闻评论点赞"""
    user = g.user
    if not user:
        return  jsonify(errno=response_code.RET.SESSIONERR,errmsg= '用户未登录')
    """接受参数"""
    comment_id = request.json.get('comment_id')
    action = request.json.get('action')

    # 校验参数
    if not all([comment_id,action]):
        return  jsonify(errno=response_code.RET.PARAMERR,errmsg= '缺少参数')
    if action not in ['add','remove']:
        return  jsonify(errno=response_code.RET.PARAMERR,errmsg= '参数错误')

    # 根据传入的comment_id 查询点赞的评论
    try:
        comment = Comment.query.get(comment_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询评论失败')
    if not comment:
        return  jsonify(errno = response_code.RET.NODATA, errmsg="评论不存在")

    # 查询要点赞的评论是否存在
    try:
        comment_like_model = CommentLike.query.filter(CommentLike.comment_id == comment_id,CommentLike.user_id == user.id).first()
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno=response_code.RET.DBERR,errmsg= '查询点赞失败')

    # 5点赞和取消点赞
    if action == 'add':
       if not comment_like_model:
           comment_like_model = CommentLike()
           comment_like_model.user_id = user.id
           comment_like_model.comment_id = comment_id

           # db.session.add(comment_like_model)
           db.session.add(comment_like_model)
           # 累加点赞
           comment.like_count += 1
    else:
        if comment_like_model:
            # 将记录从书库中删除
            # db.session.delete(comment_like_model)
            db.session.delete(comment_like_model)
            # 累加点赞
            comment.like_count -= 1

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return  jsonify(errno = response_code.RET.DBERR, errmsg='操作失败')


    # 点赞和取消点赞
    return  jsonify(errno = response_code.RET.OK, errmsg='OK')
    # 响应

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

    #     7展示评论点的赞
    # 查询用户点赞了那些评论
    comment_like_ids=[] #comment_like_ids == [21,22]
    if user:
        try:
            comment_likes = CommentLike.query.filter(CommentLike.user_id == user.id).all()
            comment_like_ids = [comment_like.comment_id for comment_like in comment_likes]
        except Exception as e:
            current_app.logger.error(e)
    comments_dict_list = []
    for comment in comments:
        comment_dict = comment.to_dict()

    #     给comment_dict追加一个is_like
    #     14 ------[21,22]
        comment_dict['is_like'] = False
        if comment.id in comment_like_ids:
            comment_dict['is_like'] = True

        comments_dict_list.append(comment_dict)
    #关注和取消关注
    #user:176
    is_followed = False

    if user and news.user:
        if news.user in user.followers:
            is_followed = True

    context = {
        'user': user.to_dict() if user else None,
        'news_clicks':news_clicks,
        'news':news.to_dict(),
        'is_collected':is_collected,
        'comments':comments_dict_list
    }
    return  render_template('news/detail.html',context =context )