from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import CheckConstraint

"""
这两个暂时不会
from sqlalchemy.orm import relationship 
from sqlalchemy import ForeignKey
"""

Base = declarative_base()  # 建立基类模板


# 建表
class UserInfo(Base):  # 储存用户信息
    __tablename__ = "UserInfo"  # 声明表名

    # autoincrement自增 primary_key主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    username = Column(String(50))  # 最大长度为 50 个字符

    password = Column(String(50))

    def to_dict(self):  # 设置返回值格式
        return {
            "id": self.id,
            "username": self.username,
            "password": self.password,
        }


class TipInfo(Base):
    __tablename__ = "TipInfo"

    id = Column(Integer, primary_key=True, autoincrement=True)

    content = Column(String(50))  # 事务

    status = Column(
        Integer,
        default=0
    )  # default默认值 CheckConstraint限制 
    """CheckConstraint("status IN (1,2,3)"),  # status与字段名一致 IN (0,1,2)
        name="=status", # 与字段名一致 不会用"""

    user_id = Column(Integer)

    def to_dict(self):  # 设置返回值格式
        return {
            "id": self.id,
            "content": self.content,
            "status": self.status,
            "user_id": self.user_id,
        }
