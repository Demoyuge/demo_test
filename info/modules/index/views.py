
#主页模块
from . import  index_blue
from info import redis_store
from flask import render_template,current_app,session,request,jsonify
from info.models import User,News,Category
from info import constants,response_code

@index_blue.route('/news_list')
def index_news_list():
  cid = request.args.get('cid','1')
  page = request.args.get('page','1')
  per_page = request.args.get('per_page','10')
  try:
      cid = int(cid)
      page = int(page)
      per_page = int(per_page)
  except Exception as e:
      current_app.logger.error(e)
      return jsonify(errno = response_code.RET.PARAMERR,errmsg = '参数错误'  )
  if cid == 5:
    # 取出10条数据
        paginate =  News.query.order_by(News.create_time.desc()).paginate(page,per_page,False)
  else:
        paginate = News.query.filter(News.category_id == cid).order_by(News.create_time.desc()).paginate(page,per_page,False)
  # 构造响应的新闻列表数据
  news_list = paginate.items
  # 读取分页的总页数
  total_page = paginate.pages
  # 读取当前是第几页
  current_page = paginate.page
  # 将模型对象列表转成字典
  news_dict_list = []
  news_userid_list = []
  for news in news_list:
      news_dict_list.append(news.to_basic_dict())
      if news.user_id:
         news_userid_list.append(news.user.to_dict())
      else:
         news_userid_list.append([])
  # 构造响应客户端的数据
  data = {
      'news_dict_list' : news_dict_list,
      'total_page' : total_page,
      'current_page' : current_page,
      'news_userid_list':news_userid_list
  }
  return  jsonify(errno = response_code.RET.OK, errmsg = 'OK',data=data)


@index_blue.route("/")
def index():
    # redis_store.set('name', 'zzy')

    user_id = session.get('user_id',None)
    user = None
    if user_id:
    #     表示已经登陆
        try:
            user = User.query.get(user_id)
        except Exception as e:
            current_app.logger.error(e)
    # 2.新闻的点击排行
    news_clicks = []
    try:
       news_clicks  =News.query.order_by(News.clicks.desc()).limit(constants.CLICK_RANK_MAX_NEWS)
    except Exception as e:
        current_app.logger.error(e)
    #     3.新闻的分类
    categories = []
    try:
       categories =  Category.query.all()
    except Exception as e:
        current_app.logger.error(e)


    #构造模板上下文数据
    context = {
        'user': user,
        'news_clicks':news_clicks,
        'categories':categories

    }
    """主页"""
    return render_template('news/index.html',context=context)

@index_blue.route('/favicon.ico',methods=['GET'])
def favicon():

    return  current_app.send_static_file('news/favicon.ico')