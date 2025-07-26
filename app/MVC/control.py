from flask import Blueprint,request,current_app
from app.MVC.model import Datetip,Dateuser
from app import session
import json
import jwt
import time


bp = Blueprint("bp",__name__)


def create_token(id):
    headers = {"alg": "HS256", "typ": "JWT"}
    exp = time.time() + 15
    payload = {"uid":id,"exp":exp}
    with current_app.app_context():
        token = jwt.encode(payload=payload,
                           key=current_app.config["SECRET_KEY"],
                           algorithm='HS256',
                           headers=headers).decode('utf-8') # encode返回bytes类型不能直接转化为json需要decode成str类型
    return token

def verify_token(token):
    # SECRET_KEY = bp.config["SECRET_KEY"] 错误用法
    with current_app.app_context(): # 非视图函数中使用current_app需要使用左边的形式 
        SECRET_KEY = current_app.config["SECRET_KEY"] # 通过全局实例访问
    try:
        # 解析令牌，自动验证exp字段
        payload = jwt.decode(
            token,
            SECRET_KEY, # 这个密钥最好使用redis动态储存
            algorithms=["HS256"],
            options={"verify_exp": True}  # 显式开启过期验证（默认开启）
        )
        return {"valid": True, "payload": payload}
    except jwt.ExpiredSignatureError:
        # 令牌已过期
        return {"valid": False, "error": "token_expired"}
    except jwt.InvalidTokenError:
        # 令牌无效（格式错误、签名错误等）
        return {"valid": False, "error": "invalid_token"}


@bp.before_request # 请求拦截器
def before():
     # 获取请求头中的Authorization

    if request.method == "OPTIONS": # 不能直接处理浏览器安全检测机制
            return  # 直接放行，让Flask-CORS处理

    url = request.path
    # print(url)
    # print(url != "/api/login")
    if url != "/api/login" and url != "/api/register":
        # 所有非login接口如果没有认证判断401
        # print(1)
        data = request.headers
        # print(data)
        token = data.get("authorization").split(" ")[1]
        print(token)
        # print(token)
        # url = request.path # 读取当前路径 但是这里我们只有一个网页所以忽略
        if not (token and 
                jwt.decode(
            token,
            current_app.config["SECRET_KEY"], # 这个密钥最好使用redis动态储存
            algorithms=["HS256"],
            options={"verify_exp": True})): # 这里应该配置一个异常检测因为jwt.decode可能报错
            return json.dumps({
                "result":False,
                "code":401,
                "data":"未登录"
            }),401
#     后续要完成前后端判断登录时间过期

@bp.route("login",methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    # print(data)
    data = session.query(Dateuser).filter(Dateuser.tipusername == username and Dateuser.tippassword == password).first()
    if data:
        id = data.to_dict()["tipuserid"]
        return json.dumps({"success":1,
                           "id":id,
                            "Auth":create_token(id) # 返回Auth的认证 前端以brear前缀储存在localstorage 后端需要验证jwt过期 前端需要定时清楚 加上 前端两个拦截器
                           })
    else:    
        return json.dumps({"success":0})

@bp.route("register",methods=["POST"])
def register():
    # 注册逻辑还有一旦存在用户则不能注册同一账号和同一密码 否则就覆盖了
    data = request.get_json()
    print(data) # 测试
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return json.dumps({
            "sucess":False,"code":400,"msg":"用户名或密码不存在"
        })
    user = session.query(Dateuser).filter(Dateuser.tippassword == password,Dateuser.tipusername == username).first()
    if user: # 如果查到了
        return json.dumps({
            "success":False,"msg":"用户名和密码重复"
        })
    else:
        # 将数据放入数据库的表里
        # 这里直接写tipusername而不是右边的形式Dateuser.tipusername
        user = Dateuser(tipusername = username,tippassword=password)
        print(user.__dict__)
        session.add(user) # id是自增数据
        session.commit()
        return json.dumps({
            "success":True,"msg":"注册成功","id":user.tipuserid,"Auth":create_token(user.tipuserid)
        })


@bp.route("/query",methods=["POST"])
def query():
    data = request.get_json()
    print(data)
    token = data.get("token")
    payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"], # 这个密钥最好使用redis动态储存
            algorithms=["HS256"],
            options={"verify_exp": True}  # 显式开启过期验证（默认开启）
        )
    userid = payload.get("uid")
    # data = session.query(Datetip).join(
    #     Dateuser,
    #     Dateuser.tipuserid == Dateuser.userid
    # ) 我直接不储存了因为第一张表里面就关联了储存了userid
    # 不要Datetip.tipstatus != 3,Dateuser.tipuserid == userid --- filter接收的是参数而不是表达式
    result = session.query(Datetip).filter(Datetip.tipstatus != 3,Datetip.tipuserid == userid).all()

    # 将对象列表转换为dict列表
    result_dicts = [item.to_dict() for item in result]
    print(result_dicts)
    return result_dicts

