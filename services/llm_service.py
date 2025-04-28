import json
import re
import datetime
from clients.gemini_client import GeminiClient
from dtos.candle_chart import CandleChart
from dtos.decision import Decision
from repos.llm_log_repo import LLMLogRepo
from services.candle_service import CandleService
from services.decision_service import DecisionService
from settings.db_connection import DBMS

class LLMService(DecisionService):
    def __init__(self, llm_request_scheme: str, debug = False):
        self.__llm_request_scheme = llm_request_scheme
        self.__debug = debug

    def _log_debug(self, message: str):
        """디버그 메시지를 출력하는 헬퍼 메서드"""
        if self.__debug:
            print(f"LLMService: {message}")
    
    def set_gemini_client(self, gemini_client: GeminiClient):
        self.__gemini_client = gemini_client
                
    def set_candle_service(self, candle_service: CandleService):
        self.__candle_service = candle_service
        
    def set_llm_log_repo(self, llm_log_repo: LLMLogRepo):
        self.__llm_log_repo = llm_log_repo
        
    def set_dbms(self, dbms: DBMS):
        self.__dbms = dbms

    def _generate_prompt(self, candle_chart: CandleChart) -> str:
        """LLM 요청을 위한 프롬프트를 생성합니다."""
        prompt = self.__llm_request_scheme
        timeframes = candle_chart.get_all_timeframes()

        # 동적으로 캔들 데이터 섹션 생성
        candle_data_markdown = ""
        for timeframe in timeframes:
            candles = candle_chart.get_candles(timeframe)
            if candles:
                json_string = self.__candle_service.candle_to_json(candles)
                candle_data_markdown += f"*   {timeframe} chart:\n  ```json\n  {json_string}\n  ```\n\n"
            else:
                candle_data_markdown += f"*   {timeframe} chart:\n  ```json\n  No data available for this timeframe\n  ```\n\n"

        # 생성된 마크다운으로 플레이스홀더 교체
        prompt = prompt.replace("$candle_data_section", candle_data_markdown.strip())

        prompt = prompt.replace("$current_price", str(candle_chart.current_price))
        prompt = prompt.replace("$current_time", datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))

        self._log_debug(f"Generated prompt for LLM:\n{prompt}")
        return prompt

    def _parse_llm_response(self, response_text: str, candle_chart: CandleChart) -> Decision:
        """LLM 응답을 파싱하여 Decision 객체를 생성합니다."""
        try:
            decision_json = json.loads(response_text)
        except json.JSONDecodeError as e:
            error_message = f"Error parsing LLM response: {str(e)}"
            self._log_debug(error_message)
            self._log_debug(f"Invalid response: {response_text}")
            # 파싱 오류 시 기본 결정 생성
            decision_json = {"action": "wait", "reason": error_message}

        decision = Decision(decision_json)
        decision.set_current_price(candle_chart.current_price)
        decision.set_market(candle_chart.market)
        return decision

    def _log_decision(self, decision: Decision):
        """결정을 데이터베이스에 로깅합니다."""
        try:
            with self.__dbms.get_session() as session:
                self.__llm_log_repo.log_decision(decision, session)
            self._log_debug("Logged decision to DB.")
        except Exception as log_error:
            self._log_debug(f"Error logging decision to DB: {str(log_error)}")

    def _handle_error(self, error: Exception, candle_chart: CandleChart) -> Decision:
        """오류 발생 시 기본 결정을 생성하고 로깅합니다."""
        error_message = f"Error in LLM service: {str(error)}"
        self._log_debug(error_message)

        decision_json = {"action": "wait", "reason": error_message}
        decision = Decision(decision_json)
        decision.set_current_price(candle_chart.current_price)
        decision.set_market(candle_chart.market)

        # 오류 발생 시에도 로깅 시도
        self._log_decision(decision)
        return decision

    async def execute_trade_decision(self, candle_chart: CandleChart) -> Decision:
        """
        LLM(Large Language Model)을 사용하여 거래 결정을 실행합니다.
        """
        self._log_debug(f"Executing trade decision for market {candle_chart.market}")

        try:
            # 1. 프롬프트 생성
            prompt = self._generate_prompt(candle_chart)

            # 2. LLM 응답 생성
            # await 제거 - generate_answer는 비동기 함수가 아님
            response_text = self.__gemini_client.generate_answer(prompt)

            # 3. 응답 파싱 및 Decision 생성
            decision = self._parse_llm_response(response_text, candle_chart)

            self._log_debug(f"Received decision from LLM: {decision.action} with reason: {decision.reason}")

            # 4. 결정 로깅
            self._log_decision(decision)

            return decision

        except Exception as e:
            # 5. 예외 처리
            return self._handle_error(e, candle_chart)