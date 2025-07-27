import os

"""
官方提供多种方法,
这里演示三种导入配置的方式(作用对象app.config)
from_object -- 默认导入全大写(规范),引入类或对象属性(如果想要导入全小写,或混合需要重写from_object方法完全不推荐)
另外三种不敏感
from_mapping -- 导入字典
from_pyfile -- 导入py文件的config.py
# config.py
debug = True       # 小写变量
SECRET_KEY = 'xxx' # 全大写变量
App_Name = 'test'  # 混合大小写变量
"""


class Config:
    # 这里采用类或者函数实现类属性配置和函数属性配置
    # 使用from import导入配置,flask.config.from_object导入配置

    # jwt密钥配置
    # os.getenv()尝试从环境变量中读取SECRET_KEY的值,如果没有采用testJWT默认值
    SECRET_KEY = os.getenv(
        "SECRET_KEY", "testJWT"
    )  # 生产环境使用环境变量 开发环境使用默认测试
    # -------------------------
    # sqlalchemy配置
    SQLALCHEMY_DATABASE_URI = "sqlite:///site.db"  # sqlite文件路径-相对于启动文件
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 一般建议设置为Flase
