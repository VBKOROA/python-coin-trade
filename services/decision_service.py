from abc import ABC, abstractmethod
from dtos.candle_chart import CandleChart
from dtos.decision import Decision

class DecisionService(ABC):
    @abstractmethod
    async def execute_trade_decision(self, candle_chart: CandleChart) -> Decision:
        pass