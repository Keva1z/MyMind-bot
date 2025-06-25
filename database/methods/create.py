from database.models import User, UserSettings, UserInfo
from database.main import async_session
from database.methods.get import get_user, get_settings

class create_user:
    @staticmethod
    async def new(userid: int, username: str) -> User: # Создает нового пользователя
        async with async_session() as session:
            user = await get_user.by_userid(userid)

            if not user:
                user = User(userid=userid, username=username)
                settings = UserSettings(userid=userid)
                info = UserInfo(userid=userid)
                session.add(user)
                session.add(settings)
                session.add(info)
                await session.commit()
                await session.refresh(user)
                
            return user
        
class create_settings:
    @staticmethod
    async def new(userid: int) -> UserSettings: # Создает нового пользователя
        async with async_session() as session:
            settings = await get_settings.by_userid(userid)

            if not settings:
                settings = UserSettings(userid=userid)
                session.add(settings)
                await session.commit()
                await session.refresh(settings)
                
            return settings
