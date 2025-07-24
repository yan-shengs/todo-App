# 蓝图模式
from app import create_app
from flask import Blueprint
from app.MVC.control import bp
# ORM数据库
from flask_cors import CORS
import jwt



if __name__ == "__main__":

    app = create_app()
    CORS(app)
    app.register_blueprint(bp,url_prefix="/api")
    app.run()