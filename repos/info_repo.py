from decimal import Decimal
import settings.db_connection as DBMS

class InfoRepo:
    def set_dbms(self, dbms: DBMS):
        self.dbms = dbms
        
    def get_balance(self, id: int) -> int:
        self.dbms.cursor.execute("SELECT balance FROM info WHERE id = %s", (id,))
        result = self.dbms.cursor.fetchone()
        balance = int(result['balance']) if result else 0
        print(f"get_balance: {balance}")
        return balance
    
    def minus_balance(self, id: int, amount: Decimal):
        self.dbms.cursor.execute("UPDATE info SET balance = balance - %s WHERE id = %s", (amount, id))

    def plus_balance(self, id: int, amount: Decimal):
        self.dbms.cursor.execute("UPDATE info SET balance = balance + %s WHERE id = %s", (amount, id))
        