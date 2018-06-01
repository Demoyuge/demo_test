#新闻详情：收藏，评论点赞
from info.utils.comment import user_login_data
from . import news_blue
from flask import render_template, session, current_app, abort,g
from info.models import User,News
from info import  constants,db
from info.utils.comment import  user_login_data


@news_blue.route('/news_collect')
@user_login_data
def news_collect():
    pass

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