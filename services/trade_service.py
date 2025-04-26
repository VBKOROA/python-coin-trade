from clients.upbit_client import UpbitClient
from tables.coin import Coin
from dtos.decision import Decision
from repos.member_repo import MemberRepo
from services.action_service import ActionService
from services.llm_service import LLMService
from settings.db_connection import DBMS
from dtos.candle_chart import CandleChart # CandleChart 임포트 추가 (타입 힌팅용)
from tables.member import Member # Member 임포트 추가 (타입 힌팅용)
from typing import Optional, Tuple # 타입 힌팅용 임포트 추가

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

    def _log_debug(self, message: str, shouldDebugMode: bool = True):
        """디버그 메시지를 출력하는 헬퍼 메서드"""
        if self.__debug or not shouldDebugMode:
            print(f"TradeService: {message}")

    async def _fetch_trade_prerequisites(self, member_id: int, session) -> Optional[Tuple[CandleChart, Decision, Member]]:
        """거래 로직 실행에 필요한 데이터를 가져옵니다."""
        self._log_debug("Fetching candle chart...")
        candle_chart = await self.__upbit_client.fetch_candle_chart(self.__timeframe_config)
        if not candle_chart or not candle_chart.current_price:
             print("TradeService: Failed to fetch candle chart or current price. Skipping logic.")
             return None
        self._log_debug("Candle chart fetched.")

        self._log_debug("Requesting trade decision from LLM...")
        decision: Decision = await self.__llm_service.execute_trade_decision(candle_chart)
        self._log_debug(f"Received decision: {decision.action} (Desired state)")

        self._log_debug(f"Fetching member {member_id} and their coin...")
        member = self.__member_repo.get_member_by_id(member_id, session)
        if not member:
            print(f"TradeService: Member {member_id} not found. Skipping logic.")
            return None
        self._log_debug(f"Member fetched. Currently holding coin: {member.coin is not None}")

        return candle_chart, decision, member

    def _execute_action_based_on_decision(self, member: Member, decision: Decision, session):
        """LLM 결정과 현재 상태를 비교하여 매수/매도 액션을 실행합니다."""
        current_coin: Optional[Coin] = member.coin
        has_coin = current_coin is not None
        action = decision.action

        if action == "hold":
            if not has_coin:
                self._log_debug("Decision is 'hold' and member does not have coin. Proceeding with buy.", False)
                self.__action_service.buy_coin(member, decision, session)
                self._log_debug("Buy action completed.")
            else:
                self._log_debug("Decision is 'hold' and member already has coin. No action needed.", False)
        elif action == "release":
            if has_coin:
                self._log_debug("Decision is 'release' and member has coin. Proceeding with sell.", False)
                # current_coin은 None이 아님이 보장됨
                self.__action_service.sell_coin(current_coin, decision, session)
                self._log_debug("Sell action completed.")
            else:
                self._log_debug("Decision is 'release' and member does not have coin. No action needed.", False)
        else:
            # 'hold', 'release' 외 다른 값이거나 LLM 오류 시 (기본값 'wait' 등)
            self._log_debug(f"Decision is '{action}'. No action taken.", False)

    async def execute_trade_logic(self, member_id: int):
        self._log_debug(f"Executing trade logic for member ID: {member_id}")

        with self.__dbms.get_session() as session:
            # 1. 거래 실행에 필요한 데이터 가져오기
            prerequisites = await self._fetch_trade_prerequisites(member_id, session)
            if prerequisites is None:
                self._log_debug(f"Could not fetch prerequisites for member {member_id}. Aborting trade logic.")
                return # 필수 데이터 없으면 중단

            candle_chart, decision, member = prerequisites

            # 2. LLM 결정과 현재 상태 비교하여 매수/매도 실행
            self._execute_action_based_on_decision(member, decision, session)

        self._log_debug(f"Trade logic execution finished for member ID: {member_id}")