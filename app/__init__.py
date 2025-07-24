from flask import Flask
from app.config import Config
from sqlalchemy import create_engine
from app.MVC.model import Base
from sqlalchemy.orm import sessionmaker


engine = create_engine('sqlite:///site.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

session = Session() # 依靠session对象实现持久化交互


def create_app(config=Config):
    app = Flask(__name__)
    if config is not None: 
        app.config.from_object(config)
    # 否则采用设置默认配置
    return app

