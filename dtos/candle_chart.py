import json

class CandleChart:
    def __init__(self):
        self.candles = {}  # 시간대별 캔들 데이터를 저장하는 딕셔너리
        self.current_price: int = None
        self.market: str = None
        
    def set_candles(self, timeframe, candles):
        """
        특정 시간대의 캔들 데이터를 설정합니다.
        
        Args:
            timeframe (str): 캔들 시간대 (예: '15m', '1h', '4h', '1d')
            candles (list): 캔들 데이터 리스트
        """
        self.candles[timeframe] = candles
        
    def get_candles(self, timeframe):
        """
        특정 시간대의 캔들 데이터를 가져옵니다.
        
        Args:
            timeframe (str): 캔들 시간대 (예: '15m', '1h', '4h', '1d')
            
        Returns:
            list: 해당 시간대의 캔들 데이터 리스트, 없으면 None
        """
        return self.candles.get(timeframe)
    
    def get_all_timeframes(self):
        """
        현재 설정된 모든 시간대를 반환합니다.
        
        Returns:
            list: 설정된 시간대 리스트
        """
        return list(self.candles.keys())
        
    def set_current_price(self, price: int):
        self.current_price = price
        
    def set_market(self, market):
        self.market = market
        
    def __str__(self):
        """json 형태로 출력"""
        return json.dumps({
            "candles": self.candles,
            "current_price": self.current_price,
            "market": self.market
        }, indent=4, ensure_ascii=False)