from settings.singleton_pack import SingletonPack as sgtPack
    
if __name__ == "__main__":
    try:
        s_pack = sgtPack()
    except KeyboardInterrupt:
        print("프로그램이 종료되었습니다.")
    finally:
        # DB 연결 종료
        if s_pack.dbms.conn:
            s_pack.dbms.conn.close()