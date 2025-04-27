import asyncio
import datetime
import traceback

from services.trade_service import TradeService
from settings.singleton_pack import SingletonPack

async def main(trade_service: TradeService, s_pack: SingletonPack):
    try:
        # 가장 작은 시간 간격(분) 가져오기
        smallest_interval_minutes = s_pack.get_smallest_timeframe_minutes()
        print(f"Detected smallest timeframe interval: {smallest_interval_minutes} minutes.")
        print(f"Trade logic will run every {smallest_interval_minutes} minutes at the start of the minute.")
    except ValueError as e:
        print(f"Error initializing main loop: {e}")
        return # 오류 발생 시 종료

    while(True):
        now = datetime.datetime.now()
        # 현재 초가 0이고, 현재 분이 가장 작은 시간 간격으로 나누어 떨어질 때 실행
        if now.second == 0 and now.minute % smallest_interval_minutes == 0:
            print(f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] Running trade logic...")
            try:
                # execute_trade_logic 호출 (user_id는 예시로 1을 사용)
                await trade_service.execute_trade_logic(1)
            except Exception as e:
                # 실행 중 오류 발생 시 로그 출력 후 계속 진행
                print(f"Error during trade logic execution: {e}")
                traceback.print_exc()
        
        # 다음 초까지 대기 (CPU 사용량 감소)
        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        # 싱글톤팩 인스턴스 생성 (여기서 환경변수 로드 및 초기화 진행)
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
        print(f"  DCA Percentage: {s_pack.DCA * 100:.2f}%") # 소수점 표시 개선
        print(f"  Timeframe Config: {s_pack.TIMEFRAME_CONFIG}")
        print(f"  Debug Mode: {'Enabled' if s_pack.DEBUG else 'Disabled'}")
        print("==========================================")
        print("\nStarting bot...\n")

        # main 함수에 trade_service와 s_pack 인스턴스 전달
        asyncio.run(main(s_pack.trade_service, s_pack))

    except ValueError as e:
        # SingletonPack 초기화 중 발생한 오류 처리
        print(f"Initialization failed: {e}")
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        # 예상치 못한 다른 오류 처리
        print(f"An unexpected error occurred: {e}")
        traceback.print_exc()
    finally:
        # 프로그램 종료 시 정리 작업
        # s_pack 인스턴스가 성공적으로 생성되었는지 확인 후 DB 연결 종료 시도
        if 's_pack' in locals() and hasattr(s_pack, 'dbms') and s_pack.dbms:
            print("Closing database connection...")
            s_pack.dbms.close_all()
            print("Database connection closed.")
        print("Bot stopped.")