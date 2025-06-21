from database.models import User, Role
from database.methods.get import get_user
from database.main import async_session

class update_user:
    @staticmethod
    async def username(userid: int, username: str) -> User | None:
        async with async_session() as session:
            user = await get_user.by_userid(userid)

            if not user:
                return None

            user.username = username
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        
    @staticmethod
    async def role(userid: int, role: Role) -> User | None:
        async with async_session() as session:
            user = await get_user.by_userid(userid)

            if not user:
                return None

            user.role = role
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user