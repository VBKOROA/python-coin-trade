import datetime
from decimal import Decimal
import json
import re

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
        # LLM 요청 구조 복사
        prompt = self.__LLM_REQUEST_SCHEME
        
        # 모든 시간대의 캔들 데이터를 LLM 요청 구조에 삽입
        timeframes = candle_chart.get_all_timeframes()
        
        # 요청 스키마에서 캔들 데이터 플레이스홀더 패턴 찾기
        # 예: $15m_candle_data, $1h_candle_data, $4h_candle_data 등
        candle_placeholders = re.findall(r'\$([0-9]+[mhdw])_candle_data', prompt)
        
        # 시간대별 캔들 데이터 삽입
        for timeframe in candle_placeholders:
            placeholder = f"${timeframe}_candle_data"
            if timeframe in timeframes:
                candles = candle_chart.get_candles(timeframe)
                json_string = self.__candle_service.candle_to_json(candles)
                prompt = prompt.replace(placeholder, json_string)
            else:
                # 요청된 시간대의 데이터가 없는 경우 빈 데이터 표시
                prompt = prompt.replace(placeholder, "No data available for this timeframe")
        
        # 현재 가격 삽입
        prompt = prompt.replace("$current_price", str(candle_chart.current_price))
        
        # 현재 시간 삽입 (datetime 사용) (yyyy-MM-dd'T'HH:mm:ss 형식)
        prompt = prompt.replace("$current_time", datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

        # LLM 응답 생성
        decision = Decision(json.loads(self.__gemini_client.generate_answer(prompt)))  
        decision.set_current_price(candle_chart.current_price)
        decision.set_market(candle_chart.market)
        self.__llm_log_repo.log_decision(decision)
        print(str(decision))
        return decision
    
    def sell_coin(self, coin, current_price):
        # 코인 판매 로직 실행 및 판매 금액 반환
        price = self.__action_log_repo.sell_coin(current_price, coin)
        # 코인 레포지토리에서 판매된 코인 정보 삭제
        self.__coin_repo.sell_coin(coin['id'])
        # Info 레포지토리에서 잔액 추가
        self.__info_repo.plus_balance(1, price)
        
    def buy_coin(self, decision: Decision):
        # 현재 잔액을 가져옴
        balance = Decimal(self.__info_repo.get_balance(1))
        # DCA 비율에 따라 구매할 금액을 계산 (소수점 이하 버림)
        price = (balance * Decimal(self.__DCA)).quantize(Decimal('1'), rounding='ROUND_DOWN')
        # 코인 구매 로직 실행 및 구매량 반환
        amount = self.__action_log_repo.buy_coin(decision.market, decision.current_price, price)
        # 코인 레포지토리에 구매 정보 저장
        self.__coin_repo.buy_coin(decision, amount)
        # Info 레포지토리에서 잔액 차감
        self.__info_repo.minus_balance(1, price)