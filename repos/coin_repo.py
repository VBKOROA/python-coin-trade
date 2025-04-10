from decimal import Decimal
from models.db.coin import Coin
from models.db.member import Member
from models.dto.decision import Decision
from sqlalchemy.orm import scoped_session

class CoinRepo:
    def buy_coin(self, member: Member, decision: Decision, amount: Decimal, session: scoped_session):
        coin = Coin(
            market = decision.market,
            amount = amount,
            member = member
        )
        session.add(coin)