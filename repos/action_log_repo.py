from decimal import Decimal
from settings.db_connection import DBMS

class ActionRepo:
    def __init__(self):
        self.FEE_RATE = Decimal(0.9995) 
    
    def set_dbms(self, dbms: DBMS):
        self.dbms = dbms
        
    def sell_coin(self, current_price, coin) -> Decimal:
        market = coin['market']
        amount = coin['amount']
        # 수수료를 고려한 가격
        price = amount * Decimal(current_price) * self.FEE_RATE 
        action = 'sell'
        query = """
            INSERT INTO action_log (market, amount, price, action)
            VALUES (%s, %s, %s, %s)
        """
        self.__dbms.cursor.execute(query, (market, amount, price, action))
        return price
    
    def buy_coin(self, market: str, current_price: int, price: Decimal) -> Decimal:
        amount = price / Decimal(current_price) * self.FEE_RATE
        action = 'buy'
        query = """
            INSERT INTO action_log (market, amount, price, action)
            VALUES (%s, %s, %s, %s)
        """
        self.__dbms.cursor.execute(query, (market, amount, price, action))
        return amount