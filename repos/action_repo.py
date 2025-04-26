from decimal import Decimal
from tables.action import Action, ActionType
from tables.coin import Coin
from tables.member import Member
from models.dto.decision import Decision
from sqlalchemy.orm import scoped_session

class ActionRepo:
    def __init__(self):
        self.__fee = 0.9995
    
    def buy_coin(self, member: Member, decision: Decision, total_price: int, session: scoped_session) -> Decimal:
        amount = Decimal(total_price) / Decimal(decision.current_price) * Decimal(self.__fee)
        
        action = Action(
            action = ActionType.BUY,
            market = decision.market,
            amount = amount,
            entry_price = decision.current_price,
            total_price = total_price,
            member = member
        )
        session.add(member)
        session.add(action)
        return amount
    
    def sell_coin(self, coin: Coin, decision: Decision, session: scoped_session) -> int:
        member: Member = coin.member
        price = Decimal(decision.current_price) * Decimal(coin.amount) * Decimal(self.__fee) // 1
        action = Action(
            action = ActionType.SELL,
            market = decision.market,
            amount = coin.amount,
            entry_price = decision.current_price,
            total_price = price,
            member = member
        )
        session.add(action)
        return price