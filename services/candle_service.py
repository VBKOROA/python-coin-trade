import json

class CandleService:
    def candle_to_json(self, candles: list) -> str:
        converted_list = []
        for candle in candles:
            converted_list.append(self.__candle_to_json(candle))
        ret = json.dumps(converted_list)
        return ret
    
    def __candle_to_json(self, candle: dict) -> dict:
        converted = {
            'time': candle['candle_date_time_kst'], # 시간
            'open': candle['opening_price'], # 시가
            'close': candle['trade_price'], # 종가
            'high': candle['high_price'], # 고가
            'low': candle['low_price'], # 저가
            'volume': candle['candle_acc_trade_volume'], # 거래량
        }
        return converted