# @bp.route("/add",methods=["POST"])
# def add():
#     id = request.form.get("id")
#     todo = request.form.get("todo")
#     tipinfo = Datetip(tipid=id,tiptodo=todo,tipdone=True,tipstatus=1)
#     print(tipinfo)
#     session.add(tipinfo)
#     session.commit()

@bp.route("/test",methods=["GET","POST"])
def test():
    res = json.dumps({"status":"200"})
    return res

@bp.route("/tick",methods=["POST"])
def tick():
    back = request.get_json()
    # print(back)
    token = back.get("token")
    print(token)
    # print(token)
    # 这里都是通过拦截器验证的因此肯定正确
    payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"], # 这个密钥最好使用redis动态储存
            algorithms=["HS256"],
            options={"verify_exp": True}  # 显式开启过期验证（默认开启）
        )
    
    id = payload.get("uid")
    data = session.query(Datetip).filter(Datetip.tipid == id).first()
    if data:
        if data.tipstatus == 2:
            data.tipstatus = 1
        else:
            data.tipstatus = 2
    session.commit()
    return {"success": True, "msg": "修改成功","data":data.tipstatus}

@bp.route("/add", methods=["POST"])
def add():
    # 兼容 application/json 和 form-data
    if request.is_json:
        data = request.get_json() # json
    else:
        data = request.form  # 表单
    # id = data.get("id")
    todo = data.get("todo")
    # userid = data.get("userid")
    token = data.get("token")
    print(token)
    # print(token)
    # 这里都是通过拦截器验证的因此肯定正确
    payload = jwt.decode(
            token,
            current_app.config["SECRET_KEY"], # 这个密钥最好使用redis动态储存
            algorithms=["HS256"],
            options={"verify_exp": True}  # 显式开启过期验证（默认开启）
        )
    userid = payload.get("uid")
    print(userid)

    if not userid or not todo:
        return {"success": False, "msg": "id和todo不能为空"}, 400
    try:
        tipinfo = Datetip(tiptodo=todo, tipstatus=0,tipuserid=userid) # 自增id
        session.add(tipinfo)
        session.commit()
        return {"success": True, "msg": "添加成功", "id": tipinfo.tipid}
    except Exception as e:
        session.rollback()
        return {"success": False, "msg": f"添加失败: {str(e)}"}, 500


@bp.route("/sub",methods=["POST"])
def sub():
    data = request.get_json() # 和get_data有关吗
    # print(data)
    id = data.get("id")
    # 查询对应的记录
    # print(id)
    
    tipinfo = session.query(Datetip).filter(Datetip.tipid == id).first()
    if tipinfo:
        tipinfo.tipstatus = 3 # 删除
        session.commit()
        return {"success": True, "msg": "删除成功"}
    else:
        return {"success": False, "msg": "未找到对应记录"}
    