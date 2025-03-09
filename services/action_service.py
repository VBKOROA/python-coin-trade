from decimal import Decimal
import json

from models.decision import Decision
from repos.coin_repo import CoinRepo
from repos.info_repo import InfoRepo
from repos.llm_log_repo import LLMLogRepo
from models.candle_chart import CandleChart
from api.gemini_client import GeminiClient
from services.candle_service import CandleService
from repos.action_log_repo import ActionLogRepo

class ActionService:
    def __init__(self, llm_request_scheme: str, dca: float):
        self.__LLM_REQUEST_SCHEME = llm_request_scheme
        self.__DCA = dca
        
    def set_gemini_client(self, gemini_client: GeminiClient):
        self.__gemini_client = gemini_client
        
    def set_candle_service(self, candle_service: CandleService):
        self.__candle_service = candle_service
        
    def set_action_log_repo(self, action_log_repo: ActionLogRepo):
        self.__action_log_repo = action_log_repo
        
    def set_coin_repo(self, coin_repo: CoinRepo):
        self.__coin_repo = coin_repo
        
    def set_info_repo(self, info_repo: InfoRepo):
        self.__info_repo = info_repo
        
    def set_llm_log_repo(self, llm_log_repo: LLMLogRepo):
        self.__llm_log_repo = llm_log_repo
        
    async def execute_trade_decision(self, candle_chart: CandleChart) -> Decision:
        """
        주어진 시장에 대한 거래 결정을 실행합니다.
        Args:
            candle_chart (CandleChart): 캔들 차트 데이터 객체.
        Returns:
            Decision: 거래 결정 결과를 포함하는 객체.
        비고:
            이 메서드는 비동기적으로 작동하며, UpbitClient를 사용하여 15분 및 1시간 간격의 캔들 데이터를 가져옵니다.
            가져온 데이터는 LLM 요청 구조에 삽입되어 최종 거래 결정을 생성합니다.
        """
        
        # LLM 요청 구조 복사
        prompt = self.__LLM_REQUEST_SCHEME

        # LLM 요청 구조에 캔들 데이터 삽입
        prompt = prompt.replace("$15m_candle_data", self.__candle_service.candle_to_yaml(candle_chart.candles_15m))
        prompt = prompt.replace("$1h_candle_data", self.__candle_service.candle_to_yaml(candle_chart.candles_1h))
        prompt = prompt.replace("$current_price", str(candle_chart.current_price))

        # LLM 응답 생성
        decision = Decision(json.loads(self.__gemini_client.generate_answer(prompt)))  
        decision.set_current_price(candle_chart.current_price)
        decision.set_market(candle_chart.market)
        self.__llm_log_repo.log_decision(decision)
        print(str(decision))
        return decision
    
    def sell_coin(self, coin, current_price):
        """
        주어진 코인을 현재 가격으로 판매합니다.
        Args:
            coin (dict): 판매할 코인 정보.
            current_price (float): 현재 시장 가격.
        비고:
            이 메서드는 ActionRepo를 사용하여 거래 로그를 데이터베이스에 기록합니다.
        """
        price = self.__action_log_repo.sell_coin(current_price, coin)
        self.__coin_repo.sell_coin(coin['id'])
        self.__info_repo.plus_balance(1, price)
        
    def buy_coin(self, decision: Decision, balance: Decimal):
        """
        주어진 결정에 따라 코인을 구매합니다.
        Args:
            decision (Decision): 구매할 코인 정보 및 가격을 포함하는 결정 객체.
            balance (Decimal): 현재 잔액.
        비고:
            이 메서드는 ActionRepo를 사용하여 거래 로그를 데이터베이스에 기록합니다.
        """
        price = balance * Decimal(self.__DCA)
        amount = self.__action_log_repo.buy_coin(decision.market, decision.current_price, price)
        self.__coin_repo.buy_coin(decision, amount)
        self.__info_repo.minus_balance(1, price)