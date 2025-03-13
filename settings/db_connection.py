from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session

Base = declarative_base()

class DBMS:
    def __init__(self, host, port, user, password, name):
        # SQLAlchemy 엔진 생성
        connection_string = f"mysql+pymysql://{user}:{password}@{host}:{port}/{name}"
        self.engine = create_engine(connection_string, echo=False)
        
        # 세션 팩토리 생성
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
    def get_session(self):
        return self.Session()
    
    def create_all(self):
        """모든 모델 테이블을 생성합니다"""
        Base.metadata.create_all(self.engine)
    
    def close_all(self):
        """모든 세션을 종료합니다"""
        self.Session.remove()
