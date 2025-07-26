from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey

Base = declarative_base() # 建立基类


# 建表
class Datetip(Base):
    # 应该增加唯一标识的id
    __tablename__ = "Datetip"

    tipid = Column(Integer,primary_key=True,autoincrement=True)
    tiptodo = Column(String(50))
    tipuserid = Column(Integer, ForeignKey("Dateuser.tipuserid")) # 用户id
    tipstatus = Column(Integer,default=0) # 默认未完成
    # 模型关系简化联表查询
    # dateuser = relationship("Dateuser") # 关联Bateuser对象 - Dateuser表 默认一对多
    # dateuser = relationship("Dateuser") 待研究

    def to_dict(self):
        return {
            'tipid': self.tipid,
            'tiptodo': self.tiptodo,
            'tipuserid': self.tipuserid,
            'tipstatus': self.tipstatus # 定义三个状态 未完成 完成 删除
        }

class Dateuser(Base):
    __tablename__ = "Dateuser"
    # 一个用户对应多个todo 主关系 一对多
    tipuserid = Column(Integer,primary_key=True,autoincrement=True) # 自增
    tipusername = Column(String(50))
    # sha1(sha1(password) + salt)
    # 防止密码被内部人员看到
    # 防止数据库被爆
    tippassword = Column(String(50)) # 按理说应该加密储存但是小项目无伤大雅
    
    # datetip =  relationship("Datetip") # 关联Datetip对象 - Datetip表 深入理解这个函数
    # 待研究
    def to_dict(self):
        return {
            "tipuserid": self.tipuserid,
            "tipusername": self.tipusername,
            "tippassword": self.tippassword
        }