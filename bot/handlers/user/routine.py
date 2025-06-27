from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import logging

from database.methods.get import get_user
from database.methods.update import update_user
from database.models import Task
from bot.states.base import CreateTaskRoutine

from bot.keyboards.inline import task_routine_list_keyboard, task_routine_keyboard

logger = logging.getLogger(__name__)

router = Router(name="routines")

@router.message(Command('routine'))
async def routines(message: Message, state: FSMContext):
    """Handle /routine command"""

    user = await get_user.by_userid(message.from_user.id)
    await message.answer("Ваши рутинные задачи:", reply_markup=task_routine_list_keyboard(user.routine_tasks))

@router.callback_query(F.data == "routines:SKIP")
async def skip_routine(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

@router.callback_query(F.data == "routines:add")
async def add_routine_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите название задачи в одно слово.\nНе больше 20 символов.",
        reply_markup = None
    )
    await state.set_state(CreateTaskRoutine.NAME)

@router.message(CreateTaskRoutine.NAME)
async def add_task_routine_name(message: Message, state: FSMContext):
    try:
        if len(message.text) <= 20:
            await state.update_data(name=message.text)
            await message.answer(f"Введите описание задачи '{message.text}'")
            await state.set_state(CreateTaskRoutine.DESCRIPTION)
        else:
            await message.answer(
            "Введите название задачи в одно слово.\nНе больше 20 символов.",
            reply_markup = None
        )
    except:
        await message.answer(
            "Введите название задачи в одно слово.\nНе больше 20 символов.",
            reply_markup = None
        )
        
@router.message(CreateTaskRoutine.DESCRIPTION)
async def add_task_routine_description(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        name = data.get('name')

        task = Task(name, message.text)
        user = await update_user.add_routine_task(message.from_user.id, task)

        await message.answer("Ваши рутинные задачи:", reply_markup=task_routine_list_keyboard(user.routine_tasks))
        await state.clear()
    except:
        data = await state.get_data()
        name = data.get('name')
        await message.answer(f"Введите описание задачи '{name}'")


@router.callback_query(F.data.startswith("routines:"))
async def view_task_routine(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split(':')[-1])
    user = await get_user.by_userid(callback.from_user.id)

    if len(user.routine_tasks)-1 < id:
        await callback.answer("Задача не найдена")
        await callback.message.edit_text("Ваши рутинные задачи:", reply_markup=task_routine_list_keyboard(user.routine_tasks))
        return
    task = user.routine_tasks[id]
    task_text = f"""ℹ️ <b>{task.name}</b> - {'✅' if task.is_completed else '❌'}

<i>{task.description}</i>"""

    await callback.message.edit_text(task_text, reply_markup=task_routine_keyboard(task, id), parse_mode='HTML')

@router.callback_query(F.data == "routine:back")
async def back_task_routine(callback: CallbackQuery, state: FSMContext):

    user = await get_user.by_userid(callback.from_user.id)
    await callback.message.edit_text("Ваши рутинные задачи:", reply_markup=task_routine_list_keyboard(user.routine_tasks))

@router.callback_query(F.data.startswith("routine:status"))
async def task_routine_status(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split(':')[-1])
    user = await get_user.by_userid(callback.from_user.id)
    user.routine_tasks[id].change_status()
    user = await update_user.add_routine_task(user.userid, user.routine_tasks[id])

    task = user.routine_tasks[id]

    task_text = f"""ℹ️ <b>{task.name}</b> - {'✅' if task.is_completed else '❌'}

<i>{task.description}</i>"""

    await callback.message.edit_text(task_text, reply_markup=task_routine_keyboard(task, id), parse_mode='HTML')

@router.callback_query(F.data.startswith("routine:delete"))
async def task_routine_delete(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split(':')[-1])
    user = await get_user.by_userid(callback.from_user.id)
    user = await update_user.remove_routine_task(user.userid, user.routine_tasks[id].name)

    await callback.message.edit_text("Ваши рутинные задачи:", reply_markup=task_routine_list_keyboard(user.routine_tasks))