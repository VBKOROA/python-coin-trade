import asyncio
from services.trade_service import TradeService
from settings.singleton_pack import SingletonPack as sgtPack

async def main(trade_service: TradeService):
    await trade_service.execute_trade_logic()
    
if __name__ == "__main__":
    try:
        s_pack = sgtPack()
        asyncio.run(main(s_pack.trade_service))
    except KeyboardInterrupt:
        print("프로그램이 종료되었습니다.")
    finally:
        # DB 연결 종료
        if s_pack.dbms.conn:
            s_pack.dbms.conn.close()