import asyncio
import aiohttp

from datetime import datetime, timedelta
from models.dto.candle_chart import CandleChart

class UpbitClient:
    def __init__(self, market: str):
        self.__MARKET = market
        # 지원하는 시간대와 각 시간대별 분 단위 매핑
        self.__TIMEFRAME_UNITS = {
            '1m': 1,
            '3m': 3,
            '5m': 5,
            '10m': 10,
            '15m': 15,
            '30m': 30,
            '1h': 60,
            '4h': 240,
            '1d': 1440,  # 하루는 1440분
        }
        # 기본 설정: 캔들 개수
        self.__DEFAULT_CANDLE_COUNTS = {
            '15m': 20,
            '1h': 5,
        }
        
    async def __req_data(self, unit: int, params: dict, session):
        url = f"https://api.upbit.com/v1/candles/minutes/{unit}"
        headers = {"accept": "application/json"}
        async with session.get(url, params=params, headers=headers) as response:
            return await response.json()

    def __get_timeframe_unit(self, timeframe: str) -> int:
        """
        시간대 문자열을 분 단위로 변환합니다.
        
        Args:
            timeframe (str): 시간대 (예: '15m', '1h').
            
        Returns:
            int: 분 단위의 시간.
            
        Raises:
            ValueError: 지원하지 않는 시간대가 주어졌을 때 발생.
        """
        unit = self.__TIMEFRAME_UNITS.get(timeframe)
        if not unit:
            raise ValueError(f"지원하지 않는 시간대입니다: {timeframe}")
        return unit
    
    def __get_completed_candle_time(self, timeframe: str) -> datetime:
        """
        현재 시간에서 가장 가까운 완료된 캔들 시간을 계산합니다.
        
        Args:
            timeframe (str): 시간대 (예: '15m', '1h').
            
        Returns:
            datetime: 완료된 캔들의 시간.
        """
        now = datetime.now()
        unit = self.__get_timeframe_unit(timeframe)
        
        # 시간대의 분 단위로 현재 시간을 조정
        minutes_to_subtract = now.minute % unit
        now = now - timedelta(minutes=minutes_to_subtract, seconds=now.second, microseconds=now.microsecond)
        
        return now
    
    def __filter_incomplete_candles(self, data: list, completed_time: datetime) -> list:
        """
        완료되지 않은 캔들을 필터링합니다.
        
        Args:
            data (list): 캔들 데이터 리스트.
            completed_time (datetime): 완료된 캔들의 기준 시간.
            
        Returns:
            list: 필터링된 캔들 데이터 리스트 (과거 순서로 정렬됨).
        """
        if not data:
            return []
            
        latest_candle = data[0]
        latest_candle_time = datetime.fromisoformat(latest_candle['candle_date_time_kst'])
        
        if latest_candle_time >= completed_time:
            # 완료되지 않은 최신 캔들 제거
            data.pop(0)
        elif len(data) > 1:  # 1개 이상의 캔들이 있을 때만 마지막 캔들 제거 고려
            # 완료된 최고 캔들 제거
            data.pop(-1)
        
        return data
        
    async def __get_candle_data(self, count: int, timeframe: str, session):
        """
        주어진 시장, 개수, 시간대에 따라 캔들 데이터를 비동기적으로 가져옵니다.
        Args:
            count (int): 요청할 캔들 데이터의 개수.
            timeframe (str): 시간대 (예: '15m', '1h').
            session: aiohttp 클라이언트 세션 객체.
        Returns:
            list: 과거 순으로 정렬된 캔들 데이터 리스트.
        """
        unit = self.__get_timeframe_unit(timeframe)
        
        params = {
            'market': self.__MARKET,
            'count': count + 1,  # 진행 중인 캔들을 고려해 하나 더 요청
        }
        
        data = await self.__req_data(unit, params, session)
        completed_time = self.__get_completed_candle_time(timeframe)
        
        return self.__filter_incomplete_candles(data, completed_time)
    
    async def fetch_candle_chart(self, timeframe_config=None) -> CandleChart:
        """
        주어진 시장에 대한 캔들 차트를 비동기적으로 가져옵니다.
        Args:
            timeframe_config (dict, optional): 시간대별 캔들 개수 구성. 기본값은 None.
                예: {'15m': 20, '1h': 5, '4h': 10}
                
        Returns:
            CandleChart: 요청한 시간대의 캔들 데이터와 현재 가격이 설정된 CandleChart 객체.
        """
        candle_chart = CandleChart()
        candle_chart.set_market(self.__MARKET)
        
        # 기본 설정 사용 또는 사용자 정의 설정 적용
        if not timeframe_config:
            timeframe_config = self.__DEFAULT_CANDLE_COUNTS
            
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # 각 시간대별 캔들 데이터 요청 태스크 생성
            for timeframe, count in timeframe_config.items():
                tasks.append(self.__get_candle_data(count, timeframe, session))
                
            # 모든 요청 동시 처리
            results = await asyncio.gather(*tasks)
            
            # 결과 처리 및 CandleChart에 설정
            for i, timeframe in enumerate(timeframe_config.keys()):
                candles = results[i]
                candle_chart.set_candles(timeframe, candles)
                
            # 현재 가격 설정 (가장 작은 시간대의 마지막 캔들 종가 사용)
            smallest_timeframe = min(timeframe_config.keys(), 
                                    key=lambda x: self.__get_timeframe_unit(x))
            if results[list(timeframe_config.keys()).index(smallest_timeframe)]:
                candle_chart.set_current_price(
                    results[list(timeframe_config.keys()).index(smallest_timeframe)][0]['trade_price']
                )
                
        return candle_chart