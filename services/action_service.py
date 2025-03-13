import datetime
from decimal import Decimal
import json
import re

from models.dto.decision import Decision
from models.dto.candle_chart import CandleChart
from api.gemini_client import GeminiClient
from services.candle_service import CandleService

class ActionService:
    def __init__(self, llm_request_scheme: str, dca: float):
        self.__LLM_REQUEST_SCHEME = llm_request_scheme
        self.__DCA = dca
        
    def set_gemini_client(self, gemini_client: GeminiClient):
        self.__gemini_client = gemini_client
        
    def set_candle_service(self, candle_service: CandleService):
        self.__candle_service = candle_service
        
    async def execute_trade_decision(self, candle_chart: CandleChart) -> Decision:
        """
            LLM(Large Language Model)을 사용하여 거래 결정을 실행합니다.
            이 메서드는 캔들 차트 데이터를 기반으로 LLM에 요청을 보내고, LLM이 생성한 응답을 해석하여 거래 결정을 내립니다.
            LLM 요청 스키마를 기반으로 프롬프트를 구성하고, 캔들 데이터, 현재 가격, 현재 시간 등의 정보를 프롬프트에 삽입합니다.
            LLM으로부터 받은 응답은 JSON 형식으로 파싱되어 Decision 객체로 변환됩니다.
            Args:
                candle_chart (CandleChart): 거래 결정을 내리는 데 사용될 캔들 차트 데이터.
            Returns:
                Decision: LLM에 의해 생성된 거래 결정.
        """
        
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
        """
            현재 가격으로 지정된 코인을 판매합니다.
            Args:
                coin (dict): 판매할 코인. 이 값은 최소한 코인의 'id'를 포함하는 딕셔너리여야 합니다.
                current_price (float): 코인의 현재 시장 가격.
            Returns:
                None
            Raises:
                기본 레포지토리 메서드에서 발생하는 예외.
        """
        
        # 코인 판매 로직 실행 및 판매 금액 반환
        price = self.__action_log_repo.sell_coin(current_price, coin)
        # 코인 레포지토리에서 판매된 코인 정보 삭제
        self.__coin_repo.sell_coin(coin['id'])
        # Info 레포지토리에서 잔액 추가
        self.__info_repo.plus_balance(1, price)
        
    def buy_coin(self, decision: Decision):
        """
            코인을 구매하는 메서드.
            DCA(Dollar-Cost Averaging) 전략에 따라 사용 가능한 잔액의 일정 비율만큼 코인을 구매한다.
            구매 금액은 소수점 이하를 버림하여 정수로 만들고, 해당 금액으로 코인을 구매한다.
            구매 후 구매 정보는 코인 레포지토리에 저장하고, Info 레포지토리에서 잔액을 차감한다.
            Args:
                decision (Decision): 코인 구매 결정 정보. 시장(market)과 현재 가격(current_price)을 포함한다.
            Returns:
                None
            Raises:
                None: 예외는 발생하지 않는다.
        """
        
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