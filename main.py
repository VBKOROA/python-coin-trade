import asyncio
import datetime

from services.trade_service import TradeService
from settings.singleton_pack import SingletonPack

async def main(trade_service: TradeService):
    while(True):
        # 현재 초가 0초고
        # 15분으로 나누어 떨어질때 작동
        # 아니면 continue
        now = datetime.datetime.now()
        if now.second == 0 and now.minute % 15 == 0:
            await trade_service.execute_trade_logic(1)
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    # 싱글톤팩 인스턴스 생성
    s_pack = SingletonPack()

    # 시작 화면 출력
    print("*****************************************")
    print("*                                       *")
    print("*        🚀 Coin Trading Bot 🚀         *")
    print("*                                       *")
    print("*****************************************")
    print("\nInitializing with the following settings:\n")

    # 설정값 출력
    print("================ Settings ================")
    print(f"  LLM Model: {s_pack.LLM_MODEL}")
    print(f"  Market: {s_pack.MARKET}")
    print(f"  DCA Percentage: {s_pack.DCA * 100}%")
    print(f"  Timeframe Config: {s_pack.TIMEFRAME_CONFIG}")
    print(f"  Debug Mode: {'Enabled' if s_pack.DEBUG else 'Disabled'}")
    print("==========================================")
    print("\nStarting bot...\n")

    try:    
        asyncio.run(main(s_pack.trade_service))
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    finally:
        # DB 연결 종료
        if s_pack.dbms:
            s_pack.dbms.close_all()