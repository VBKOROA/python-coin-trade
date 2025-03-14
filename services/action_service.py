import datetime
from decimal import Decimal
import json
import re

from models.dto.decision import Decision
from models.dto.candle_chart import CandleChart
from api.gemini_client import GeminiClient
from services.candle_service import CandleService

class ActionService:
    def __init__(self, dca: float):
        self.__dca = dca
    
    def sell_coin(self, coin, current_price):
        """
        현재 가격으로 지정된 코인을 판매합니다.
        Args:
            coin (dict): 판매할 코인. 이 값은 최소한 코인의 'id'를 포함하는 딕셔너리여야 합니다.
            current_price (float): 코인의 현재 시장 가격.
        Returns:
            None
        Raises:
            기본 레포지토리 메서드에서 발생하는 예외.
        """
        
        # 코인 판매 로직 실행 및 판매 금액 반환
        price = self.__action_log_repo.sell_coin(current_price, coin)
        # 코인 레포지토리에서 판매된 코인 정보 삭제
        self.__coin_repo.sell_coin(coin['id'])
        # Info 레포지토리에서 잔액 추가
        self.__info_repo.plus_balance(1, price)
        
    def buy_coin(self, decision: Decision):
        """
        코인을 구매하는 메서드.
        DCA(Dollar-Cost Averaging) 전략에 따라 사용 가능한 잔액의 일정 비율만큼 코인을 구매한다.
        구매 금액은 소수점 이하를 버림하여 정수로 만들고, 해당 금액으로 코인을 구매한다.
        구매 후 구매 정보는 코인 레포지토리에 저장하고, Info 레포지토리에서 잔액을 차감한다.
        Args:
            decision (Decision): 코인 구매 결정 정보. 시장(market)과 현재 가격(current_price)을 포함한다.
        Returns:
            None
        Raises:
            None: 예외는 발생하지 않는다.
        """
        
        # 현재 잔액을 가져옴
        balance = Decimal(self.__info_repo.get_balance(1))
        # DCA 비율에 따라 구매할 금액을 계산 (소수점 이하 버림)
        price = (balance * Decimal(self.__dca)).quantize(Decimal('1'), rounding='ROUND_DOWN')
        # 코인 구매 로직 실행 및 구매량 반환
        amount = self.__action_log_repo.buy_coin(decision.market, decision.current_price, price)
        # 코인 레포지토리에 구매 정보 저장
        self.__coin_repo.buy_coin(decision, amount)
        # Info 레포지토리에서 잔액 차감
        self.__info_repo.minus_balance(1, price)