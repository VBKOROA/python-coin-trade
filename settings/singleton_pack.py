import os
import json

from dotenv import load_dotenv
from clients.gemini_client import GeminiClient
from clients.upbit_client import UpbitClient
from repos.action_repo import ActionRepo
from repos.coin_repo import CoinRepo
from repos.llm_log_repo import LLMLogRepo
from repos.member_repo import MemberRepo
from services.action_service import ActionService
from services.candle_service import CandleService
from services.llm_service import LLMService
from services.trade_service import TradeService
from settings.db_connection import DBMS

class SingletonPack:
    """
        설정 값들을 담고, 싱글톤 객체들을 초기화 및 관리하는 클래스.
        환경 변수를 로드하고, 필요한 상수 값들을 설정하며, 각 서비스 객체들을 싱글톤으로 관리하여
        전역적으로 접근할 수 있도록 한다. DBMS, GeminiClient, UpbitClient, ActionService,
        TradeService, CandleService 등의 객체를 생성하고,
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
            candle_service (CandleService): 캔들 서비스 객체.
        Methods:
            initialize_dependencies(): 객체 간의 의존성을 초기화한다. 각 서비스 객체에 필요한 저장소 및 클라이언트를 설정한다.
            set_action_service(action_service: ActionService): ActionService 객체를 설정한다.
            set_dbms(dbms: DBMS): DBMS 객체를 설정한다.
            set_candle_service(candle_service: CandleService): CandleService 객체를 설정한다.
            set_gemini_client(gemini_client: GeminiClient): GeminiClient 객체를 설정한다.
            set_upbit_client(upbit_client: UpbitClient): UpbitClient 객체를 설정한다.
            set_trade_service(trade_service: TradeService): TradeService 객체를 설정한다.
    """
    
    def __init__(self):
        # 환경변수 로드
        load_dotenv()
        
        # 상수
        self.LLM_API_KEY = os.environ.get("API_KEY") # LLM API 키
        if not self.LLM_API_KEY:
            raise ValueError("API_KEY 환경 변수가 설정되지 않았습니다.")
        self.LLM_REQUEST_SCHEME = open("./scheme/request.scheme.md", "r").read() # LLM 요청 구조
        self.LLM_RESPONSE_SCHEME = open("./scheme/response.scheme.json", "r").read() # LLM 응답 구조
        self.LLM_MODEL = os.environ.get("LLM_MODEL") # LLM 모델 (ex. gemini-2.0-pro-exp-02-05)
        self.MARKET = os.environ.get("MARKET") # 거래소 마켓 (ex. KRW-BTC)
        self.DEBUG = bool(os.environ.get("DEBUG"))
        
        # DCA 비율 설정
        temp = os.environ.get("DCA")
        self.DCA = float(temp) / 100 if temp else 0.01 # DCA 비율 (ex. 0.01 = 1%)
        
        # 시간대 설정 로드 및 유효성 검사
        timeframe_config_str = os.environ.get("TIMEFRAME_CONFIG")
        if timeframe_config_str:
            try:
                self.TIMEFRAME_CONFIG = json.loads(timeframe_config_str)
                if not isinstance(self.TIMEFRAME_CONFIG, dict) or not self.TIMEFRAME_CONFIG:
                    raise ValueError("TIMEFRAME_CONFIG는 비어 있지 않은 JSON 객체여야 합니다.")
            except json.JSONDecodeError:
                raise ValueError("TIMEFRAME_CONFIG 환경 변수가 유효한 JSON 형식이 아닙니다.")
            except ValueError as e:
                raise ValueError(f"TIMEFRAME_CONFIG 설정 오류: {e}")
        else:
            # 기본값 설정 또는 오류 발생 (오류 발생 선택)
            raise ValueError("TIMEFRAME_CONFIG 환경 변수가 설정되지 않았습니다.")

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
            llm_response_scheme=self.LLM_RESPONSE_SCHEME,
            debug=self.DEBUG
        ))
        self.set_upbit_client(UpbitClient(self.MARKET, self.DEBUG))
        self.set_action_service(ActionService(self.DCA, self.DEBUG))
        self.set_trade_service(TradeService(self.TIMEFRAME_CONFIG, self.DEBUG))
        self.set_llm_service(LLMService(self.LLM_REQUEST_SCHEME, self.DEBUG))
        self.set_candle_service(CandleService())
        self.set_llm_log_repo(LLMLogRepo())
        self.set_member_repo(MemberRepo())
        self.set_action_repo(ActionRepo())
        self.set_coin_repo(CoinRepo())
        self.initialize_dependencies()
        
    def initialize_dependencies(self):
        self.trade_service.set_upbit_client(self.upbit_client)
        self.trade_service.set_action_service(self.action_service)
        self.trade_service.set_dbms(self.dbms)
        self.trade_service.set_member_repo(self.member_repo)
        self.trade_service.set_llm_service(self.llm_service)
        self.llm_service.set_gemini_client(self.gemini_client)
        self.llm_service.set_candle_service(self.candle_service)
        self.llm_service.set_llm_log_repo(self.llm_log_repo)
        self.llm_service.set_dbms(self.dbms)
        self.action_service.set_action_repo(self.action_repo)
        self.action_service.set_coin_repo(self.coin_repo)
    
    def __parse_timeframe_to_minutes(self, timeframe: str) -> int:
        """ 시간대 문자열을 분 단위 정수로 변환합니다. (예: '5m' -> 5, '1h' -> 60) """
        unit_map = {'m': 1, 'h': 60, 'd': 1440, 'w': 10080} # 분, 시, 일, 주
        try:
            if timeframe[-1] in unit_map:
                unit = timeframe[-1]
                value = int(timeframe[:-1])
                return value * unit_map[unit]
            else: # 분 단위 숫자만 있는 경우 (Upbit API 호환)
                return int(timeframe)
        except (ValueError, IndexError, KeyError):
            # 숫자만 있는 경우 분으로 간주 (예: '3', '5', '10')
            try:
                return int(timeframe)
            except ValueError:
                raise ValueError(f"지원하지 않거나 잘못된 시간대 형식입니다: {timeframe}")
    
    def get_smallest_timeframe_minutes(self) -> int:
        """ TIMEFRAME_CONFIG에서 가장 작은 시간 간격(분)을 반환합니다. """
        if not self.TIMEFRAME_CONFIG:
            # 설정이 없을 경우 기본값 또는 오류 처리 (여기서는 오류 발생시키도록 __init__에서 처리됨)
            raise ValueError("TIMEFRAME_CONFIG가 설정되지 않아 최소 시간 간격을 계산할 수 없습니다.")

        try:
            minutes = [self.__parse_timeframe_to_minutes(tf) for tf in self.TIMEFRAME_CONFIG.keys()]
            if not minutes:
                raise ValueError("TIMEFRAME_CONFIG에 유효한 시간대가 없습니다.")
            smallest = min(minutes)
            if smallest <= 0:
                raise ValueError("시간 간격은 0보다 커야 합니다.")
            return smallest
        except ValueError as e:
            # __parse_timeframe_to_minutes 에서 발생한 오류 포함
            raise ValueError(f"TIMEFRAME_CONFIG 처리 중 오류 발생: {e}")
        
    def set_action_service(self, action_service: ActionService):
        self.action_service = action_service
    
    def set_dbms(self, dbms: DBMS):
        self.dbms = dbms
        self.dbms.setup(drop=self.DEBUG)
        
    def set_candle_service(self, candle_service: CandleService):
        self.candle_service = candle_service
        
    def set_gemini_client(self, gemini_client: GeminiClient):
        self.gemini_client = gemini_client
        
    def set_upbit_client(self, upbit_client: UpbitClient):
        self.upbit_client = upbit_client
        
    def set_trade_service(self, trade_service: TradeService):
        self.trade_service = trade_service
        
    def set_llm_service(self, llm_service: LLMService):
        self.llm_service = llm_service
        
    def set_llm_log_repo(self, llm_log_repo: LLMLogRepo):
        self.llm_log_repo = llm_log_repo
        
    def set_member_repo(self, member_repo: MemberRepo):
        self.member_repo = member_repo
        
    def set_action_repo(self, action_repo: ActionRepo):
        self.action_repo = action_repo
        
    def set_coin_repo(self, coin_repo: CoinRepo):
        self.coin_repo = coin_repo