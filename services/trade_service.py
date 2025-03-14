from api.upbit_client import UpbitClient
from models.db.coin import Coin
from repos.member_repo import MemberRepo
from services.action_service import ActionService
from sqlalchemy.orm import scoped_session

from services.decision_service import DecisionAction, DecisionService
from services.llm_service import LLMService
from settings.db_connection import DBMS

class TradeService:
    def __init__(self, timeframe_config: dict):
        # 기본 시간대 구성 설정
        self.__timeframe_config = timeframe_config
    
    def set_upbit_client(self, upbit_client: UpbitClient):
        self.__upbit_client = upbit_client
    
    def set_action_service(self, action_service: ActionService):
        self.__action_service = action_service
        
    def set_llm_service(self, llm_service: LLMService):
        self.__llm_service = llm_service
        
    def set_member_repo(self, member_repo: MemberRepo):
        self.__member_repo = member_repo
        
    def set_decision_service(self, decision_service: DecisionService):
        self.__decision_service = decision_service
        
    def set_dbms(self, dbms: DBMS):
        self.__dbms = dbms
        
    async def execute_trade_logic(self, member_id: int):
        with self.__dbms.get_session() as session:
            # 먼저 캔들 차트를 가져온다.
            candle_chart = await self.__upbit_client.fetch_candle_chart(self.__timeframe_config)
            
            # AI한테 결정을 요청한다.
            decision = await self.__llm_service.execute_trade_decision(candle_chart)
            
            # 현재 내가 가지고 있는 코인을 가져온다.
            member = self.__member_repo.get_member_by_id(member_id, session)
            coin: Coin = member.coin
            
            # 최종 결정을 계산한다.
            decisionAction = self.__decision_service.decide_action(decision)
        
            if(decisionAction == DecisionAction.BUY):
                if(coin is None):
                    # 코인을 구매한다.
                    self.__action_service.buy_coin(member, decision, session)
            elif(decisionAction == DecisionAction.SELL):
                if(coin is not None):
                    # 코인을 판매한다.
                    self.__action_service.sell_coin(coin, decision, session)