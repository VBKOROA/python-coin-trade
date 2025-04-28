from sqlalchemy.orm import scoped_session
from tables.decision_log import DecisionLog
from dtos.decision import Decision

class DecisionLogRepo:
    def log_decision(self, decision: Decision, session: scoped_session):
        decision_log = DecisionLog(
            action = decision.action,
            reason = decision.reason,
            price = decision.current_price,
            market = decision.market
        )
        session.add(decision_log)