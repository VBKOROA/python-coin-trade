import asyncio
from api.upbit_client import UpbitClient
from services.llm_service import LLMService
from settings.singleton_pack import SingletonPack as sgtPack

async def test_candle_and_gemini(upbit_client: UpbitClient, llm_service: LLMService):
    # 먼저 캔들 차트를 가져온다.
    candle_chart = await upbit_client.fetch_candle_chart({"5m": 25})
    
    # AI한테 결정을 요청한다.
    decision = await llm_service.execute_trade_decision(candle_chart)
    
    print("결정:", decision)
    
if __name__ == "__main__":
    s_pack = sgtPack()
    try:
        asyncio.run(test_candle_and_gemini(s_pack.upbit_client, s_pack.llm_service))
    except KeyboardInterrupt:
        print("프로그램이 종료되었습니다.")
    finally:
        # DB 연결 종료
        if s_pack.dbms:
            s_pack.dbms.close_all()