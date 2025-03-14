from api.upbit_client import UpbitClient
from repos.member_repo import MemberRepo
from services.action_service import ActionService
from sqlalchemy.orm import scoped_session

from services.llm_service import LLMService

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
        
    def set_conn(self, session: scoped_session):
        self.__session = session
        
    def set_member_repo(self, member_repo: MemberRepo):
        self.__member_repo = member_repo
        
    async def execute_trade_logic(self, member_id: int):
        """
        자동 매매 로직을 실행하는 메서드.
        캔들 차트를 가져오고, 팔아야 할 코인이 있는지 확인하여 판매한다.
        AI 모델을 통해 매매 결정을 수행하고, 결정에 따라 코인을 구매한다.
        """
        
        # 먼저 캔들 차트를 가져온다.
        candle_chart = await self.__upbit_client.fetch_candle_chart(self.__timeframe_config)
        
        # AI한테 결정을 요청한다.
        decision = await self.__llm_service.execute_trade_decision(candle_chart)
        
        # 현재 내가 가지고 있는 코인을 가져온다.
        member = self.__member_repo.get_member_by_id(member_id)
        
        # 만약 구매라면
        if(decision.action == 'buy'):
            self.__action_service.buy_coin(decision)
            self.__session.commit()