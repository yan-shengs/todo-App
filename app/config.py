# flask配置 
import os

class Config:
    # 配置用于全局
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key') # 这一行用于从环境变量中获取SECRET_KEY如没有采用dev-secret-key默认值
    SQLALCHEMY_DATABASE_URI = 'sqlite:///site.db'  
    SQLALCHEMY_TRACK_MODIFICATIONS = False # 一般建议设置为Flase
    UPLOAD_FOLDER = 'uploads'