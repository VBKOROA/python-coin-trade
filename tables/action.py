import enum
from settings.db_connection import Base
from sqlalchemy import Column, Enum, Integer, Numeric, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

class ActionType(enum.Enum):
    BUY = "buy"  # 구매
    SELL = "sell"  # 판매

    def __repr__(self):
        return self.value

class Action(Base):
    __tablename__ = "action"
    
    id = Column(Integer, primary_key=True) # 기본키
    action = Column(Enum(ActionType), nullable=False) # 액션 (Enum)
    market = Column(String(20), nullable=False) # 거래소 마켓
    amount = Column(Numeric(precision=20, scale=8), nullable=False) # 코인 수량
    entry_price = Column(Integer, nullable=False) # 구매 시점 가격
    total_price = Column(Integer, nullable=False) # 총 구매 금액
    created_at = Column(DateTime, nullable=False, default=func.now())  # 생성시간
    member_id = Column(Integer, ForeignKey('member.id'), nullable=False)  # 회원 ID (외래키)
    member = relationship("Member", backref="actions")  # Member 테이블과의 관계 설정
    