# install requests
# python -m pip install requests
import asyncio
import datetime

from services.trade_service import TradeService
from settings.singleton_pack import SingletonPack

async def main(trade_service: TradeService):
    while(True):
        # 현재 초가 0초고
        # 5분으로 나누어 떨어질때 작동
        # 아니면 continue
        now = datetime.datetime.now()
        if now.second == 0 and now.minute % 5 == 0:
            await trade_service.execute_trade_logic()
        else:
            await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        # 싱글톤팩 인스턴스 생성
        s_pack = SingletonPack()  
        asyncio.run(main(s_pack.trade_service))
    except KeyboardInterrupt:
        print("프로그램이 종료되었습니다.")
    finally:
        # DB 연결 종료
        if s_pack.dbms:
            s_pack.dbms.close_all()