from sqlalchemy import Column, Integer, String
from settings.db_connection import Base

class Member(Base):
    __tablename__ = "member"
    
    id = Column(Integer, primary_key=True, autoincrement=True) # 기본키
    name = Column(String(10), nullable=False, unique=True) # 회원 이름
    balance = Column(Integer, nullable=False) # 잔고(KRW)
    
    def minus_balance(self, amount: int):
        self.balance -= amount
        
    def plus_balance(self, amount: int):
        self.balance += amount