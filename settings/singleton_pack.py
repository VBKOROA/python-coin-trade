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
    """
        설정 값들을 담고, 싱글톤 객체들을 초기화 및 관리하는 클래스.
        환경 변수를 로드하고, 필요한 상수 값들을 설정하며, 각 서비스 객체들을 싱글톤으로 관리하여
        전역적으로 접근할 수 있도록 한다. DBMS, GeminiClient, UpbitClient, ActionService,
        TradeService, InfoRepo, ActionLogRepo, LLMLogRepo, CoinRepo, CandleService 등의 객체를 생성하고,
        각 객체 간의 의존성을 설정하여 전체 시스템을 구성한다.
        Attributes:
            LLM_API_KEY (str): LLM API 키. 환경 변수에서 로드.
            LLM_REQUEST_SCHEME (str): LLM 요청 구조. 파일에서 읽어옴.
            LLM_RESPONSE_SCHEME (str): LLM 응답 구조. 파일에서 읽어옴.
            LLM_MODEL (str): LLM 모델 이름. 환경 변수에서 로드.
            MARKET (str): 거래소 마켓. 환경 변수에서 로드. (ex. KRW-BTC)
            DCA (float): DCA 비율. 환경 변수에서 로드하여 퍼센트(%)로 변환. (ex. 0.01 = 1%)
            TIMEFRAME_CONFIG (dict): 시간대 설정. 환경 변수에서 JSON 형태로 로드.
            dbms (DBMS): 데이터베이스 관리 시스템 객체.
            gemini_client (GeminiClient): Gemini API 클라이언트 객체.
            upbit_client (UpbitClient): Upbit API 클라이언트 객체.
            action_service (ActionService): 액션 서비스 객체.
            trade_service (TradeService): 거래 서비스 객체.
            info_repo (InfoRepo): 정보 저장소 객체.
            action_log_repo (ActionLogRepo): 액션 로그 저장소 객체.
            llm_log_repo (LLMLogRepo): LLM 로그 저장소 객체.
            coin_repo (CoinRepo): 코인 저장소 객체.
            candle_service (CandleService): 캔들 서비스 객체.
        Methods:
            initialize_dependencies(): 객체 간의 의존성을 초기화한다. 각 서비스 객체에 필요한 저장소 및 클라이언트를 설정한다.
            set_action_service(action_service: ActionService): ActionService 객체를 설정한다.
            set_dbms(dbms: DBMS): DBMS 객체를 설정한다.
            set_candle_service(candle_service: CandleService): CandleService 객체를 설정한다.
            set_info_repo(info_repo: InfoRepo): InfoRepo 객체를 설정한다.
            set_gemini_client(gemini_client: GeminiClient): GeminiClient 객체를 설정한다.
            set_upbit_client(upbit_client: UpbitClient): UpbitClient 객체를 설정한다.
            set_trade_service(trade_service: TradeService): TradeService 객체를 설정한다.
            set_coin_repo(coin_repo: CoinRepo): CoinRepo 객체를 설정한다.
            set_action_log_repo(action_log_repo: ActionLogRepo): ActionLogRepo 객체를 설정한다.
            set_llm_log_repo(llm_log_repo: LLMLogRepo): LLMLogRepo 객체를 설정한다.
    """
    
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