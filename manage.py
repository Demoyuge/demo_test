from flask import Flask
from flask_script import Manager
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
from flask_wtf.csrf import CSRFProtect
from flask_session import  Session
from flask_migrate import  Migrate, MigrateCommand
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

app = Flask(__name__)
# 获取配置信息
app.config.from_object(Config)

# 创建连接数据库对象
db = SQLAlchemy(app)

#创建连接到redis 数据库的对象
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)

#开启CSRF保护
CSRFProtect(app)
# 将session数据存储在后端的位置
Session(app)

# 创建脚本管理对象
manager = Manager(app)

# 让迁移和app数据库建立管理
Migrate(app, db)
# 将数据库迁移的脚本添加到manager
manager.add_command('mysql', MigrateCommand)




@app.route("/")
def index():
    # redis_store.set("name","zzy")
    from flask import session
    # 会将{'age':'2'}写入到cookie
    session['age'] = '2'

    return "index page"

if __name__ == "__main__":

    manager.run()
