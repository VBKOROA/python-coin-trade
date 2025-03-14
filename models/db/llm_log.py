from sqlalchemy import Column, DateTime, Integer, String, Text, func
from settings.db_connection import Base

class LLMLog(Base):
    __tablename__ = "llm_log"
    
    id = Column(Integer, primary_key=True, autoincrement=True) # 기본키
    up_chance = Column(Integer, nullable=False) # 상승 확률
    down_chance = Column(Integer, nullable=False) # 하락 확률
    price = Column(Integer, nullable=False) # 현재가
    market = Column(String(10), nullable=False) # 마켓
    details = Column(Text, nullable=False) # 상세 내용
    created_at = Column(DateTime, nullable=False, default=func.now()) # 생성시간