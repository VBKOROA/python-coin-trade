import enum
from models.dto.decision import Decision

class DecisionAction(enum.Enum):
    BUY = "buy"
    SELL = "sell"
    WAIT = "wait"
    
    def __repr__(self):
        return self.value

class DecisionService:
    def __init__(self, chance_reliability: int, buy_at_up_chance_above: int, sell_at_down_chance_above: int):
        self.__chance_reliability = chance_reliability
        self.__buy_at_up_chance_above = buy_at_up_chance_above
        self.__sell_at_down_chance_above = sell_at_down_chance_above
    
    def decide_action(self, decision: Decision) -> DecisionAction:
        # buy, sell, wait의 3가지 행동을 결정하는 메서드
        
        if(abs(decision.up_chance - decision.down_chance) < self.__chance_reliability):
            # 확률 차이가 chance_reliability보다 작으면 wait
            return DecisionAction.WAIT
        
        if(decision.up_chance > decision.down_chance):
            if(decision.up_chance >= self.__buy_at_up_chance_above):
                # up_chance가 buy_at_up_chance_above보다 크면 buy
                return DecisionAction.BUY
        else:
            if(decision.down_chance >= self.__sell_at_down_chance_above):
                # down_chance가 sell_at_down_chance_above보다 크면 sell
                return DecisionAction.SELL
        