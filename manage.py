from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from redis import StrictRedis
class Config(object):
    """配置文件的加载"""
    # 开启调试模式
    DEBUGE = True
    # 配置mysql连接信息
    SQLALCHEMY_DATABASE_URI = 'mysql://root:mysql@127.0.0.1:3306/information_29'
    # 不去追踪数据库的修改
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 配置redis 数据库 不是flask的扩展所以需要自己添加
    REDIS_HOST = "127.0.0.1"
    REDIS_PORT = 6379
app = Flask(__name__)
# 获取配置信息
app.config.from_object(Config)

# 创建连接数据库对象
db = SQLAlchemy(app)

#创建连接到redis 数据库的对象
redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
@app.route("/")
def index():
    redis_store.set("name","zzy")
    return "index page"

if __name__ == "__main__":
    app.run(debug=True)
