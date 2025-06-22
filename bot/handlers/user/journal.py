from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from datetime import datetime
import logging

from database.methods.get import get_user
from database.methods.update import update_user
from database.models import User

from bot.keyboards.inline import journal_keyboard
from bot.states.base import AddNote

logger = logging.getLogger(__name__)

router = Router(name="journal")

@router.message(Command('journal'))
async def journal(message: Message, state: FSMContext, edit: bool = False, user: User|None = None):
    """Handle /journal command"""

    if user is None:
        user = await get_user.by_userid(message.from_user.id)
    date = datetime.strftime(datetime.now(), "%d.%m.%Y")

    text = f"""<b>Сегодня:</b> <i>{date}</i>

{f'<pre>{user.parsed_journal}</pre>' if user.parsed_journal != '' else 'Журнал пока пуст...'}"""
    
    keyboard = journal_keyboard(user.list_journal != [])
    if edit:
        await message.edit_text(text=text, reply_markup=keyboard, parse_mode='HTML')
    else:
        await message.answer(text=text, reply_markup=keyboard, parse_mode='HTML')


@router.callback_query(F.data == "journal:add")
async def journal_add_handle(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Напишите ваши мысли", reply_markup=None)
    await state.set_state(AddNote.BODY)

@router.message(AddNote.BODY)
async def journal_add_note(message: Message, state: FSMContext):
    try:
        user = await get_user.by_userid(message.from_user.id)
        
        time = datetime.strftime(datetime.now(), "%H:%M")
        text = f"""#### {time}
{message.text.replace("&&&&&&&&&&", "")}"""
        
        divisor = ""
        
        if user.list_journal != []: divisor = "&&&&&&&&&&"
        new_journal = user.parsed_journal + divisor + text

        await update_user.journal(user.userid, new_journal)
        await state.clear()
        await journal(message, state)
    except:
        await message.answer("Напишите свои мысли...")

@router.callback_query(F.data == "journal:delete")
async def journal_delete(callback: CallbackQuery, state: FSMContext):
    user = await get_user.by_userid(callback.from_user.id)

    new_journal = user.delete_last_note()
    user = await update_user.journal(user.userid, new_journal)

    await journal(callback.message, state, edit=True, user=user)


    
