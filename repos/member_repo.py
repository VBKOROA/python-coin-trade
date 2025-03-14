from sqlalchemy.orm import scoped_session

from models.db.member import Member

class MemberRepo:
    def set_session(self, session: scoped_session):
        self.__session = session
        
    def get_member_by_id(self, member_id: int) -> (Member | None):
        return self.__session.query(Member).filter(Member.id == member_id).first()