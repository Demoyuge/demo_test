# 个人中心
from . import user_blue
from flask import render_template,g,redirect,url_for,request,jsonify,current_app,session,abort
from info.utils.comment import user_login_data
from info import response_code,db,constants
from info.utils.file_storage import upload_file
from info.models import Category,News,User

@user_blue.route('/other_news_list')
def other_news_list():
    # 1.获取页数
    page = request.args.get("p", '1')
    other_id = request.args.get("user_id")

    # 2.校验参数
    try:
        p = int(page)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='参数错误')

    if not all([page, other_id]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')

    # 3.查询用户数据
    try:
        user = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=response_code.RET.NODATA, errmsg='用户不存在')

    # 4.分页查询
    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(p, constants.OTHER_NEWS_PAGE_MAX_COUNT, False)
        # 获取当前页数据
        news_list = paginate.items
        # 获取当前页
        current_page = paginate.page
        # 获取总页数
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户数据失败')

    # 5.构造响应数据
    news_dict_list = []
    for news_item in news_list:
        news_dict_list.append(news_item.to_review_dict())

    data = {
        "news_list": news_dict_list,
        "total_page": total_page,
        "current_page": current_page
    }

    # 6.渲染界面
    return jsonify(errno=response_code.RET.OK, errmsg='OK',data=data)

@user_blue.route('/other_info')
@user_login_data
def other_info():
    """其他用户概况"""

    # 1.获取登录用户信息
    login_user = g.user
    if not login_user:
        return redirect(url_for('index.index'))

    # 获取被登录用户关注的用户的信息
    other_id = request.args.get('user_id')
    if not other_id:
        abort(404)

    # 查询要展示的被关注的用户的信息
    other = None
    try:
        other = User.query.get(other_id)
    except Exception as e:
        current_app.logger.error(e)
        abort(404)
    if not other:
        abort(404)

    # 判断关注和取消关注的显示
    is_followed = False
    if login_user and other:
        if other in login_user.followed:
            is_followed = True

    context = {
        'user':login_user.to_dict(),
        'other':other.to_dict(),
        'is_followed':is_followed
    }

    return render_template('news/other.html',context=context)


@user_blue.route('/user_follow')
@user_login_data
def user_followed():
    """我的关注"""

    # 1.获取登录用户信息
    login_user = g.user
    if not login_user:
        return redirect(url_for('index.index'))

    # 2.接受参数
    page = request.args.get('p', '1')

    # 3.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'

    # 4.查询登录用户关注的用户 （login_user.followed）
    followed_user_list = []
    total_page = 1
    current_page = 1
    try:
        paginate = login_user.followed.paginate(page,constants.USER_FOLLOWED_MAX_COUNT,False)
        followed_user_list = paginate.items
        total_page = paginate.pages
        current_page = paginate.page
    except Exception as e:
        current_app.logger.error(e)
        abort(404)

    # 5.构造渲染数据
    followed_dict_list = []
    for followed_user in followed_user_list:
        followed_dict_list.append(followed_user.to_dict())

    context = {
        'users':followed_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }

    # 6.响应结果
    return render_template('news/user_follow.html',context=context)

@user_blue.route('/news_list')
@user_login_data
def user_news_list():

    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    page =request.args.get('p','1')
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1'
    news_list = []
    current_page = 1
    total_page = 1

    try:
        paginate = News.query.filter(News.user_id == user.id).paginate(page,constants.USER_COLLECTION_MAX_NEWS ,False)
        news_list = paginate.items
        current_page = paginate.page
        total_page = paginate.pages
    except Exception as e:
        current_app.logger.error(e)

    news_dict_list = []
    for news in news_list:
        # news_dict_list.append(news.to_review_dict())
        news_dict_list.append(news.to_basic_dict())

    context = {
        'news_list':news_dict_list,
        'current_page':current_page,
        'total_page':total_page
    }
    return render_template('news/user_news_list.html',context=context)

