from sqlalchemy import Column, DateTime, Integer, String, Text, func
from settings.db_connection import Base

class DecisionLog(Base):
    __tablename__ = "decision_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True) # 기본키
    action = Column(String(10), nullable=False) # 행동 (buy, sell, wait)
    reason = Column(Text, nullable=False) # 이유
    price = Column(Integer, nullable=False) # 현재가
    market = Column(String(10), nullable=False) # 마켓
    created_at = Column(DateTime, nullable=False, default=func.now()) # 생성시간