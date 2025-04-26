from sqlalchemy import Column, Integer, String
from settings.db_connection import Base
from sqlalchemy.orm import relationship

class Member(Base):
    __tablename__ = "member"
    
    id = Column(Integer, primary_key=True, autoincrement=True) # 기본키
    name = Column(String(10), nullable=False, unique=True) # 회원 이름
    balance = Column(Integer, nullable=False) # 잔고(KRW)
    coin = relationship("Coin", back_populates="member", uselist=False) # Coin 테이블과의 관계 설정
    
    def minus_balance(self, amount: int):
        self.balance -= amount
        
    def plus_balance(self, amount: int):
        self.balance += amount