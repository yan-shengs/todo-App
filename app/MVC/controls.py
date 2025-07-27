from flask import request, json, Blueprint
from flask import current_app
from app.utils.message import Message
# 移除直接导入session，改为在函数内部导入
from app.mvc.models import UserInfo, TipInfo
import jwt
import bcrypt
import time

# 创建蓝图
bp = Blueprint("bp", __name__)


# 获取数据库session的辅助函数
def get_session():
    """获取数据库session对象"""
    from app import session
    return session


# 加密Pwd
def cryptPwd(pwd, salt=None):
    """密码加密函数"""
    if salt is None:
        salt = bcrypt.gensalt()  # 生成随机盐值
    if isinstance(pwd, str):
        pwd = pwd.encode('utf-8')  # 确保密码是bytes类型
    hashedPwd = bcrypt.hashpw(pwd, salt)
    return hashedPwd


# 验证密码
def verify_password(plain_password, hashed_password):
    """验证密码是否正确"""
    if isinstance(plain_password, str):
        plain_password = plain_password.encode('utf-8')
    return bcrypt.checkpw(plain_password, hashed_password)


# 创建token -- 后续可以把非视图函数的业务处理放入service层
def createToken(user_id):
    """
    创立蓝图的文件不能直接导入main.py的app否则导致循环,我们使用应用上下文的方法
    with current_app.context():
        current_app.config["xxx"]的方式
    """
    """headers = {"alg": "HS256", "typ": "JWT"}冗余-jwt自动生成"""
    exp = time.time() + 15 * 60  # 增加15分钟
    payload = {"user_id": user_id, "exp": exp}
    with current_app.app_context():
        token = jwt.encode(
            payload=payload,
            key=current_app.config["SECRET_KEY"],
            algorithm="HS256",
            # headers=headers,
        )  # 新版本jwt.encode返回字符串，不需要decode
    print(token)
    return token


# 验证token 注意由于verify方法可能报错需要使用异常检测
def verifyToken(token):
    with current_app.app_context():  # 非视图函数中使用current_app需要使用左边的形式
        SECRET_KEY = current_app.config["SECRET_KEY"]  # 通过全局实例访问
    try:  # 发生错误 -> except
        # 解析令牌，自动验证exp字段
        print(token)
        payload = jwt.decode(
            token,
            SECRET_KEY,  # 这个密钥生产环境最好使用redis等动态储存
            algorithms=["HS256"],
            options={"verify_exp": True},  # 显式开启过期验证（默认开启）
        )
        # print(1)
        # print(payload)
        return {"valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        # 令牌已过期
        return {"valid": False, "error": "token_expired"}
    except jwt.InvalidTokenError:
        # 令牌无效（格式错误、签名错误等）
        return {"valid": False, "error": "invalid_token"}


# 验证POW(proof of work)
def verifyPOW():
    pass


# 采用json数据,http_status的返回格式


@bp.before_app_request  # 钩子函数 - 后端拦截器
def before():
    """
    除了登录和注册接口所有接口需要检测jwt
    以及注意由于前后端分离的浏览器安全策略options
    """
    if request.method == "OPTIONS":
        return  # 给cors处理

    url = request.path
    if url != "/api/login" and url != "/api/register":
        # 针对login和register放行
        token = request.headers.get("authorization").split(" ")[1]
        res = verifyToken(token)
        valid = res["valid"]
        try:
            payload = res["payload"]
        except Exception:
            error = res["error"]
        if valid: # valid == True有些冗余 直接valid 
            return 
            # return json.dumps(Message.success_msg(payload)), 200 # 找了一个下午 随后发现Message.success_msg写成了error
        else:
            return json.dumps(Message.error_msg(error)), 401  # 过期 错误


@bp.route("/login", methods=["POST"])
def login():
    # 登录接口
    session = get_session()  # 获取session对象
    
    if request.is_json:
        data = request.get_json()  # json格式
    else:
        data = request.form
    username = data.get("username")
    password = data.get("password")

    # 先查找用户
    user = session.query(UserInfo).filter(UserInfo.username == username).first()
    
    if user and verify_password(password, user.password):
        token = createToken(user.to_dict()["id"])
        return json.dumps(Message.success_msg({"token": token, "id": user.id})), 200
    else:
        return json.dumps(Message.error_msg("用户名或密码错误")), 401


@bp.route("/register", methods=["POST"])
def register():
    # 注册
    session = get_session()  # 获取session对象

    if request.is_json:
        data = request.get_json()  # json格式
    else:
        data = request.form  # 表单
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return json.dumps(Message.error_msg("用户名或密码不存在")), 400
    
    # 检查用户名是否已存在
    existing_user = session.query(UserInfo).filter(UserInfo.username == username).first()
    if existing_user:
        return json.dumps(Message.error_msg("用户名已存在")), 401
    
    # 创建新用户
    try:
        hashed_password = cryptPwd(password)
        user = UserInfo(username=username, password=hashed_password)
        session.add(user)  # id是自增数据
        session.commit()
        token = createToken(user.id)
        return json.dumps(Message.success_msg(data = {"token": token})),200
    except Exception as e:
        session.rollback()
        return json.dumps(Message.error_msg(f"注册失败: {str(e)}")), 500


@bp.route("/subAccount", methods=["POST"])
def subAccount():
    # 删除账户
    pass


@bp.route("/query", methods=["POST"])
def query():
    session = get_session()  # 获取session对象
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    token = data.get("token")
    
    payload = verifyToken(token)["payload"]  # 显然通过了token的验证
    userid = payload["user_id"]
    
    # 修正：应该查询TipInfo而不是UserInfo  # 修正：使用逗号分隔条件
    result = session.query(TipInfo).filter(TipInfo.status != 3, TipInfo.user_id == userid).all()
    
    result_dicts = [item.to_dict() for item in result]
    return result_dicts


@bp.route("/add", methods=["POST"])
def add():
    session = get_session()  # 获取session对象
    
    # 兼容 application/json 和 form-data
    if request.is_json:
        data = request.get_json()  # json
    else:
        data = request.form  # 表单
    content = data.get("content")
    token = data.get("token")
    payload = verifyToken(token)["payload"]
    userid = payload.get("user_id")
    
    if not userid or not content:
        return Message.error_msg(msg={"msg": "id和todo不能为空"}), 400
    try:
        info = TipInfo(content=content, user_id=userid)  # 自增id
        session.add(info)
        session.commit()
        return Message.success_msg(msg={"msg": "添加成功"}, data={"id": info.id}),200
    except Exception as e:
        session.rollback()
        return Message.error_msg(msg={"msg": f"添加失败: {str(e)}"}), 500


@bp.route("/subContent", methods=["POST"])
def subContent():
    session = get_session()  # 获取session对象
    
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form
    id = data.get("id")
    info = session.query(TipInfo).filter(TipInfo.id == id).first()
    if info:
        info.status = 3  # 删除
        session.commit()
        return Message.success_msg({"msg": "删除成功"}), 200
    else:
        return Message.error_msg(msg={"msg": "未找到对应记录"}), 400


@bp.route("/tick", methods=["POST"])
def tick():
    session = get_session()  # 获取session对象
    
    # 一个函数一个功能
    # 负责打勾状态
    if request.is_json:
        data = request.get_json()
    else:
        data = request.form

    id = data.get("id")

    data = session.query(TipInfo).filter(TipInfo.id == id).first()
    if data:
        if data.status == 2:  # 修正字段名
            data.status = 1
        else:
            data.status = 2
    session.commit()
    # 返回状态
    return Message.success_msg(msg={"msg": "修改成功"}, data={"data": data.status}), 200
