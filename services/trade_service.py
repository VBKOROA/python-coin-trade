from api.upbit_client import UpbitClient
from models.db.coin import Coin
from repos.member_repo import MemberRepo
from services.action_service import ActionService
from services.llm_service import LLMService
from settings.db_connection import DBMS

class TradeService:
    def __init__(self, timeframe_config: dict, debug = False):
        # 기본 시간대 구성 설정
        self.__timeframe_config = timeframe_config
        self.__debug = debug
    
    def set_upbit_client(self, upbit_client: UpbitClient):
        self.__upbit_client = upbit_client
    
    def set_action_service(self, action_service: ActionService):
        self.__action_service = action_service
        
    def set_llm_service(self, llm_service: LLMService):
        self.__llm_service = llm_service
        
    def set_member_repo(self, member_repo: MemberRepo):
        self.__member_repo = member_repo
        
    def set_dbms(self, dbms: DBMS):
        self.__dbms = dbms
        
    async def execute_trade_logic(self, member_id: int):
        if self.__debug:
            print(f"TradeService: Executing trade logic for member ID: {member_id}")

        with self.__dbms.get_session() as session:
            # 먼저 캔들 차트를 가져온다.
            if self.__debug:
                print("TradeService: Fetching candle chart...")
            candle_chart = await self.__upbit_client.fetch_candle_chart(self.__timeframe_config)
            if self.__debug:
                print("TradeService: Candle chart fetched.")

            # AI한테 결정을 요청한다.
            if self.__debug:
                print("TradeService: Requesting trade decision from LLM...")
            decision = await self.__llm_service.execute_trade_decision(candle_chart)
            if self.__debug:
                print(f"TradeService: Received decision: {decision.action}")

            # 현재 내가 가지고 있는 코인을 가져온다.
            if self.__debug:
                print(f"TradeService: Fetching member {member_id} and their coin...")
            member = self.__member_repo.get_member_by_id(member_id, session)
            coin: Coin = member.coin
            if self.__debug:
                print(f"TradeService: Member fetched. Has coin: {coin is not None}")

            # Decision 객체의 action 값을 직접 사용
            if decision.action == "buy":
                if self.__debug:
                    print("TradeService: Decision is 'buy'.")
                if(coin is None):
                    if self.__debug:
                        print("TradeService: Member does not hold coin. Proceeding with buy action.")
                    # 코인을 구매한다.
                    self.__action_service.buy_coin(member, decision, session)
                    if self.__debug:
                        print("TradeService: Buy action completed.")
                else:
                    if self.__debug:
                        print("TradeService: Member already holds coin. Skipping buy action.")
            elif decision.action == "sell":
                if self.__debug:
                    print("TradeService: Decision is 'sell'.")
                if(coin is not None):
                    if self.__debug:
                        print("TradeService: Member holds coin. Proceeding with sell action.")
                    # 코인을 판매한다.
                    self.__action_service.sell_coin(coin, decision, session)
                    if self.__debug:
                        print("TradeService: Sell action completed.")
                else:
                    if self.__debug:
                        print("TradeService: Member does not hold coin. Skipping sell action.")
            elif decision.action == "wait":
                if self.__debug:
                    print("TradeService: Decision is 'wait'. No action taken.")
            else:
                 if self.__debug:
                    print(f"TradeService: Unknown decision action: {decision.action}. No action taken.")

        if self.__debug:
            print(f"TradeService: Trade logic execution finished for member ID: {member_id}")