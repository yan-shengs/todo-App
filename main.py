from flask_cors import CORS
from app import createApp,databaseInit
from app.mvc.controls import bp

if __name__ == "__main__":
    # 注意py导入文件是从上到下执行一遍,编译结果在__pycache__作为缓存如果文件不修改,可以直接利用缓存

    #  导入创建flask实例
    app = createApp()
    # 初始化数据库
    databaseInit(app)
    # CORS解决跨域问题
    CORS(app)  # -- 开发环境开全跨域策略 生产环境需要指定域名
    """
    # 导入flask配置
    # app.config.from_object()
    后续查文档发现更推荐在createApp()创建时,进行配置
    """
    # 注册蓝图
    app.register_blueprint(
        bp, url_prefix="/api"
    )  # 先导入bp蓝图(路由配置) url_prefix默认前缀
    # 运行flask实例
    app.run()
