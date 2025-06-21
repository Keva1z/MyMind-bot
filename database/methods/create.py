from database.models import User
from database.main import async_session
from database.methods.get import get_user

class create_user:
    @staticmethod
    async def new(userid: int, username: str) -> User: # Создает нового пользователя
        async with async_session() as session:
            user = await get_user.by_userid(userid)

            if not user:
                user = User(userid=userid, username=username)
                session.add(user)
                await session.commit()
                await session.refresh(user)
                
            return user