from database.models import User, Role, UserSettings, Task
from database.methods.get import get_user, get_settings
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
        
    @staticmethod
    async def journal(userid: int, journal: str) -> User | None:
        async with async_session() as session:
            user = await get_user.by_userid(userid)

            if not user:
                return None

            user.journal = journal
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user
        
    @staticmethod
    async def add_task(userid: int, task: Task) -> User | None:
        """Add a task to the user's task list."""
        async with async_session() as session:
            user = await get_user.by_userid(userid)
            if not user:
                return None
            
            id = -1
            for ex_task in user.tasks:
                if ex_task.name.lower() == task.name.lower():
                    id = user.tasks.index(ex_task)
            if id != -1: user.tasks[id] = task
            else: user.tasks.append(task)

            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    @staticmethod
    async def remove_task(userid: int, task_name: str) -> User | None:
        """Remove a task by name from the user's task list."""
        async with async_session() as session:
            user = await get_user.by_userid(userid)
            if not user:
                return None
            if not user.tasks: return user
            task_name = task_name.lower()
            user.tasks = [task for task in user.tasks if task.name.lower() != task_name]
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

class update_settings:
    @staticmethod
    async def notes_link(userid: int, link: str) -> UserSettings | None:
        async with async_session() as session:
            settings = await get_settings.by_userid(userid)

            if not settings:
                return None

            settings.notes_link = link
            session.add(settings)
            await session.commit()
            await session.refresh(settings)
            return settings