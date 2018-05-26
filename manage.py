from flask_migrate import  Migrate, MigrateCommand
from flask_script import Manager
# from info import app,db
from info import create_app,db
from werkzeug.routing import BaseConverter



app = create_app('pro')



# app = Flask(__name__)
# # 获取配置信息
# app.config.from_object(Config)
#
# # 创建连接数据库对象
# db = SQLAlchemy(app)
#
# #创建连接到redis 数据库的对象
# redis_store = StrictRedis(host=Config.REDIS_HOST,port=Config.REDIS_PORT)
#
# #开启CSRF保护
# CSRFProtect(app)
# # 将session数据存储在后端的位置
# Session(app)

# 创建脚本管理对象
manager = Manager(app)

# 让迁移和app数据库建立管理
Migrate(app, db)
# 将数据库迁移的脚本添加到manager
manager.add_command('mysql', MigrateCommand)




@app.route("/")
def index():
    # redis_store.set("name","zzy")
    # from flask import session
    # # 会将{'age':'2'}写入到cookie
    # session['age'] = '2'

    return "index page"

if __name__ == "__main__":

    manager.run()
