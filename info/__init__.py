from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import  Session
# from config import  Config,DevelopmentConfig,UnittestConfig,ProductionConfig
from config import configs

# 创建连接数据库对象
db = SQLAlchemy()

def create_app(config_name):
    """创建app工厂方法"""
    app = Flask(__name__)
    # 获取配置信息
    app.config.from_object(configs[config_name])

    # 创建连接数据库对象
    db.init_app(app)
    #创建连接到redis 数据库的对象
    redis_store = StrictRedis(host=configs[config_name].REDIS_HOST,port=configs[config_name].REDIS_PORT)

    #开启CSRF保护
    CSRFProtect(app)
    # 将session数据存储在后端的位置
    Session(app)

    return  app