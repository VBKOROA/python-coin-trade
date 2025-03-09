import asyncio
from decimal import Decimal
from repos.action_log_repo import ActionLogRepo
from services.trade_service import TradeService
from settings.singleton_pack import SingletonPack as sgtPack

def buy_coin_test(action_log_repo: ActionLogRepo):
    # 테스트용 데이터
    market = 'KRW-BTC'
    current_price = 50000000
    price = Decimal(1000000)
        
    # 매수 메소드 호출
    amount = action_log_repo.buy_coin(market, current_price, price)
    
    # 결과 출력
    print(f"Market: {market}, Amount: {amount}, Price: {price}")

async def __execute_trade_logic_test(trade_service: TradeService):
    await trade_service.execute_trade_logic()
    
def execute_trade_logic_test(trade_service: TradeService):
    asyncio.run(__execute_trade_logic_test(trade_service))
    
if __name__ == "__main__":
    try:
        s_pack = sgtPack()
        execute_trade_logic_test(s_pack.trade_service)
    except KeyboardInterrupt:
        print("프로그램이 종료되었습니다.")
    finally:
        # DB 연결 종료
        if s_pack.dbms.conn:
            s_pack.dbms.conn.close()