@user_blue.route('/news_release',methods=['GET','POST'])
@user_login_data
def news_release():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    #2.GET请求逻辑
    if request.method == 'GET':
        categories =[]
        try:
            categories = Category.query.all()
        except Exception as e:
            current_app.logger.error(e)
        categories.pop(0)
        context = {
            'categories':categories
        }
        return render_template('news/user_news_release.html',context = context)
    if request.method == 'POST':
        title = request.form.get("title")
        source ="个人发布"
        digest = request.form.get("digest")
        category_id = request.form.get("category_id")
        index_image = request.files.get("index_image")
        content  =request.form.get("content")
    if not all([title,source,digest,content,index_image,category_id]):
        return jsonify(errno=response_code.RET.PARAMERR,errmsg="缺少参数")
    try:
        index_image_data = index_image.read()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.PARAMERR,errmsg="读取新闻图片失败")

    try:
        key = upload_file(index_image_data)
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno=response_code.RET.THIRDERR,errmsg="上传新闻图片失败")

     # 3. 初始化新闻模型，并设置相关数据
    news = News()
    news.title = title
    news.digest = digest
    news.source = source
    news.content = content
    news.index_image_url = constants.QINIU_DOMIN_PREFIX + key
    news.category_id = category_id
    news.user_id = g.user.id
    # 1代表待审核状态
    news.status = 1

    try:
        db.session.add(news)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(e)
        return  jsonify(errno=response_code.RET.DBERR,errmsg="存储失败")

    return jsonify(errno=response_code.RET.OK,srrmsg="成功")

@user_blue.route('/user_collection')
@user_login_data
def user_collection():
    """用户收藏"""
    # 1.获取登录用户信息
    user = g.user
    if not user:
        return redirect(url_for('index.index'))

    # 2.接受参数
    page = request.args.get('p', '1')

    # 3.校验参数
    try:
        page = int(page)
    except Exception as e:
        current_app.logger.error(e)
        page = '1' # 公司中对于这种处理会有专门的方案的，不需要操心

    # 4.分页查询 : user.collection_news == BaseQuery类型的对象
    paginate = None
    try:
        paginate = user.collection_news.paginate(page, constants.USER_COLLECTION_MAX_NEWS, False)
    except Exception as e:
        current_app.logger.error(e)

    # 5.构造渲染模板的数据
    news_list = paginate.items
    total_page = paginate.pages
    current_page = paginate.page

    news_dict_list = []
    for news in news_list:
        news_dict_list.append(news.to_basic_dict())

    context = {
        'news_list':news_dict_list,
        'total_page':total_page,
        'current_page':current_page
    }

    # 6.渲染模板
    return render_template('news/user_collection.html',context=context)


@user_blue.route('/pass_info', methods = ['GET','POST'])
@user_login_data
def pass_info():
    user = g.user
    if not user:
        return  redirect(url_for('index.index'))

    if request.method == 'GET':
        return  render_template('news/user_pass_info.html')
    if request.method == 'POST':
        #接受参数
        old_password = request.json.get('old_password')
        new_password = request.json.get('new_password')
        #校验参数
        if not all([old_password,new_password]):
            return  jsonify(errno=response_code.RET.PARAMERR, errmsg="缺少参数")
        if not user.check_password(old_password):
            return jsonify(errno=response_code.RET.PARAMERR, errmsg='原密码有错误')
        #更新密码
        user.password = new_password
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR,errmsg='保存修改后的密码失败')

        return jsonify(errno=response_code.RET.OK,errmsg='保存成功')

@user_blue.route('/pic_info',methods =['GET','POST'])
@user_login_data
def pic_info():
    user = g.user
    if not user:
        return redirect(url_for('index.index'))
    if request.method =='GET':
        context = {
            'user':user.to_dict()
        }
        return render_template('news/user_pic_info.html', context=context)
    if request.method == 'POST':
        # 获取参数（图片）
        avatar_file = request.files.get('avatar')
        # 校验参数
        try:
            avatar_data = avatar_file.read()
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno = response_code.RET.PARAMERR, errmsg= "读取头像数据失败")

        # 调用上传方法，将图片上传到七牛
        try:
            key = upload_file(avatar_data)
        except Exception as e:
            current_app.logger.error(e)
            return jsonify(errno = response_code.RET.THIRDERR,errmsg = "头像上传失败")
        #保存用户头像的key到数据库
        user.avatar_url = key
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(e)
            return jsonify(errno=response_code.RET.DBERR,errmsg= "保存失败")
        data = {
            'avatar_url':constants.QINIU_DOMIN_PREFIX +key
        }
        #响应头像上传的结果
        return jsonify(errno=response_code.RET.OK, errmsg='上传头像成功', data=data)

@user_blue.route('/base_info',methods =['GET','POST'])
@user_login_data
def base_info():

    user = g.user
    if not user:
        return  redirect(url_for('index.index'))
    if request.method =='GET':
        context = {
            'user':user.to_dict()
        }
        return render_template('news/user_base_info.html', context=context)

    if request.method =='POST':
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
        'user':user.to_dict()
    }
    return  render_template('news/user.html',context=context)