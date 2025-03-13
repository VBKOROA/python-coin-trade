from sqlalchemy import Column, DateTime, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import relationship
from settings.db_connection import Base

class Coin(Base):
    __tablename__ = "coin"
    
    id = Column(Integer, primary_key=True) # 기본키
    market = Column(String(20), nullable=False) # 거래소 마켓
    amount = Column(Numeric(precision=20, scale=8), nullable=False) # 구매 수량
    entry_price = Column(Integer, nullable=False) # 구매 시점 가격
    total_price = Column(Integer, nullable=False) # 총 구매 금액
    created_at = Column(DateTime, nullable=False, default=func.now()) # 생성시간
    member_id = Column(Integer, ForeignKey('member.id'), nullable=False, unique=True) # 회원 ID (외래키, Member 테이블과의 관계 설정)
    member = relationship("Member", backref="coin", uselist=False) # Member 테이블과의 관계 설정