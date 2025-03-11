from settings.db_connection import DBMS
from models.decision import Decision

class LLMLogRepo:
    def set_dbms(self, dbms: DBMS):
        self.dbms = dbms
        
    def log_decision(self, decision: Decision):
        query = """
            INSERT INTO llm_log (action, details, price)
            VALUES (%s, %s, %s)
        """
        self.dbms.cursor.execute(query, (decision.action, decision.think, decision.current_price))
        self.dbms.conn.commit()