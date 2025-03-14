import datetime
from decimal import Decimal
import json
import re

from models.db.coin import Coin
from models.db.member import Member
from models.dto.decision import Decision
from repos.action_repo import ActionRepo
from repos.coin_repo import CoinRepo
from sqlalchemy.orm import scoped_session

class ActionService:
    def __init__(self, dca: float):
        self.__dca = dca
        
    def set_action_repo(self, action_repo: ActionRepo):
        self.__action_repo = action_repo
        
    def set_coin_repo(self, coin_repo: CoinRepo):
        self.__coin_repo = coin_repo
    
    def sell_coin(self, coin: Coin, decision: Decision, session: scoped_session):
        # 코인 판매 로직 실행 및 판매 금액 반환
        price = self.__action_repo.sell_coin(
            coin = coin,
            decision = decision,
            session = session
        )
        # 코인 레포지토리에서 판매된 코인 정보 삭제
        session.delete(coin)
        # 잔액 업데이트
        member: Member = coin.member
        member.plus_balance(price)
        session.add(member)
        
    def buy_coin(self, member: Member, decision: Decision, session: scoped_session):
        # 현재 잔액을 가져옴
        balance = Decimal(member.balance)
        # DCA 비율에 따라 구매할 금액을 계산 (소수점 이하를 버림하여 정수로 변환)
        total_price: int = balance * Decimal(self.__dca) // 1
        # 코인 구매 로직 실행 및 구매량 반환
        amount = self.__action_repo.buy_coin(
            member = member,
            decision = decision,
            total_price = total_price,
            session = session
        )
        # 코인 레포지토리에 구매 정보 저장
        self.__coin_repo.buy_coin(decision, amount)
        # 잔액 업데이트
        member.minus_balance(total_price)
        session.add(member)