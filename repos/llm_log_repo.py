from sqlalchemy.orm import scoped_session
from tables.llm_log import LLMLog
from dtos.decision import Decision

class LLMLogRepo:
    def log_decision(self, decision: Decision, session: scoped_session):
        llm_log = LLMLog(
            action = decision.action,
            reason = decision.reason,
            price = decision.current_price,
            market = decision.market
        )
        session.add(llm_log)
        session.commit()