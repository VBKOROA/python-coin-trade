from decimal import Decimal
from tables.coin import Coin
from tables.member import Member
from dtos.decision import Decision
from sqlalchemy.orm import scoped_session

class CoinRepo:
    def buy_coin(self, member: Member, decision: Decision, amount: Decimal, session: scoped_session):
        coin = Coin(
            market = decision.market,
            amount = amount,
            member = member
        )
        session.add(coin)