from abc import ABC, abstractmethod
from dtos.candle_chart import CandleChart
from dtos.decision import Decision
from repos.decision_log_repo import DecisionLogRepo
from settings.db_connection import DBMS

class DecisionService(ABC):
    @abstractmethod
    async def execute_trade_decision(self, candle_chart: CandleChart) -> Decision:
        pass
    
    @abstractmethod
    def set_decision_log_repo(self, decision_log_repo: DecisionLogRepo):
        pass
        
    @abstractmethod
    def set_dbms(self, dbms: DBMS):
        pass