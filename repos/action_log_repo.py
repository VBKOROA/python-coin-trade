from decimal import Decimal
from settings.db_connection import DBMS

class ActionLogRepo:
    def __init__(self):
        self.FEE_RATE = Decimal(0.9995) 
    
    def set_dbms(self, dbms: DBMS):
        self.__dbms = dbms
        
    def sell_coin(self, current_price, coin) -> Decimal:
        # 판매할 코인 정보를 이용하여 판매
        market = coin['market'] # 코인 마켓 정보
        amount = coin['amount'] # 코인 수량
        price = (amount * Decimal(current_price) * self.FEE_RATE).quantize(Decimal('1'), rounding='ROUND_DOWN') # 판매 가격 계산 (수수료 적용)
        action = 'sell' # 액션 타입
        query = """
            INSERT INTO action_log (market, amount, price, action)
            VALUES (%s, %s, %s, %s)
        """
        self.__dbms.cursor.execute(query, (market, amount, price, action)) # DB에 판매 로그 기록
        return price # 판매 가격 반환
    
    def buy_coin(self, market: str, current_price: int, price: Decimal) -> Decimal:
        amount = price / Decimal(current_price) * self.FEE_RATE # 구매 가능한 코인 수량 계산 (수수료 적용)
        action = 'buy' # 액션 타입
        query = """
            INSERT INTO action_log (market, amount, price, action)
            VALUES (%s, %s, %s, %s)
        """
        self.__dbms.cursor.execute(query, (market, amount, price, action)) # DB에 구매 로그 기록
        return amount # 구매한 코인 수량 반환