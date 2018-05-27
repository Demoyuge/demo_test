from flask_migrate import  Migrate, MigrateCommand
from flask_script import Manager
# from info import app,db
from info import create_app,db
from werkzeug.routing import BaseConverter



app = create_app('dev')

# 创建脚本管理对象
manager = Manager(app)

# 让迁移和app数据库建立管理
Migrate(app, db)
# 将数据库迁移的脚本添加到manager
manager.add_command('mysql', MigrateCommand)




# @app.route("/")
# def index():
#     # redis_store.set("name","zzy")
#     # from flask import session
#     # # 会将{'age':'2'}写入到cookie
#     # session['age'] = '2'
#
#     return "index page"

if __name__ == "__main__":
    print(app.url_map)
    manager.run()
