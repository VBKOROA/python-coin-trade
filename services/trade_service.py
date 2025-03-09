from api.upbit_client import UpbitClient
from repos.coin_repo import CoinRepo
from repos.info_repo import InfoRepo
from services.action_service import ActionService
from pymysql.connections import Connection

class TradeService:
    def set_upbit_client(self, upbit_client: UpbitClient):
        self.__upbit_client = upbit_client
        
    def set_coin_repo(self, coin_repo: CoinRepo):
        self.__coin_repo = coin_repo
    
    def set_action_service(self, action_service: ActionService):
        self.__action_service = action_service
        
    def set_info_repo(self, info_repo: InfoRepo):
        self.__info_repo = info_repo
        
    def set_conn(self, conn: Connection):
        self.__conn = conn
        
    async def execute_trade_logic(self):
        # 먼저 캔들 차트를 가져온다.
        candle_chart = await self.__upbit_client.fetch_candle_chart()
        
        # 현재 팔아야 할 코인을 전부 조회한다.
        coins_should_sell = self.__coin_repo.get_coins_should_sell(candle_chart.current_price)
        
        # 만약 팔아야 할 코인이 있다면 판다.
        if coins_should_sell:
            for coin in coins_should_sell:
                self.__action_service.sell_coin(coin, candle_chart.current_price)
            self.__conn.commit()
        
        # AI한테 결정을 요청한다.
        decision = await self.__action_service.execute_trade_decision(candle_chart)
        
        # 만약 구매라면
        if(decision.action == 'buy'):
            balance = self.__info_repo.get_balance(1)
            self.__action_service.buy_coin(decision, balance)
            self.__conn.commit()