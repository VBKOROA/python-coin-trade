from sqlalchemy.orm import scoped_session
from models.db.llm_log import LLMLog
from models.dto.decision import Decision

class LLMLogRepo:
    def log_decision(self, decision: Decision, session: scoped_session):
        llm_log = LLMLog(
            up_chance = decision.up_chance,
            down_chance = decision.down_chance,
            price = decision.current_price,
            market = decision.market,
            details = decision.details
        )
        session.add(llm_log)
        session.commit()