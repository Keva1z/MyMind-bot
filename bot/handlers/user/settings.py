from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from database.methods.get import get_user
from database.methods.update import update_user, update_settings
from database.models import User

from bot.keyboards.inline import settings_keyboard
from bot.states.base import SettingsLink

logger = logging.getLogger(__name__)

router = Router(name="settings")

@router.message(Command('settings'))
async def settings(message: Message, state: FSMContext):
    """Handle /settings command"""
    user = await get_user.by_userid(message.from_user.id)

    # await message.answer("ВРЕМЕННО ОТКЛЮЧЕН")
    # return

    text = f"""⚙️ <b>НАСТРОЙКИ</b>
    
🔗 Заметки: {f'<code>{user.settings.notes_link}</code>' if user.settings.notes_link else '<code>Ссылки нет</code>'}
☀️ Формат даты: {f'<code>{user.settings.time_format}</code>' if user.settings.time_format is not None else '<code>Не установлен</code>'}"""

    await message.answer(text=text, reply_markup=settings_keyboard(), parse_mode='HTML')

@router.callback_query(F.data == "settings:link")
async def settings_link_handle(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Отправьте ссылку на заметку.\nВместо даты напишите <b>{date}</b>\n\nЧтобы удалить ссылку напишите <code>.</code>", reply_markup=None, parse_mode='HTML')
    await state.set_state(SettingsLink.LINK)

@router.message(SettingsLink.LINK)
async def settings_link(message: Message, state: FSMContext):
    try:    
        if message.text.strip() == '.':
            await state.clear()
            await update_settings.notes_link(message.from_user.id, None, None)
            await settings(message, state)
            return
        
        if '{date}' not in message.text.strip():
            await message.answer("Отправьте ссылку на заметку.\nВместо даты напишите <b>{date}</b>\n\nЧтобы удалить ссылку напишите <code>.</code>", reply_markup=None, parse_mode='HTML')
            return
        
        
        await state.update_data(link=message.text)
        await state.set_state(SettingsLink.TIME)

        await message.answer("Теперь введите формат даты.\nДолжны задействоваться <code>DD</code>, <code>MM</code>, <code>YY</code>/<code>YYYY</code>\n\nЧтобы удалить ссылку напишите <code>.</code>", parse_mode='HTML')
        
    except:
        await message.answer("Отправьте ссылку на заметку.\nВместо даты напишите <b>{date}</b>\n\nЧтобы удалить ссылку напишите <code>.</code>", reply_markup=None, parse_mode='HTML')

@router.message(SettingsLink.TIME)
async def settings_link(message: Message, state: FSMContext):
    try:    
        if message.text.strip() == '.':
            await state.clear()
            await update_settings.notes_link(message.from_user.id, None, None)
            await settings(message, state)
            return
        
        if any(t_format not in message.text for t_format in ['DD', 'MM']):
            await message.answer("Отправьте ссылку на заметку.\nВместо даты напишите <b>{date}</b>\n\nЧтобы удалить ссылку напишите <code>.</code>", reply_markup=None, parse_mode='HTML')
            return
        
        if 'YY' not in message.text:
            await message.answer("Отправьте ссылку на заметку.\nВместо даты напишите <b>{date}</b>\n\nЧтобы удалить ссылку напишите <code>.</code>", reply_markup=None, parse_mode='HTML')
            return
        
        data = await state.get_data()
        link = data.get("link")
        time = message.text
        time = time.replace("DD", "%d").replace("MM", "%m").replace("YYYY", "%Y").replace("YY", "%Y")

        await update_settings.notes_link(message.from_user.id, link, time)
        await state.clear()

        await settings(message, state)
    except:
        await message.answer("Теперь введите формат даты.\nДолжны задействоваться <code>DD</code>, <code>MM</code>, <code>YY</code>/<code>YYYY</code>\n\nЧтобы удалить ссылку напишите <code>.</code>", parse_mode='HTML')
