from flask import Flask
from app.config import Config  # 相对于启动文件

# 导入sqlalchemy的create_engine创建引擎
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
# from main import app  # 导入实例 为什么不直接使用createApp因为其app存在于函数(局部)
# 上面会导致循环
from app.mvc.models import Base  # 导入数据库基类


# 创建flask实例函数
def createApp(config=Config):
    app = Flask(__name__)

    # 导入flask配置
    app.config.from_object(config)

    return app


# 采用sqlalchemy的全局session 如果想要局部需要使用flask-sqlalchemy库

# 声明全局变量（先不初始化）
engine = None
Session = None
session = None

# 创建sqlalchemy的数据库引擎
# 这里的执行,利用py导入文件自上而下全部执行一遍
def databaseInit(app):
    global engine, session, Base
    with app.app_context():
        URI = app.config["SQLALCHEMY_DATABASE_URI"]
        engine = create_engine(URI)

        # 创建sqlalchemy的session会话通过引擎进行交互
        # 基类用于建表
        Base.metadata.create_all(engine) # 只会创建新表或新增字段
        Session = sessionmaker(bind=engine)

        session = Session()  # 依靠session对象实现持久化交互
