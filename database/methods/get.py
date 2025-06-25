from database.models import User, Role, UserSettings, UserInfo
from database.main import async_session
from sqlalchemy import select
from sqlalchemy.orm import joinedload

class get_user:
    @staticmethod
    async def by_userid(userid: int) -> User|None:
        async with async_session() as session:
            return (await session.execute(
                select(User).options(joinedload(User.settings), joinedload(User.info)).where(User.userid == userid)
            )).scalar_one_or_none()
        
    @staticmethod
    async def by_username(username: str) -> User|None:
        async with async_session() as session:
            return (await session.execute(
                select(User).options(joinedload(User.settings), joinedload(User.info)).where(User.username == username)
            )).scalar_one_or_none()

    @staticmethod
    async def all(role: list[Role]|Role|None = None) -> list[User]:
        async with async_session() as session:
            if role:
                if isinstance(role, Role):
                    role = [role]
                return (await session.execute(
                    select(User).options(joinedload(User.settings), joinedload(User.info)).where(User.role.in_(role))
                )).scalars().all()
            return (await session.execute(
                select(User).options(joinedload(User.settings), joinedload(User.info))
            )).scalars().all()
        
class get_settings:
    @staticmethod
    async def by_userid(userid: int) -> UserSettings|None:
        async with async_session() as session:
            return (await session.execute(select(UserSettings).where(UserSettings.userid == userid))).scalar_one_or_none()
        
class get_info:
    @staticmethod
    async def by_userid(userid: int) -> UserInfo|None:
        async with async_session() as session:
            return (await session.execute(select(UserInfo).where(UserInfo.userid == userid))).scalar_one_or_none()