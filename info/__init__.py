from logging.handlers import RotatingFileHandler

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import  Session
# from config import  Config,DevelopmentConfig,UnittestConfig,ProductionConfig
from config import configs
import logging
from logging.handlers import   RotatingFileHandler




def setup_log(level):
    # 设置日志的记录等级
    logging.basicConfig(level=level )  # 调试debug级
    # 创建日志记录器，指明日志保存的路径、每个日志文件的最大大小、保存的日志文件个数上限
    file_log_handler = RotatingFileHandler("logs/log", maxBytes=1024 * 1024 * 100, backupCount=10)
    # 创建日志记录的格式                 日志等级    输入日志信息的文件名 行数    日志信息
    formatter = logging.Formatter('%(levelname)s %(filename)s:%(lineno)d %(message)s')
    # 为刚创建的日志记录器设置日志记录格式
    file_log_handler.setFormatter(formatter)
    # 为全局的日志工具对象（flask app使用的）添加日志记录器
    logging.getLogger().addHandler(file_log_handler)

# 创建连接数据库对象
db = SQLAlchemy()
redis_store = None

def create_app(config_name):
    """创建app工厂方法"""

    setup_log(configs[config_name].LEVEL_LOG)

    app = Flask(__name__)
    # 获取配置信息
    app.config.from_object(configs[config_name])

    # 创建连接数据库对象
    db.init_app(app)
    #创建连接到redis 数据库的对象
    global redis_store
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST,port=configs[config_name].REDIS_PORT)

    #开启CSRF保护
    CSRFProtect(app)
    # 将session数据存储在后端的位置
    Session(app)
    from info.modules.index import index_blue
    # 注册路由
    # from info.modules.index import index_blue
    app.register_blueprint(index_blue)
    return  app