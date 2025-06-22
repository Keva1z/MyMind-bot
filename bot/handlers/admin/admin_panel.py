from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
import logging

from bot.filters.role import RoleFilter
from database.models import Role, User, Enum, UserSettings, Task

from database.methods.get import get_user
from database.methods.delete import delete_user
from database.methods.update import update_user

from bot.keyboards.inline import admin_panel_keyboard, user_info_keyboard, confirm_keyboard, role_change_keyboard
from bot.states.admin import AdminPanelState
logger = logging.getLogger(__name__)

router = Router(name="admin_panel")
router.message.filter(RoleFilter(role=[Role.SUPERADMIN, Role.ADMIN]))

def get_other_repr(object) -> str:
    if isinstance(object, Enum):
        return f"`{object.value}`"
    if isinstance(object, UserSettings):
        return "\n  - "+"\n  - ".join(f"*{k}:* {get_other_repr(v)}" for k, v in sorted(object.__dict__.items()) if not k.startswith('_'))
    if isinstance(object, list):
        if len(object) == 0: return '`None`'
        if isinstance(object[0], Task):
            object: list[Task] = object
            return "\n  - "+"\n  - ".join(f"{'✅' if task.is_completed else '❌'} {task.name}" for task in object)
    return f"`{object}`"

def get_user_repr(user: User):
    return "\n".join(f"*{k}:* {get_other_repr(v)}" for k, v in sorted(user.__dict__.items()) if not k.startswith('_'))

@router.message(Command("admin"))
async def cmd_panel(message: Message, state: FSMContext):
    """Handle /panel command"""
    logger.info(f"User {message.from_user.id} opened admin panel")
    
    await message.answer("🔑 Админ-панель", reply_markup=admin_panel_keyboard())

@router.callback_query(F.data == "admin:close_menu")
async def close_menu(callback: CallbackQuery, state: FSMContext):
    """Handle admin:close_menu callback"""
    logger.info(f"User {callback.from_user.id} closed admin menu")

    await callback.message.delete()
    await state.clear()

@router.callback_query(F.data == "admin:user_info")
async def get_user_info(callback: CallbackQuery, state: FSMContext):
    """Handle admin:user_info callback"""
    logger.info(f"User {callback.from_user.id} opened user info")
    
    await callback.message.delete()
    await callback.message.answer("Отправьте ID/Username пользователя\n_Для отмены напишите '.'_",
                                  parse_mode="Markdown")

    await state.set_state(AdminPanelState.GET_USER_ID)

@router.message(AdminPanelState.GET_USER_ID)
async def get_user_info_handler(message: Message, state: FSMContext):
    """Handle user info input"""
    logger.info(f"User {message.from_user.id} inputted user info: {message.text}")

    admin = await get_user.by_userid(message.from_user.id)

    if message.text == ".":
        await state.clear()
        await message.answer("⚠️ Отменено")
        await cmd_panel(message, state)
        return
    
    if message.text.isdigit():
        user = await get_user.by_userid(int(message.text))
        if not user:
            await message.answer("⚠️ Пользователь не найден")
            await cmd_panel(message, state)
            return   
    else:
        user = await get_user.by_username(message.text if not message.text.startswith("@") else message.text[1:])
        if not user:
            await message.answer("⚠️ Пользователь не найден")
            await cmd_panel(message, state)
            return
        
    await message.answer(f"ℹ️ Информация о пользователе\n\n{get_user_repr(user)}",
                         parse_mode="Markdown",
                         reply_markup=user_info_keyboard(user.userid, admin.role == Role.SUPERADMIN))
    await state.clear()

@router.callback_query(F.data == "userinfo:back")
async def back_to_admin_panel(callback: CallbackQuery, state: FSMContext):
    """Handle userinfo:back callback"""
    logger.info(f"User {callback.from_user.id} returned to admin panel")

    await callback.message.delete()
    
    await cmd_panel(callback.message, state)

@router.callback_query(F.data.startswith("superadmin:change_role"))
async def change_role_callback(callback: CallbackQuery, state: FSMContext):
    """Handle superadmin:change_role callback"""
    logger.info(f"User {callback.from_user.id} changed role")

    await callback.message.delete()

    userid = int(callback.data.split(":")[2])

    if userid == callback.from_user.id:
        await callback.message.answer("⚠️ Вы не можете изменить роль самого себя")
        await cmd_panel(callback.message, state)
        return

    await callback.message.answer("Выберите новую роль для пользователя",
                                  reply_markup=role_change_keyboard(userid))

@router.callback_query(F.data.startswith("superadmin:select_role"))
async def select_role_callback(callback: CallbackQuery, state: FSMContext):
    """Handle superadmin:select_role callback"""
    logger.info(f"User {callback.from_user.id} selected role")

    await callback.message.delete()

    userid = int(callback.data.split(":")[2])
    role = Role(callback.data.split(":")[3])
    
    await update_user.role(userid, role)

    await callback.message.answer(f"✅ Роль пользователя `{userid}` изменена на `{role.value}`")

    await cmd_panel(callback.message, state)
                                  
@router.callback_query(F.data.startswith("superadmin:delete_user"))
async def delete_user_callback(callback: CallbackQuery, state: FSMContext):
    """Handle superadmin:delete_user callback"""
    logger.info(f"User {callback.from_user.id} deleted user")
    
    userid = int(callback.data.split(":")[2])

    await callback.message.delete()
    
    if userid == callback.from_user.id:
        await callback.message.answer("⚠️ Вы не можете удалить самого себя")
        await cmd_panel(callback.message, state)
        await state.clear()
        return

    user = await get_user.by_userid(userid)

    if user.role == Role.SUPERADMIN:
        await callback.message.answer("⚠️ Вы не можете удалить супер-админа")
        await cmd_panel(callback.message, state)
        await state.clear()
        return

    await state.update_data(userid=userid)

    await callback.message.delete()

    await callback.message.answer("⚠️ Вы уверены, что хотите удалить пользователя?",
                                  reply_markup=confirm_keyboard("delete_user"))

@router.callback_query(F.data == "confirm:delete_user")
async def confirm_delete_user(callback: CallbackQuery, state: FSMContext):
    """Handle confirm:delete_user callback"""
    logger.info(f"User {callback.from_user.id} confirmed delete user")
    
    data = await state.get_data()
    userid = data.get("userid")

    await callback.message.delete()

    await delete_user.by_userid(userid)
    
    await callback.message.answer(f"✅ Пользователь `{userid}` удален")

    await state.clear()
    await cmd_panel(callback.message, state)

@router.callback_query(F.data == "cancel:delete_user")
async def cancel_delete_user(callback: CallbackQuery, state: FSMContext):
    """Handle cancel:delete_user callback"""
    logger.info(f"User {callback.from_user.id} cancelled delete user")

    await callback.message.delete()
    await callback.message.answer("🚫 Удаление пользователя отменено")

    await state.clear()
    await cmd_panel(callback.message, state)

@router.callback_query(F.data.startswith("userinfo:reset_state"))
async def reset_user_state(callback: CallbackQuery, state: FSMContext):
    """Handle userinfo:reset_state callback"""
    logger.info(f"User {callback.from_user.id} reset user state")

    await callback.message.delete()

    userid = int(callback.data.split(":")[2])

    storage = StorageKey(callback.bot.id, callback.message.chat.id, userid)
    await state.storage.set_state(storage, None)

    await callback.message.answer(f"✅ Состояние пользователя `{userid}` сброшено",
                                  parse_mode="Markdown")

    await cmd_panel(callback.message, state)