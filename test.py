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
    # 먼저 캔들 차트를 가져온다.
    candle_chart = await upbit_client.fetch_candle_chart({"5m": 25})
    
    # AI한테 결정을 요청한다.
    decision = await llm_service.execute_trade_decision(candle_chart)
    
    print("결정:", decision)
    
def buy_and_sell_test(action_service: ActionService, member_repo: MemberRepo, dbms: DBMS):
    with dbms.get_session() as session:
        member = member_repo.get_member_by_id(1, session)
        
        # 코인 구매 테스트
        buy_decision = Decision({
            "up_chance": 100,
            "down_chance": 0,
            "details": ""
        })
        buy_decision.set_current_price(10000)
        buy_decision.set_market("KRW-BTC")
        action_service.buy_coin(member, buy_decision, session)
        session.commit()
        
        # 코인 판매 테스트
        sell_decision = Decision({
            "up_chance": 0,
            "down_chance": 100,
            "details": ""
        })
        sell_decision.set_current_price(10000)
        sell_decision.set_market("KRW-BTC")
        coin = member.coin
        action_service.sell_coin(coin, sell_decision, session)
        session.commit()
        
        print("코인 구매 및 판매 테스트 완료")
        
async def test_trade_logic(trade_service: TradeService):
    await trade_service.execute_trade_logic(1)
    
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