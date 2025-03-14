from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

class DBMS:
    def __init__(self, host, port, user, password, name):
        # SQLAlchemy 엔진 생성
        connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
        self.__engine = create_engine(connection_string, echo=False)
        
        # 세션 팩토리 생성
        self.session_factory = sessionmaker(bind=self.__engine)
        self.Session = scoped_session(self.session_factory)
    
    @contextmanager
    def get_session(self):
        """세션을 제공하고 완료 시 자동으로 닫는 컨텍스트 매니저"""
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def setup(self):
        """
        데이터베이스 스키마를 초기화합니다.
        이 메서드는 기존의 모든 테이블을 삭제하고 Base 메타데이터를 기반으로 새 테이블을 생성합니다.
        """
        Base.metadata.drop_all(self.__engine)
        Base.metadata.create_all(self.__engine)
    
    def close_all(self):
        self.Session.remove()
