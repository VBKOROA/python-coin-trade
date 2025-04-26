from api.upbit_client import UpbitClient
from models.db.coin import Coin
from models.dto.decision import Decision
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
            # 1. 캔들 차트 가져오기
            if self.__debug:
                print("TradeService: Fetching candle chart...")
            candle_chart = await self.__upbit_client.fetch_candle_chart(self.__timeframe_config)
            if not candle_chart or not candle_chart.current_price:
                 print("TradeService: Failed to fetch candle chart or current price. Skipping logic.")
                 return # 캔들 차트나 현재 가격 없으면 중단

            if self.__debug:
                print("TradeService: Candle chart fetched.")

            # 2. LLM에게 결정 요청 ('hold' 또는 'release')
            if self.__debug:
                print("TradeService: Requesting trade decision from LLM...")
            decision: Decision = await self.__llm_service.execute_trade_decision(candle_chart)
            if self.__debug:
                print(f"TradeService: Received decision: {decision.action} (Desired state)")

            # 3. 현재 코인 보유 상태 확인
            if self.__debug:
                print(f"TradeService: Fetching member {member_id} and their coin...")
            member = self.__member_repo.get_member_by_id(member_id, session)
            if not member:
                print(f"TradeService: Member {member_id} not found. Skipping logic.")
                return # 멤버 없으면 중단

            current_coin: Coin = member.coin
            has_coin = current_coin is not None
            if self.__debug:
                print(f"TradeService: Member fetched. Currently holding coin: {has_coin}")

            # 4. LLM 결정과 현재 상태 비교하여 매수/매도 결정
            if decision.action == "hold":
                if not has_coin:
                    print("TradeService: Decision is 'hold' and member does not have coin. Proceeding with buy.")
                    # 코인 구매 실행
                    self.__action_service.buy_coin(member, decision, session)
                    if self.__debug:
                        print("TradeService: Buy action completed.")
                else:
                    print("TradeService: Decision is 'hold' and member already has coin. No action needed.")
            elif decision.action == "release":
                if has_coin:                   
                    print("TradeService: Decision is 'release' and member has coin. Proceeding with sell.")     
                    # 코인 판매 실행
                    self.__action_service.sell_coin(current_coin, decision, session)
                    if self.__debug:
                        print("TradeService: Sell action completed.")
                else:
                    print("TradeService: Decision is 'release' and member does not have coin. No action needed.")
            else:
                # 'hold', 'release' 외 다른 값이거나 LLM 오류 시 (기본값 'wait' 등)
                print(f"TradeService: Decision is '{decision.action}'. No action taken.")

        if self.__debug:
            print(f"TradeService: Trade logic execution finished for member ID: {member_id}")