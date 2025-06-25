from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from database.methods.get import get_user
from database.methods.update import update_user
from database.models import User

from service.AI.GPT import generate, prompts


logger = logging.getLogger(__name__)

router = Router(name="review")

@router.message(Command('review'))
async def review(message: Message, state: FSMContext):
    """Handle /review command"""

    text = " ".join(message.text.split(' ')[1::])

    wait_message = await message.answer("Обозреваю твой день...")

    user = await get_user.by_userid(message.from_user.id)

    tasks = "\n".join([f"{i}. {'✅' if task.is_completed else '❌'} {task.name}: {task.description}" for i, task in enumerate(user.tasks)])
    if tasks == '': tasks = 'Задач пока не поставлено...'
    journal = user.parsed_journal if user.parsed_journal != '' else 'Пока в журнале пусто...'
    date = datetime.strftime(datetime.now(), "%d.%m.%Y"),
    time = datetime.strftime(datetime.now(), "%H:%M")
    user_ask = '' if text == '' else f'Доп.Запрос от пользователя: {text}'
    user_info = f"""Телеграмм ЮЗ: @{message.from_user.username}
Имя: {user.info.name}
Возраст: {user.info.age}
Город: {user.info.city}
Работа: {user.info.job}
Хобби: {user.info.hobby}
Мечта: {user.info.dream}
Характер: {user.info.personality}
Пожелания в ответах ИИ:
{user.info.wishes}"""

    prompt = prompts.review.format(
        date = date,
        time = time,
        tasks = tasks,
        journal = journal,
        user_ask = user_ask,
        user_info = user_info
    )

    while True:
        try:
            response = await generate(prompt)
            await wait_message.edit_text(text=response, parse_mode='HTML')
            return
        except:
            pass