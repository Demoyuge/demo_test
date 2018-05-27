from redis import StrictRedis
import logging
class Config(object):
    """配置文件的加载"""
    # 项目密钥CSRF/session
    SECRET_KEY = "zzy"

    # 开启调试模式
    DEBUGE = True
    # 配置mysql连接信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/information_29'
    # 不去追踪数据库的修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis 数据库 不是flask的扩展所以需要自己添加
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
    # 指定Session用什么来存储
    SESSION_TYPE = 'redis'
    # 指定session数据存储在后端的位置
    SESSION_REDIS = StrictRedis(host=REDIS_HOST,port=REDIS_PORT)
    #是否是用secret_key签名你的session
    SESSION_USE_SIGNER =True
    #设置过期时间 要求SESSION_PERMANENT,True而默认就是31天
    PERMANENT_SESSION_LIFETIME = 60*60*24

    # 封装不同开发环境下的配置
class DevelopmentConfig(Config):
    # DEBUGE = True
    # SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information_29"
    LEVEL_LOG  = logging.DEBUG
    pass

class ProductionConfig(Config):
    DEBUGE =  True
    SQLALCHEMY_DATABASE_URI ="mysql://root:mysql@127.0.0.1:3306/information_pro_29"
    LEVEL_LOG = logging.WARNING

class UnittestConfig(Config):
    DEBUGE = True
    # TESTING = True
    SQLALCHEMY_DATABASE_URI = "mysql://root:mysql@127.0.0.1:3306/information_case_29"
    LEVEL_LOG = logging.DEBUG
#定义字典
configs ={
    'dev' :DevelopmentConfig,
    'pro' : ProductionConfig,
    'unit': UnittestConfig
}