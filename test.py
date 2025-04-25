import asyncio
from api.upbit_client import UpbitClient
from models.dto.decision import Decision
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
    candle_chart = await upbit_client.fetch_candle_chart({"5m": 25})

    if not candle_chart or not candle_chart.get_candles("5m"):
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

            # 구매 테스트
            buy_decision = Decision({"action": "buy", "reason": "Test buy"})
            buy_price = 10000  # 가상 구매 가격
            market = s_pack.MARKET
            buy_decision.set_current_price(buy_price)
            buy_decision.set_market(market)

            print(f"구매 결정: {buy_decision}")
            action_service.buy_coin(member, buy_decision, session)
            session.flush() # DB에 변경사항 반영 (commit 전)

            print(f"구매 후 잔액: {member.balance}")
            print(f"구매 후 코인 보유 정보: {member.coin}")

            # 판매 테스트 (코인을 보유하고 있을 경우)
            # 참고: member 객체는 메모리에서 업데이트될 수 있지만, DB 변경사항은 아직 커밋되지 않았습니다.
            # 실제와 같은 테스트를 위해서는 다시 가져오거나 메모리 내 상태를 신중하게 처리해야 할 수 있습니다.
            # 여기서는 메모리 내 member 객체가 구매 후 상태를 반영한다고 가정합니다.
            if member.coin:
                sell_decision = Decision({"action": "sell", "reason": "Test sell"})
                sell_price = 11000 # 가상 판매 가격
                sell_decision.set_current_price(sell_price)
                sell_decision.set_market(market)

                print(f"판매 결정: {sell_decision}")
                action_service.sell_coin(member.coin, sell_decision, session)
                session.flush() # DB에 변경사항 반영 (commit 전)

                print(f"판매 후 잔액: {member.balance}")
                print(f"판매 후 코인 보유 정보: {member.coin}")
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
        asyncio.run(test_trade_logic(s_pack.trade_service))
        # buy_and_sell_test(s_pack.action_service, s_pack.member_repo, s_pack.dbms)
    except KeyboardInterrupt:
        print("프로그램이 종료되었습니다.")
    finally:
        # DB 연결 종료
        if s_pack.dbms:
            s_pack.dbms.close_all()