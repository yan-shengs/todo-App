# 小工具 - message返回json格式


class Message:
    def success_msg(data=None, msg="success"):
        """成功消息格式"""
        return {"status": True, "msg": msg, "data": data}

    def error_msg(data=None, msg="error"):
        """错误消息格式"""
        return {"status": False, "msg": msg, "data": data}
