import asyncio
from clients.upbit_client import UpbitClient
from dtos.decision import Decision
from repos.member_repo import MemberRepo
from services.action_service import ActionService
from services.llm_service import LLMService
from services.trade_service import TradeService
from settings.db_connection import DBMS
from settings.singleton_pack import SingletonPack as sgtPack

async def test_candle_and_gemini(upbit_client: UpbitClient, llm_service: LLMService):
    """
    캔들 데이터를 가져와 LLM에게 거래 결정을 요청하는 테스트 함수.
    """
    # 먼저 캔들 차트를 가져온다.
    # 예: 5분봉 25개 캔들
    candle_chart = await upbit_client.fetch_candle_chart({"15m": 25, "5m": 25, "4h": 25})

    if not candle_chart or not candle_chart.get_candles("15m"):
        print("캔들 데이터를 가져오는데 실패했습니다.")
        return

    print("가져온 캔들 차트:", candle_chart)

    # AI한테 결정을 요청한다.
    decision = await llm_service.execute_trade_decision(candle_chart)

    print("결정:", decision)
    
def buy_and_sell_test(action_service: ActionService, member_repo: MemberRepo, dbms: DBMS):
    with dbms.get_session() as session:
        try:
            # 테스트 멤버 가져오기
            member = member_repo.get_member_by_id(1, session)
            if not member:
                print("테스트 멤버(ID 1)를 찾을 수 없습니다. DB를 초기화하거나 멤버를 추가하세요.")
                return

            initial_balance = member.balance
            print(f"초기 잔액: {initial_balance}")

            # 코인이 없을 때 hold 결정 테스트 (코인 구매)
            hold_decision = Decision({"action": "hold", "reason": "Test hold when no coin"})
            buy_price = 10000  # 가상 구매 가격
            market = s_pack.MARKET
            hold_decision.set_current_price(buy_price)
            hold_decision.set_market(market)

            print(f"'hold' 결정 (코인 없음): {hold_decision}")
            action_service.buy_coin(member, hold_decision, session)
            session.flush() # DB에 변경사항 반영 (commit 전)

            print(f"'hold' 후 잔액: {member.balance}")
            print(f"'hold' 후 코인 보유 정보: {member.coin}")

            # 코인이 있을 때 release 결정 테스트 (코인 판매)
            if member.coin:
                release_decision = Decision({"action": "release", "reason": "Test release when having coin"})
                sell_price = 11000 # 가상 판매 가격
                release_decision.set_current_price(sell_price)
                release_decision.set_market(market)

                print(f"'release' 결정 (코인 있음): {release_decision}")
                action_service.sell_coin(member.coin, release_decision, session)
                session.flush() # DB에 변경사항 반영 (commit 전)

                print(f"'release' 후 잔액: {member.balance}")
                print(f"'release' 후 코인 보유 정보: {member.coin}")
            else:
                print("판매할 코인이 없습니다.")

            print("테스트 완료. DB 변경사항은 커밋되지 않고 롤백됩니다.")

        finally:
            # 테스트 변경사항을 DB에 반영하지 않고 롤백
            session.rollback()
            print("DB 변경사항이 롤백되었습니다.")
        
async def test_trade_logic(trade_service: TradeService):
    await trade_service.execute_trade_logic(1)
    
async def fetch_5m_200_candle(upbit_client: UpbitClient):
    candle_chart = await upbit_client.fetch_candle_chart({"5m": 200})
    print("5분 캔들 차트:", candle_chart)
    
if __name__ == "__main__":
    s_pack = sgtPack()
    try:
        # asyncio.run(test_trade_logic(s_pack.trade_service))
        # buy_and_sell_test(s_pack.action_service, s_pack.member_repo, s_pack.dbms)
        asyncio.run(test_candle_and_gemini(s_pack.upbit_client, s_pack.llm_service))
        # Clear and recreate all tables after tests
        print("Clearing and recreating all database tables...")
        s_pack.dbms.setup(drop=True)
        print("Database tables cleared and recreated.")
    except KeyboardInterrupt:
        print("프로그램이 종료되었습니다.")
    finally:
        # DB 연결 종료
        if s_pack.dbms:
            s_pack.dbms.close_all()