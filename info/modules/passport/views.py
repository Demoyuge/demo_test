# 注册和登录
from . import  passport_blue
from flask import  request,abort,current_app,make_response,jsonify
from info.utils.captcha.captcha import captcha
from info import redis_store,constants,response_code
import  json,re,random
from info.libs.yuntongxun.sms import CCP

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
    moblie = json_dict.get('mobile')
    image_code_client = json_dict.get('image_code')
    image_code_id = json_dict.get("image_code_id")
#     2
    if not all([moblie, image_code_client, image_code_id]):
        return  jsonify(errno= response_code.RET.PARAMERR,errmsg="缺少参数")
    if not re.match(r'^1[345678][0-9]{9}$',moblie):
        return  jsonify(errno=response_code.RET.PARAMERR, errmsg ="手机号码格式错误" )

    try:
        image_code_server = redis_store.get('imageCode:'+image_code_id)
    except Exception as e:
        current_app.logger.error(e)
        return  jsonify(errno = response_code.RET.DBERR, errmsg="查询图片的验证码")
    if not image_code_server:
        return jsonify(errno = response_code.RET.NODATA, errmsg="查询图片不存在")
    if not image_code_server.lower() != image_code_client:
        return jsonify(errno=response_code.RET.PARAMERR, errmsg="验证码有误")

    sms_code = '%6d' %random.randint(0,999999)

    result = CCP().send_template_sms(moblie,[sms_code,5],1)
    if result !=0:
        return jsonify(errno=response_code.RET.THIRDERR, errmsg="短信发送失败")

    try:
        redis_store.set('SMS:'+moblie,sms_code,constants.SMS_CODE_REDIS_EXPIRES)
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
    #1.
    imageCodeId = request.args.get('imageCodeId')
    # 2
    if not imageCodeId:
        abort(403)
    # 3
    name, text, image = captcha.generate_captcha()

    try:
        redis_store.set('ImageCode:'+ imageCodeId,text,constants.IMAGE_CODE_REDIS_EXPIRES)
    except Exception as e:
        current_app.logger.error(e)
        abort(500)
    # 5
    response = make_response(image)
    response.headers['Content-Type'] = 'image/jpg'

    return response