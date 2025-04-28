import pandas as pd # 데이터 처리를 위해 pandas 사용
from dtos.candle_chart import CandleChart
from dtos.decision import Decision
from services.decision_service import DecisionService
import numpy as np # NaN 값 처리를 위해 numpy 사용
import re # 시간 프레임 문자열 파싱을 위해 re 사용
from enum import Enum # Enum 정의를 위해 enum 모듈 추가

# Action 열거형 정의
class Action(str, Enum):
    BUY = "BUY"
    SELL = "SELL"
    NEUTRAL = "NEUTRAL"

# Trend 열거형 정의
class Trend(str, Enum):
    BULLISH = "BULLISH"
    BEARISH = "BEARISH"
    NEUTRAL = "NEUTRAL"

class CandleAnalysisService(DecisionService):
    # Ichimoku 파라미터를 클래스 상수로 정의
    DEFAULT_TENKAN_PERIOD = 9
    DEFAULT_KIJUN_PERIOD = 26
    DEFAULT_SENKOU_B_PERIOD = 52
    DEFAULT_CHIKOU_OFFSET = 26
    DEFAULT_SENKOU_OFFSET = 26

    def __init__(self,
                 strict_mode: bool = False,
                 debug: bool = False,
                 tenkan_period: int = DEFAULT_TENKAN_PERIOD,
                 kijun_period: int = DEFAULT_KIJUN_PERIOD,
                 senkou_b_period: int = DEFAULT_SENKOU_B_PERIOD,
                 chikou_offset: int = DEFAULT_CHIKOU_OFFSET,
                 senkou_offset: int = DEFAULT_SENKOU_OFFSET):
        """
        Ichimoku Multi-Timeframe 분석 서비스 초기화
        Args:
            debug (bool): 디버그 모드 활성화 여부
            tenkan_period (int): Tenkan-sen 기간
            kijun_period (int): Kijun-sen 기간
            senkou_b_period (int): Senkou Span B 기간
            chikou_offset (int): Chikou Span 오프셋
            senkou_offset (int): Senkou Span 오프셋
        """
        self.debug = debug
        self.strict_mode = strict_mode
        self.tenkan_period = tenkan_period
        self.kijun_period = kijun_period
        self.senkou_b_period = senkou_b_period
        self.chikou_offset = chikou_offset
        self.senkou_offset = senkou_offset
        
    def _log_debug(self, message: str):
        """디버그 메시지를 출력하는 헬퍼 메서드"""
        if self.debug:
            print(f"CandleAnalysisService: {message}")

    def _parse_timeframe_to_minutes(self, timeframe: str) -> int:
        """시간 프레임 문자열을 분 단위로 변환 (예: '1d', '4h', '15m')"""
        match = re.match(r"(\d+)([mhd])", timeframe, re.IGNORECASE)
        if not match:
            raise ValueError(f"Invalid timeframe format: {timeframe}")
        
        value, unit = int(match.group(1)), match.group(2).lower()
        
        if unit == 'm':
            return value
        elif unit == 'h':
            return value * 60
        elif unit == 'd':
            return value * 60 * 24
        else:
            raise ValueError(f"Unknown timeframe unit: {unit}")

    def _calculate_ichimoku(self, df: pd.DataFrame) -> pd.DataFrame:
        """Ichimoku 지표 계산"""
        self._log_debug("Calculating Ichimoku indicators")
        # Tenkan-sen (Conversion Line)
        high_tenkan = df['high'].rolling(window=self.tenkan_period).max()
        low_tenkan = df['low'].rolling(window=self.tenkan_period).min()
        df['tenkan_sen'] = (high_tenkan + low_tenkan) / 2

        # Kijun-sen (Base Line)
        high_kijun = df['high'].rolling(window=self.kijun_period).max()
        low_kijun = df['low'].rolling(window=self.kijun_period).min()
        df['kijun_sen'] = (high_kijun + low_kijun) / 2

        # Senkou Span A (Leading Span A)
        # senkou_offset 기간만큼 앞으로 이동하여 플롯됨
        df['senkou_span_a'] = ((df['tenkan_sen'] + df['kijun_sen']) / 2).shift(self.senkou_offset)

        # Senkou Span B (Leading Span B)
        high_senkou_b = df['high'].rolling(window=self.senkou_b_period).max()
        low_senkou_b = df['low'].rolling(window=self.senkou_b_period).min()
        # senkou_offset 기간만큼 앞으로 이동하여 플롯됨
        df['senkou_span_b'] = ((high_senkou_b + low_senkou_b) / 2).shift(self.senkou_offset)
        
        # Kumo (Cloud) Top/Bottom - 현재 시점 기준 구름대 계산 (미래 플롯된 값 사용)
        # 실제 분석 시점에서는 미래의 구름대를 현재 가격과 비교해야 함
        df['kumo_top'] = df[['senkou_span_a', 'senkou_span_b']].max(axis=1)
        df['kumo_bottom'] = df[['senkou_span_a', 'senkou_span_b']].min(axis=1)

        # Chikou Span (Lagging Span)
        # chikou_offset 기간만큼 뒤로 이동하여 플롯됨
        df['chikou_span'] = df['close'].shift(-self.chikou_offset)
        
        # Chikou Span 비교를 위한 과거 가격
        # 현재 Chikou Span 위치에 해당하는 과거 종가
        df['price_at_chikou_time'] = df['close'] 
        
        self._log_debug("Ichimoku indicators calculation completed")
        return df

    def execute_trade_decision(self, candle_chart: CandleChart) -> Decision:
        """Ichimoku Multi-Timeframe 전략 실행"""
        self._log_debug(f"Executing trade decision for market {candle_chart.market}")
        
        available_timeframes = candle_chart.get_all_timeframes()
        if len(available_timeframes) < 2:
            self._log_debug("Insufficient timeframes: requires at least two timeframes")
            return Decision({"action": Action.NEUTRAL, "reason": "Requires at least two timeframes in CandleChart"})

        # 시간 프레임을 분 단위로 변환하여 정렬
        try:
            timeframes_minutes = {tf: self._parse_timeframe_to_minutes(tf) for tf in available_timeframes}
            self._log_debug(f"Parsed timeframes to minutes: {timeframes_minutes}")
        except ValueError as e:
             self._log_debug(f"Error parsing timeframes: {e}")
             return Decision({"action": Action.NEUTRAL, "reason": f"Error parsing timeframes: {e}"})
             
        sorted_timeframes = sorted(timeframes_minutes.keys(), key=lambda tf: timeframes_minutes[tf])
        
        # 가장 짧은 시간 프레임을 LTF, 가장 긴 시간 프레임을 HTF로 설정
        ltf = sorted_timeframes[0]
        htf = sorted_timeframes[-1]
        self._log_debug(f"Using LTF: {ltf}, HTF: {htf}")

        htf_candles = candle_chart.get_candles(htf)
        ltf_candles = candle_chart.get_candles(ltf)
        current_price = candle_chart.current_price
        market = candle_chart.market

        if not htf_candles or not ltf_candles or len(htf_candles) < self.senkou_b_period or len(ltf_candles) < self.senkou_b_period:
            self._log_debug(f"Insufficient candle data for HTF({htf}) or LTF({ltf})")
            return Decision({"action": Action.NEUTRAL, "reason": f"Insufficient candle data for HTF({htf}) or LTF({ltf})"})

        # 데이터프레임 생성 (컬럼명은 일반적인 형태 가정, 필요시 조정)
        self._log_debug("Creating dataframes for HTF and LTF")
        htf_df = pd.DataFrame(htf_candles)
        htf_df.rename(columns={'high_price': 'high', 'low_price': 'low', 'trade_price': 'close', 'opening_price': 'open'}, inplace=True)
        htf_df['timestamp'] = pd.to_datetime(htf_df['candle_date_time_kst'])
        htf_df.set_index('timestamp', inplace=True)
        htf_df.sort_index(inplace=True)

        ltf_df = pd.DataFrame(ltf_candles)
        ltf_df.rename(columns={'high_price': 'high', 'low_price': 'low', 'trade_price': 'close', 'opening_price': 'open'}, inplace=True)
        ltf_df['timestamp'] = pd.to_datetime(ltf_df['candle_date_time_kst'])
        ltf_df.set_index('timestamp', inplace=True)
        ltf_df.sort_index(inplace=True)

        # Ichimoku 지표 계산
        self._log_debug("Calculating Ichimoku indicators for HTF and LTF")
        htf_ichimoku = self._calculate_ichimoku(htf_df.copy())
        ltf_ichimoku = self._calculate_ichimoku(ltf_df.copy())

        # 최신 데이터 가져오기 (NaN 값 제거 후)
        htf_analysis = htf_ichimoku.dropna()
        if htf_analysis.empty:
            self._log_debug(f"HTF({htf}) data insufficient after dropna()")
            return Decision({"action": Action.NEUTRAL, "reason": f"HTF({htf}) data insufficient after dropna()"})
        htf_latest = htf_analysis.iloc[-1]
        # LTF는 현재와 이전 캔들 필요 (크로스오버 확인용)
        ltf_analysis = ltf_ichimoku.dropna()
        if len(ltf_analysis) < 2:
             self._log_debug(f"Insufficient LTF({ltf}) data for crossover analysis")
             return Decision({"action": Action.NEUTRAL, "reason": f"Insufficient LTF({ltf}) data for crossover analysis"})
        ltf_latest = ltf_analysis.iloc[-1]
        ltf_previous = ltf_analysis.iloc[-2]

        # --- HTF Trend Assessment ---
        self._log_debug("Assessing HTF trend")
        htf_trend = Trend.NEUTRAL
        # Chikou Span 비교를 위한 과거 가격 (chikou_offset 이전 캔들)
        htf_price_at_chikou_time_index = htf_ichimoku.index.get_loc(htf_latest.name) - self.chikou_offset
        htf_price_at_chikou_time = np.nan
        if htf_price_at_chikou_time_index >= 0 and htf_price_at_chikou_time_index < len(htf_ichimoku): # 인덱스 범위 확인 추가
             htf_price_at_chikou_time = htf_ichimoku.iloc[htf_price_at_chikou_time_index]['close']

        is_htf_bullish = (htf_latest['close'] > htf_latest['kumo_top'] and 
                          not np.isnan(htf_price_at_chikou_time) and
                          htf_latest['chikou_span'] > htf_price_at_chikou_time)
                          
        is_htf_bearish = (htf_latest['close'] < htf_latest['kumo_bottom'] and
                          not np.isnan(htf_price_at_chikou_time) and
                          htf_latest['chikou_span'] < htf_price_at_chikou_time)

        if self.strict_mode:
            # 추가적인 조건을 확인합니다.
            is_htf_bullish = is_htf_bullish and htf_latest['senkou_span_a'] > htf_latest['senkou_span_b']
            is_htf_bearish = is_htf_bearish and htf_latest['senkou_span_a'] < htf_latest['senkou_span_b']

        if is_htf_bullish:
            htf_trend = Trend.BULLISH
            self._log_debug("HTF trend is BULLISH")
        elif is_htf_bearish:
            htf_trend = Trend.BEARISH
            self._log_debug("HTF trend is BEARISH")
        else:
            self._log_debug("HTF trend is NEUTRAL")

        # --- LTF Entry Signal Generation ---
        self._log_debug("Generating LTF entry signals")
        action = Action.NEUTRAL
        reason = f"HTF({htf}) Trend: {htf_trend}"

        # Chikou Span 비교를 위한 과거 가격 (chikou_offset 이전 캔들)
        ltf_price_at_chikou_time_index = ltf_ichimoku.index.get_loc(ltf_latest.name) - self.chikou_offset
        ltf_price_at_chikou_time = np.nan
        if ltf_price_at_chikou_time_index >= 0 and ltf_price_at_chikou_time_index < len(ltf_ichimoku): # 인덱스 범위 확인 추가
             ltf_price_at_chikou_time = ltf_ichimoku.iloc[ltf_price_at_chikou_time_index]['close']

        if htf_trend == Trend.BULLISH:
            # LTF Buy Signal (TK Cross Above Kumo)
            tk_crossed_up = (ltf_previous['tenkan_sen'] <= ltf_previous['kijun_sen'] and 
                             ltf_latest['tenkan_sen'] > ltf_latest['kijun_sen'])
            cross_above_kumo = ltf_latest['tenkan_sen'] > ltf_latest['kumo_top'] # 크로스 지점 또는 현재 종가 기준
            price_above_kumo = ltf_latest['close'] > ltf_latest['kumo_top']
            chikou_confirms = (not np.isnan(ltf_price_at_chikou_time) and 
                               ltf_latest['chikou_span'] > ltf_price_at_chikou_time)

            if tk_crossed_up and cross_above_kumo and price_above_kumo and chikou_confirms:
                action = Action.BUY
                reason = f"HTF({htf}) Bullish & LTF({ltf}) TK Cross Above Kumo Confirmed. HTF Close: {htf_latest['close']:.2f}, HTF Kumo Top: {htf_latest['kumo_top']:.2f}. LTF Close: {ltf_latest['close']:.2f}, LTF Kumo Top: {ltf_latest['kumo_top']:.2f}"
                self._log_debug(f"BUY signal generated: {reason}")

        elif htf_trend == Trend.BEARISH:
            # LTF Sell Signal (TK Cross Below Kumo)
            tk_crossed_down = (ltf_previous['tenkan_sen'] >= ltf_previous['kijun_sen'] and 
                               ltf_latest['tenkan_sen'] < ltf_latest['kijun_sen'])
            cross_below_kumo = ltf_latest['tenkan_sen'] < ltf_latest['kumo_bottom'] # 크로스 지점 또는 현재 종가 기준
            price_below_kumo = ltf_latest['close'] < ltf_latest['kumo_bottom']
            chikou_confirms = (not np.isnan(ltf_price_at_chikou_time) and 
                               ltf_latest['chikou_span'] < ltf_price_at_chikou_time)

            if tk_crossed_down and cross_below_kumo and price_below_kumo and chikou_confirms:
                action = Action.SELL
                reason = f"HTF({htf}) Bearish & LTF({ltf}) TK Cross Below Kumo Confirmed. HTF Close: {htf_latest['close']:.2f}, HTF Kumo Bottom: {htf_latest['kumo_bottom']:.2f}. LTF Close: {ltf_latest['close']:.2f}, LTF Kumo Bottom: {ltf_latest['kumo_bottom']:.2f}"
                self._log_debug(f"SELL signal generated: {reason}")

        decision = Decision({"action": action, "reason": reason})
        decision.set_current_price(current_price)
        decision.set_market(market)
        self._log_debug(f"Final decision: {action} with reason: {reason}")
        return decision