from database.models import User
from database.methods.get import get_user
from database.main import async_session

class delete_user:
    @staticmethod
    async def by_userid(userid: int) -> None:
        async with async_session() as session:
            user = await get_user.by_userid(userid)
            
            if not user:
                return

            await session.delete(user)
            await session.commit()