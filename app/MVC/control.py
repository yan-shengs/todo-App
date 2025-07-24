from flask import Blueprint,request
from app.MVC.model import Datetip,Dateuser
from app import session
import json
import jwt

bp = Blueprint("bp",__name__)


# def verify_token(token):
#     try:
#         # 解析令牌，自动验证exp字段
#         payload = jwt.decode(
#             token,
#             SECRET_KEY, # 这个密钥最好使用redis动态储存
#             algorithms=["HS256"],
#             options={"verify_exp": True}  # 显式开启过期验证（默认开启）
#         )
#         return {"valid": True, "payload": payload}
#     except jwt.ExpiredSignatureError:
#         # 令牌已过期
#         return {"valid": False, "error": "token_expired"}
#     except jwt.InvalidTokenError:
#         # 令牌无效（格式错误、签名错误等）
#         return {"valid": False, "error": "invalid_token"}


# @bp.before_request # 请求拦截器
# def before():
#      # 获取请求头中的Authorization
#     auth_header = request.headers.get("Authorization")
#     # url = request.path # 读取当前路径 但是这里我们只有一个网页所以忽略
#     if !(auth_header && auth_header):
#         return json.dumps({
#             "ruselt":"error",
#             "code":401,
#             "data":"未登录"
#         }),401

#     # 判断登录时间过期
#     if 
#     return None

@bp.route("login",methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    print(data)
    data = session.query(Dateuser).filter(Dateuser.tipusername == username and Dateuser.tippassword == password).first()
    if data:
        id = data.to_dict()["tipuserid"]
        return json.dumps({"success":1,
                           "id":id
                           })
    else:    
        return json.dumps({"success":0})

@bp.route("/query",methods=["POST"])
def query():
    data = request.get_json()
    print(data)
    userid = data.get("userid")
    # 不要Datetip.tipstatus != 3,Dateuser.tipuserid == userid --- filter接收的是参数而不是表达式
    result = session.query(Datetip).filter(Datetip.tipstatus != 3,Dateuser.tipuserid == userid).all()

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
    print(back)
    id = back.get("id")
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
    userid = data.get("userid")
    if userid or todo:
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
    