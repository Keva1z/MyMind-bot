from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.config import config
import logging

from database.methods.get import get_user
from database.methods.update import update_user
from database.models import Role, Task
from bot.states.base import CreateTask

from bot.keyboards.inline import task_list_keyboard, task_keyboard

logger = logging.getLogger(__name__)

router = Router(name="tasks")

@router.message(Command('tasks'))
async def tasks(message: Message, state: FSMContext):
    """Handle /tasks command"""

    user = await get_user.by_userid(message.from_user.id)
    await message.answer("Ваши задачи:", reply_markup=task_list_keyboard(user.tasks))

@router.callback_query(F.data == "tasks:SKIP")
async def skip(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

@router.callback_query(F.data == "tasks:add")
async def add_task(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Введите название задачи в одно слово.\nНе больше 12 символов.",
        reply_markup = None
    )
    await state.set_state(CreateTask.NAME)

@router.message(CreateTask.NAME)
async def add_task_name(message: Message, state: FSMContext):
    try:
        if len(message.text.split()) in [1,0] and len(message.text) <= 12:
            await state.update_data(name=message.text)
            await message.answer(f"Введите описание задачи '{message.text}'")
            await state.set_state(CreateTask.DESCRIPTION)
        else:
            await message.answer(
            "Введите название задачи в одно слово.\nНе больше 12 символов.",
            reply_markup = None
        )
    except:
        await message.answer(
            "Введите название задачи в одно слово.\nНе больше 12 символов.",
            reply_markup = None
        )
        
@router.message(CreateTask.DESCRIPTION)
async def add_task_description(message: Message, state: FSMContext):
    try:
        data = await state.get_data()
        name = data.get('name')

        task = Task(name, message.text)
        user = await update_user.add_task(message.from_user.id, task)

        await message.answer("Ваши задачи:", reply_markup=task_list_keyboard(user.tasks))
        await state.clear()
    except:
        data = await state.get_data()
        name = data.get('name')
        await message.answer(f"Введите описание задачи '{name}'")


@router.callback_query(F.data.startswith("tasks:"))
async def view_task(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split(':')[-1])
    user = await get_user.by_userid(callback.from_user.id)

    if len(user.tasks)-1 < id:
        await callback.answer("Задача не найдена")
        await callback.message.edit_text("Ваши задачи:", reply_markup=task_list_keyboard(user.tasks))
        return
    task = user.tasks[id]
    task_text = f"""ℹ️ <b>{task.name}</b> - {'✅' if task.is_completed else '❌'}

<i>{task.description}</i>"""

    await callback.message.edit_text(task_text, reply_markup=task_keyboard(task, id), parse_mode='HTML')

@router.callback_query(F.data == "task:back")
async def back_task(callback: CallbackQuery, state: FSMContext):

    user = await get_user.by_userid(callback.from_user.id)
    await callback.message.edit_text("Ваши задачи:", reply_markup=task_list_keyboard(user.tasks))

@router.callback_query(F.data.startswith("task:status"))
async def task_status(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split(':')[-1])
    user = await get_user.by_userid(callback.from_user.id)
    user.tasks[id].change_status()
    user = await update_user.add_task(user.userid, user.tasks[id])

    task = user.tasks[id]

    task_text = f"""ℹ️ <b>{task.name}</b> - {'✅' if task.is_completed else '❌'}

<i>{task.description}</i>"""

    await callback.message.edit_text(task_text, reply_markup=task_keyboard(task, id), parse_mode='HTML')

@router.callback_query(F.data.startswith("task:delete"))
async def task_delete(callback: CallbackQuery, state: FSMContext):
    id = int(callback.data.split(':')[-1])
    user = await get_user.by_userid(callback.from_user.id)
    user = await update_user.remove_task(user.userid, user.tasks[id].name)

    await callback.message.edit_text("Ваши задачи:", reply_markup=task_list_keyboard(user.tasks))