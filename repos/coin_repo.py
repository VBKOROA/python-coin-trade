from decimal import Decimal
from settings.db_connection import DBMS
from models.decision import Decision

class CoinRepo:
    def set_dbms(self, dbms: DBMS):
        self.dbms = dbms

    def get_coins(self):
        self.dbms.cursor.execute("SELECT * FROM coins")
        return self.dbms.cursor.fetchall()
    
    def get_coins_should_sell(self, price: int):
        query = """
            SELECT * FROM coin
            WHERE target_price <= %s
            OR stop_loss_price >= %s
        """
        self.dbms.cursor.execute(query, (price, price))
        return self.dbms.cursor.fetchall()
    
    def sell_coin(self, coin_id: int):
        query = """
            DELETE FROM coin
            WHERE id = %s
        """
        self.dbms.cursor.execute(query, (coin_id,))
        
    def buy_coin(self, decision: Decision, amount: Decimal):
        market = decision.market
        buy_price = decision.current_price
        target_price = decision.target_price
        stop_loss_price = decision.stop_loss_price
        query = """
            INSERT INTO coin (market, amount, buy_price, target_price, stop_loss_price)
            VALUES (%s, %s, %s, %s, %s)
        """
        self.dbms.cursor.execute(query, (market, amount, buy_price, target_price, stop_loss_price))