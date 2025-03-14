from sqlalchemy.orm import scoped_session

from models.db.llm_log import LLMLog
from models.dto.decision import Decision

class LLMLogRepo:
    def set_session(self, session: scoped_session):
        self.__session = session
        
    def log_decision(self, decision: Decision):
        llm_log = LLMLog(
            up_chance = decision.up_chance,
            down_chance = decision.down_chance,
            price = decision.current_price,
            market = decision.market,
            details = decision.details
        )
        self.__session.add(llm_log)
        self.__session.commit()