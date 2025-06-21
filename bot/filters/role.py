from typing import Union
from aiogram.filters import BaseFilter
from aiogram.types import Message, CallbackQuery
from database.models import Role
from database.methods.get import get_user

class RoleFilter(BaseFilter):
    def __init__(self, role: Union[Role, list[Role]]):
        self.role = role if isinstance(role, list) else [role]

    async def __call__(self, event: Union[Message, CallbackQuery]) -> bool:
        """Check if user has required role"""
        user = await get_user.by_userid(event.from_user.id)
            
        if not user:
            return False
                
        return user.role in self.role 