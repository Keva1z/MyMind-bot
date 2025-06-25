from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from database.methods.get import get_user
from database.methods.update import update_user, update_settings, update_userinfo
from database.models import User

from bot.keyboards.inline import personal_keyboard, personal_none_keyboard
from bot.states.base import PersonalChange

logger = logging.getLogger(__name__)

router = Router(name="personal")

personal_data = {
    'name' : ['Имя', str, update_userinfo.name],
    'age' : ['Возраст', int, update_userinfo.age],
    'job' : ['Работа', str, update_userinfo.job],
    'dream' : ['Мечта', str, update_userinfo.dream],
    'city' : ['Город', str, update_userinfo.city],
    'personality' : ['Характер', str, update_userinfo.personality],
    'hobby' : ['Хобби', str, update_userinfo.hobby],
    'wishes' : ['Пожелания', str, update_userinfo.wishes],
}

@router.message(Command('personal'))
async def personal(message: Message, state: FSMContext, username: str|None = None, edit: bool = False, user: User|None = None):
    """Handle /personal command"""

    if user is None:
        user = await get_user.by_userid(message.from_user.id)
    if username is None: username = message.from_user.username
    text = f"""👤 <b>ВАШИ ДАННЫЕ:</b>

ЮЗ: <code>{username}</code>
Имя: <code>{user.info.name}</code>
Возраст: <code>{user.info.age}</code>
Город: <code>{user.info.city}</code>
Работа: <code>{user.info.job}</code>
Хобби: <code>{user.info.hobby}</code>
Мечта: <code>{user.info.dream}</code>
Характер: <code>{user.info.personality}</code>
Пожелания в ответах ИИ:
<code>{user.info.wishes}</code>"""

    if edit:
        await message.edit_text(
            text = text,
            reply_markup=personal_keyboard(personal_data),
            parse_mode='HTML'
        )
    else:
        await message.answer(
            text = text,
            reply_markup=personal_keyboard(personal_data),
            parse_mode='HTML'
        )

@router.callback_query(F.data == 'personal:none')
async def handle_none(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    key = data.get('key')

    user = await get_user.by_userid(callback.from_user.id)
    await personal_data[key][2](callback.from_user.id, None)

    await state.clear()
    await personal(callback.message, state, callback.from_user.username, True, user)

@router.callback_query(F.data.startswith('personal:'))
async def handle_change(callback: CallbackQuery, state: FSMContext):

    key = callback.data.split(':')[-1]

    await state.set_state(PersonalChange.CHANGE)

    action_msg = await callback.message.edit_text(
        text = f'Введите значение для `{personal_data[key][0]}`',
        parse_mode='MarkdownV2',
        reply_markup=personal_none_keyboard()
    )

    await state.update_data(key = key, action_msg = action_msg)

@router.message(PersonalChange.CHANGE)
async def handle_change_final(message: Message, state: FSMContext):
    data = await state.get_data()
    key = data.get('key')
    action_msg: Message = data.get('action_msg')
    user = await get_user.by_userid(message.from_user.id)

    object: str = message.text

    if personal_data[key][1] is int:
        try:
            object: int = int(message.text)
        except:
            action_msg = await action_msg.edit_text(
                text = f'Введите значение для `{personal_data[key][0]}`, оно должно быть числом\!',
                parse_mode='MarkdownV2',
                reply_markup=personal_none_keyboard()
            )
            await state.update_data(key = key, action_msg = action_msg)
            return
    

    await action_msg.delete()
    await personal_data[key][2](user.userid, object)
    await state.clear()
    await personal(message, state)

