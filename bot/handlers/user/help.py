from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.config import config
import logging

from database.methods.get import get_user
from database.models import Role

logger = logging.getLogger(__name__)

router = Router(name="help")

@router.message(Command('help'))
async def help(message: Message, state: FSMContext):
    """Handle /help command"""
    
    user = await get_user.by_userid(message.from_user.id)

    commands = f"""<b>ПОМОЩЬ ПО КОММАНДАМ</b>

/help - Данное меню
/settings - Настройки бота
/personal - Персональная информация
{'\n' if user.role not in [Role.ADMIN, Role.SUPERADMIN] else '/admin - Админ панель\n'}
/review [ЗАПРОС] - Сделать комментарий по поводу сегодняшнего журнала и задач
<i>Если написать что-то после /review то ИИ учтет это, но можно и не добавлять</i>

<b>Журнал</b>
/journal - Выведет весь журнал
Так-же даст 2 кнопки для добавления и удаления записей.
Добавить - Добавить новую запись в журнал
Удалить - Удалит последнюю запись

<b>Задачи</b>
/tasks - Выведет все задачи

<b>Напоминания</b>
/timers - Выведет все напоминания которые вы установили
"""

    await message.answer(text=commands, parse_mode="HTML")