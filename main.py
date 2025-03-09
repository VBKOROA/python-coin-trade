# install requests
# python -m pip install requests
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
            await trade_service.execute_trade_logic()
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        # 싱글톤팩 인스턴스 생성
        sgtPack = SingletonPack()  
        asyncio.run(main(sgtPack.trade_service))
    except KeyboardInterrupt:
        print("프로그램이 종료되었습니다.")
    finally:
        # DB 연결 종료
        if sgtPack.dbms.conn:
            sgtPack.dbms.conn.close()

# 15(20) & 5(50) 테스트 요망