import asyncio
import aiohttp

from datetime import datetime, timedelta
from models.candle_chart import CandleChart

class UpbitClient:
    def __init__(self, market: str):
        self.__MARKET = market
        
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
        timeframe_units = {
            '15m': 15,
            '1h': 60,
        }
        unit = timeframe_units.get(timeframe)
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
        
        if timeframe == '15m':
            # 15분 단위로 시간 맞추기
            now = now - timedelta(minutes=now.minute % 15, seconds=now.second, microseconds=now.microsecond)
        elif timeframe == '1h':
            # 1시간 단위로 시간 맞추기
            now = now - timedelta(minutes=now.minute % 60, seconds=now.second, microseconds=now.microsecond)
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
        latest_candle = data[0]
        latest_candle_time = datetime.fromisoformat(latest_candle['candle_date_time_kst'])
        
        if latest_candle_time >= completed_time:
            # 완료되지 않은 최신 캔들 제거
            data.pop(0)
        else:
            # 완료된 최고 캔들 제거
            data.pop(-1)
        
        # 과거 순으로 정렬하여 반환
        return data[::-1]
        
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
    
    async def fetch_candle_chart(self) -> CandleChart:
        """
        주어진 시장에 대한 캔들 차트를 비동기적으로 가져옵니다.
        Args:
            market (str): 시장 코드 (예: 'KRW-BTC').
        Returns:
            CandleChart: 15분 및 1시간 캔들 데이터와 현재 가격이 설정된 CandleChart 객체.
        """
        candle_chart = CandleChart()
        candle_chart.set_market(self.__MARKET)
        async with aiohttp.ClientSession() as session:
            candles_15m, candles_1h = await asyncio.gather(
                self.__get_candle_data(5, '15m', session),
                self.__get_candle_data(5, '1h', session)
            )
            candle_chart.set_candles_1h(candles_1h)
            candle_chart.set_candles_15m(candles_15m)
            candle_chart.set_current_price(candles_15m[-1]['trade_price'])
        return candle_chart