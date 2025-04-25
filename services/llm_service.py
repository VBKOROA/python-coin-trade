import json
import re
from api.gemini_client import GeminiClient
from models.dto.candle_chart import CandleChart
from models.dto.decision import Decision
from repos.llm_log_repo import LLMLogRepo
from services.candle_service import CandleService
from settings.db_connection import DBMS

class LLMService:
    def __init__(self, llm_request_scheme: str, debug = False):
        self.__llm_request_scheme = llm_request_scheme
        self.__debug = debug
    
    def set_gemini_client(self, gemini_client: GeminiClient):
        self.__gemini_client = gemini_client
                
    def set_candle_service(self, candle_service: CandleService):
        self.__candle_service = candle_service
        
    def set_llm_log_repo(self, llm_log_repo: LLMLogRepo):
        self.__llm_log_repo = llm_log_repo
        
    def set_dbms(self, dbms: DBMS):
        self.__dbms = dbms
                
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
        if self.__debug:
            print(f"LLMService: Executing trade decision for market {candle_chart.market}")

        # LLM 요청 구조 복사
        prompt = self.__llm_request_scheme

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

        # # 현재 가격 삽입
        # prompt = prompt.replace("$current_price", str(candle_chart.current_price))

        # # 현재 시간 삽입 (datetime 사용) (yyyy-MM-dd'T'HH:mm:ss 형식)
        # prompt = prompt.replace("$current_time", datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

        if self.__debug:
            print(f"LLMService: Generated prompt for LLM:\n{prompt}")

        try:
            # LLM 응답 생성
            response_text = self.__gemini_client.generate_answer(prompt)
            
            # JSON 응답 파싱
            try:
                decision_json = json.loads(response_text)
            except json.JSONDecodeError as e:
                if self.__debug:
                    print(f"LLMService: Error parsing JSON response: {str(e)}")
                    print(f"LLMService: Invalid response: {response_text}")
                # 기본 결정 생성
                decision_json = {"action": "wait", "reason": f"Error parsing LLM response: {str(e)}"}
            
            decision = Decision(decision_json)
            decision.set_current_price(candle_chart.current_price)
            decision.set_market(candle_chart.market)

            if self.__debug:
                print(f"LLMService: Received decision from LLM: {decision.action} with reason: {decision.reason}")

            with self.__dbms.get_session() as session:
                self.__llm_log_repo.log_decision(decision, session)

            if self.__debug:
                print(f"LLMService: Logged decision to DB.")

            return decision
            
        except Exception as e:
            if self.__debug:
                print(f"LLMService: Error executing trade decision: {str(e)}")
            
            # 에러 발생 시 기본 결정 반환
            decision_json = {"action": "wait", "reason": f"Error in LLM service: {str(e)}"}
            decision = Decision(decision_json)
            decision.set_current_price(candle_chart.current_price)
            decision.set_market(candle_chart.market)
            
            try:
                with self.__dbms.get_session() as session:
                    self.__llm_log_repo.log_decision(decision, session)
            except Exception as log_error:
                if self.__debug:
                    print(f"LLMService: Error logging decision to DB: {str(log_error)}")
            
            return decision