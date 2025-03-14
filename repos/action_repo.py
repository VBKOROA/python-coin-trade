from decimal import Decimal
from models.db.action import Action, ActionType
from models.db.member import Member
from models.dto.decision import Decision
from sqlalchemy.orm import scoped_session

class ActionRepo:
    def __init__(self):
        self.__fee = 0.9995
    
    def buy_coin(self, member: Member, decision: Decision, total_price: int, session: scoped_session):
        amount = Decimal(total_price) / Decimal(decision.current_price) * Decimal(self.__fee)
        action = Action(
            action = ActionType.BUY,
            market = decision.market,
            amount = amount,
            entry_price = decision.current_price,
            total_price = total_price,
            member = member
        )
        session.add(action)
        return amount