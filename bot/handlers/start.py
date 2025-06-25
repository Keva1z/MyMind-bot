from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.config import config
import logging

from bot.filters.role import RoleFilter
from database.models import Role

from database.methods.create import create_user, create_settings
from database.methods.update import update_user

logger = logging.getLogger(__name__)

router = Router(name="start")

@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    logger.info(f"User {message.from_user.id} started bot")
    
    # Create user and settings if not exists
    user = await create_user.new(message.from_user.id, message.from_user.username)

    # Update username if it changed
    if message.from_user.username != user.username:
        await update_user.username(user.userid, message.from_user.username)
    
    if user.userid in config.superadmin_ids and user.role != Role.SUPERADMIN:
        await update_user.role(user.userid, Role.SUPERADMIN)

    await state.clear()

    await message.answer(f"Привет, {user.username}! Я бот - помощник для жизни. напиши /help")