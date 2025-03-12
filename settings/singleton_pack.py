import os
import json

from dotenv import load_dotenv
from api.gemini_client import GeminiClient
from api.upbit_client import UpbitClient
from repos.info_repo import InfoRepo
from services.action_service import ActionService
from services.candle_service import CandleService
from services.trade_service import TradeService
from settings.db_connection import DBMS
from repos.coin_repo import CoinRepo
from repos.action_log_repo import ActionLogRepo
from repos.llm_log_repo import LLMLogRepo

class SingletonPack:
    def __init__(self):
        # 환경변수 로드
        load_dotenv()
        
        # 상수
        self.LLM_API_KEY = os.environ.get("API_KEY") # LLM API 키
        self.LLM_REQUEST_SCHEME = open("request.scheme.md", "r").read() # LLM 요청 구조
        self.LLM_RESPONSE_SCHEME = open("response.scheme.json", "r").read() # LLM 응답 구조
        self.LLM_MODEL = os.environ.get("LLM_MODEL") # LLM 모델 (ex. gemini-2.0-pro-exp-02-05)
        self.MARKET = os.environ.get("MARKET") # 거래소 마켓 (ex. KRW-BTC)
        print(f"거래 종목 설정: {self.MARKET}")
        # DCA 비율 설정
        temp = os.environ.get("DCA")
        self.DCA = int(temp) / 100 # DCA 비율 (ex. 0.01 = 1%)
        # 시간대 설정
        timeframe_config_str = os.environ.get("TIMEFRAME_CONFIG")
        self.TIMEFRAME_CONFIG = json.loads(timeframe_config_str)
        print(f"시간대 설정: {self.TIMEFRAME_CONFIG}")

        # 싱글톤
        self.set_dbms(DBMS(
            host=os.environ.get("DB_HOST"),
            port=int(os.environ.get("DB_PORT")),
            user=os.environ.get("DB_USER"),
            password=os.environ.get("DB_PASSWORD"),
            name=os.environ.get("DB_NAME")
        ))
        self.set_gemini_client(GeminiClient(
            llm_key=self.LLM_API_KEY,
            llm_model = self.LLM_MODEL,
            llm_response_scheme=self.LLM_RESPONSE_SCHEME
        ))
        self.set_upbit_client(UpbitClient(self.MARKET))
        self.set_action_service(ActionService(
            llm_request_scheme=self.LLM_REQUEST_SCHEME,
            dca=self.DCA
        ))
        self.set_trade_service(TradeService(self.TIMEFRAME_CONFIG))
        self.set_info_repo(InfoRepo())
        self.set_action_log_repo(ActionLogRepo())
        self.set_llm_log_repo(LLMLogRepo())
        self.set_coin_repo(CoinRepo())
        self.set_candle_service(CandleService())
        self.initialize_dependencies()
        
    def initialize_dependencies(self):
        self.info_repo.set_dbms(self.dbms)
        self.action_log_repo.set_dbms(self.dbms)
        self.llm_log_repo.set_dbms(self.dbms)
        self.coin_repo.set_dbms(self.dbms)
        self.action_service.set_action_log_repo(self.action_log_repo)
        self.action_service.set_candle_service(self.candle_service)
        self.action_service.set_coin_repo(self.coin_repo)
        self.action_service.set_info_repo(self.info_repo)
        self.action_service.set_llm_log_repo(self.llm_log_repo)
        self.action_service.set_gemini_client(self.gemini_client)
        self.trade_service.set_upbit_client(self.upbit_client)
        self.trade_service.set_coin_repo(self.coin_repo)
        self.trade_service.set_action_service(self.action_service)
        self.trade_service.set_conn(self.dbms.conn)
        
    def set_action_service(self, action_service: ActionService):
        self.action_service = action_service
    
    def set_dbms(self, dbms: DBMS):
        self.dbms = dbms
        
    def set_candle_service(self, candle_service: CandleService):
        self.candle_service = candle_service
        
    def set_info_repo(self, info_repo: InfoRepo):
        self.info_repo = info_repo
        
    def set_gemini_client(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        
    def set_upbit_client(self, upbit_client: UpbitClient):
        self.upbit_client = upbit_client
        
    def set_trade_service(self, trade_service: TradeService):
        self.trade_service = trade_service
        
    def set_coin_repo(self, coin_repo: CoinRepo):
        self.coin_repo = coin_repo
        
    def set_action_log_repo(self, action_log_repo: ActionLogRepo):
        self.action_log_repo = action_log_repo
        
    def set_llm_log_repo(self, llm_log_repo: LLMLogRepo):
        self.llm_log_repo = llm_log_repo