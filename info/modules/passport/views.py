# 注册和登录
from . import  passport_blue
from flask import  request,abort,current_app,make_response,jsonify,session
from info.utils.captcha.captcha import captcha
from info import redis_store,constants,response_code,db
import re,random, datetime
from flask import  json
from info.libs.yuntongxun.sms import CCP
from info.models import User, News
from info import  constants


@passport_blue.route('/logout',methods=['GET'])
def logout():
    try:
        session.pop('user_id',None)
        session.pop('mobile',None)
        session.pop('nick_name', None)
        session.pop('is_admin',False)
    except Exception as e:
        current_app.logger.debug(e)
        return jsonify(errno=response_code.RET.DATAERR, errmsg='退出登录失败')
    return jsonify(errno=response_code.RET.OK, errmsg='退出登录成功')


@passport_blue.route('/login', methods=['POST'])
def login():
    """登录
    1.获取参数（手机号，密码明文）
    2.校验参数（判断参数是否缺少和手机号是否合法）
    3.还使用手机号查询用户信息
    4.校验用户密码是否正确
    5.将状态保持信息写入到session,完成登录
    6.记录最后一次登录时间
    7.响应登录结果
    """
    # 1.获取参数（手机号，密码明文）
    json_dict = request.json
    mobile = json_dict.get('mobile')
    password = json_dict.get('password')

    # 2.校验参数（判断参数是否缺少和手机号是否合法）
    if not all([mobile, password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')

    # 3.还使用手机号查询用户信息
    try:
        user = User.query.filter(User.mobile==mobile).first()
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询用户数据失败')
    if not user:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='用户名或密码错误')

    # 4.校验用户密码是否正确
    if not user.check_password(password):
        return jsonify(errno=response_code.RET.PWDERR, errmsg='用户名或密码错误')

    # 5.将状态保持信息写入到session,完成登录
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    # 6.记录最后一次登录的时间
    user.last_login = datetime.datetime.now()
    try:
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='记录最后一次登录的时间失败')

    # 7.响应登录结果
    return jsonify(errno=response_code.RET.OK, errmsg='登录成功')



@passport_blue.route('/register', methods=['POST'])
def register():
    """注册
    1.接受参数（手机号，短信验证码，密码明文）
    2.校验参数（判断是否缺少和手机号是否合法）
    3.查询服务器的短信验证码
    4.跟客户端传入的短信验证码对比
    5.如果对比成功，就创建User模型对象，并对属性赋值
    6.将模型数据同步到数据库
    7.保存session,实现状态保持，注册即登录
    8.响应注册结果
    """
    # 1.接受参数（手机号，短信验证码，密码明文）
    # request.json : 封装了json.loads(request.data)
    json_dict = request.json
    mobile = json_dict.get('mobile')
    smscode_client = json_dict.get('smscode')
    password = json_dict.get('password')

    # 2.校验参数（判断是否缺少和手机号是否合法）
    if not all([mobile, smscode_client, password]):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='缺少参数')
    if not re.match(r'^1[345678][0-9]{9}$', mobile):
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='手机号格式错误')

    # 3.查询服务器的短信验证码
    try:
        smscode_server = redis_store.get('SMS:'+mobile)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg='查询短信验证码失败')
    if not smscode_server:
        return jsonify(errno=response_code.RET.NODATA, errmsg='短信验证码不存在')

    # 4.跟客户端传入的短信验证码对比
    if smscode_client != smscode_server:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg='输入短信验证码有误')

    # 5.如果对比成功，就创建User模型对象，并对属性赋值
    user = User()
    user.mobile = mobile
    user.nick_name = mobile
    # TODO 密码需要加密后再存储
    # user.password_hash = password
    # 记录最后一次登录的时间
    # 密码需要加密后再存储
    # 方案一：在这个视图中，直接调用对应的密码加密的算法，加密密码存储到数据库
    # 方案二: 在这个视图中，封装一个加密的方法，加密密码存储到数据库
    # 方案三：在模型类中新增一个属性叫做password,并加载setter和getter方法，调用setter，直接完成密码加密存储
    # psd = user.password
    user.password = password#setter 方法
    user.last_login = datetime.datetime.now()

    # # 6.将模型数据同步到数据库
    try:
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        current_app.logger.error(e)
        db.session.rollback()
        return jsonify(errno=response_code.RET.DBERR, errmsg='保存注册数据失败')

    # 7.保存session,实现状态保持，注册即登录
    session['user_id'] = user.id
    session['mobile'] = user.mobile
    session['nick_name'] = user.nick_name

    # 8.响应注册结果
    return jsonify(errno=response_code.RET.OK, errmsg='注册成功')

@passport_blue.route('/sms_code',methods=['post'])
def sms_code():
    """发送短信
    1.接收参数
    2.校验参数是否齐全
    3.查询服务器存储的图片
    4.跟客户端传入的图片验证码对比
    5.如果对比成功,生成短信验证码,并发送短信
    6.存储短信验证码redis,方便注册时比较
    """
#     1.{'mobiel':'12312312','image_code':'asdc','image_code_id':'uuid'}
    json_str = request.data
    json_dict = json.loads(json_str)
    mobile = json_dict.get('mobile')
    image_code_client = json_dict.get('image_code')
    image_code_id = json_dict.get("image_code_id")
#     2
    if not all([mobile, image_code_client, image_code_id]):
        return  jsonify(errno= response_code.RET.PARAMERR,errmsg="缺少参数")
    if not re.match(r'^1[345678][0-9]{9}$',mobile):
        return  jsonify(errno=response_code.RET.PARAMERR, errmsg ="手机号码格式错误" )

    try:
        image_code_server = redis_store.get('ImageCode:'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno = response_code.RET.DBERR, errmsg="查询图片的验证码")
    if not image_code_server:
        return jsonify(errno = response_code.RET.NODATA, errmsg="查询图片不存在")
    if image_code_server.lower() != image_code_client.lower():
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="验证码有误")

    sms_code = '%6d' %random.randint(0,999999)
    current_app.logger.debug(sms_code)
    # result = CCP().send_template_sms(mobile,[sms_code,5],1)
    # if result !=0:
    #     return jsonify(errno=response_code.RET.THIRDERR, errmsg="短信发送失败")

    try:
        redis_store.set('SMS:'+mobile,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        return jsonify(errno=response_code.RET.DBERR, errmsg="保存短信验证码失败")

    return jsonify(errno=response_code.RET.OK, errmsg="发送短信验证码成功")


@passport_blue.route("/image_code", methods=['GET'])
def image_code():
    """提供图片
      1.接收参数(uuid)
      2.校验参数
      3.生成图片验证码
      4.保存图片验证码到redis
      5.修改image的ContentType = 'image/jpg'
      6.响应图片验证码
    """
    print(request.url)
    #1.
    imageCodeId = request.args.get('imageCodeId')
    # 2
    if not imageCodeId:
        abort(403)
    # 3
    name, text, image = captcha.generate_captcha()
    current_app.logger.debug(text)
    try:
        redis_store.set('ImageCode:'+ imageCodeId,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 5
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'

    return response