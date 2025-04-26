from sqlalchemy.orm import scoped_session

from tables.member import Member

class MemberRepo:
    def get_member_by_id(self, member_id: int, session: scoped_session) -> (Member | None):
        return session.query(Member).filter(Member.id == member_id).first()