from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Task

def admin_panel_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="ℹ️ Информация о пользователе", callback_data="admin:user_info")],
            [InlineKeyboardButton(text="❌ Закрыть меню", callback_data="admin:close_menu")]
        ]
    )
    return keyboard

def user_info_keyboard(userid: int, is_superadmin: bool) -> InlineKeyboardMarkup:
    superadmin_buttons = [[
        InlineKeyboardButton(text="🚫 Удалить пользователя", callback_data=f"superadmin:delete_user:{userid}"),
        InlineKeyboardButton(text="🔑 Изменить роль", callback_data=f"superadmin:change_role:{userid}"),
    ],
    [InlineKeyboardButton(text="🔄 Сбросить состояние", callback_data=f"userinfo:reset_state:{userid}")]
    ]
    admin_buttons = [
        InlineKeyboardButton(text="🔙 Назад", callback_data="userinfo:back")
    ]
    superadmin_buttons.append(admin_buttons)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=superadmin_buttons if is_superadmin else [admin_buttons]
    )
    return keyboard

def role_change_keyboard(userid: int) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="👨‍💼 Админ", callback_data=f"superadmin:select_role:{userid}:ADMIN"),
             InlineKeyboardButton(text="👤 Пользователь", callback_data=f"superadmin:select_role:{userid}:USER")]
        ]
    )
    return keyboard

def confirm_keyboard(action: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="✅ Да", callback_data=f"confirm:{action}"),
             InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel:{action}")]
        ]
    )
    return keyboard

def task_list_keyboard(tasks: list[Task]) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=f"{'✅' if tasks[id].is_completed else '❌'} {tasks[id].name}", callback_data=f"tasks:{id}")] for id in range(len(tasks))
    ]
    keyboard.append([InlineKeyboardButton(text=f" ", callback_data=f"tasks:SKIP")],)
    keyboard.append([InlineKeyboardButton(text=f"📝 Добавить", callback_data=f"tasks:add")])

    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def task_keyboard(task: Task, id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text=f"{'✅' if task.is_completed else '❌'}", callback_data=f"task:status:{id}"),
         InlineKeyboardButton(text=f"🗑 Удалить", callback_data=f"task:delete:{id}")],
        [InlineKeyboardButton(text="⬅️ Назад", callback_data=f"task:back")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def journal_keyboard(delete: bool = False, parsed_link: str|None = None) -> InlineKeyboardMarkup:
    keyboard = []
    if parsed_link != '': keyboard.append([InlineKeyboardButton(text="🔗 Открыть приложение", url=parsed_link)])
    keyboard.append([InlineKeyboardButton(text="📝 Записать", callback_data="journal:add")])
    if delete: keyboard[0 if parsed_link == '' else 1].append(InlineKeyboardButton(text="🗑 Удалить", callback_data="journal:delete"))
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def settings_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔗 Изменить ссылку", callback_data="settings:link")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def personal_keyboard(personal: dict[str, str]) -> InlineKeyboardMarkup:
    keyboard = []
    step = []
    for k, v in personal.items():
        step.append(InlineKeyboardButton(text=f"🏷 {v[0]}", callback_data=f"personal:{k}"))
        if len(step) % 3 == 0:
            keyboard.append(step)
            step = []
    keyboard.append(step)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def personal_none_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton(text="🔄 Убрать значение", callback_data="personal:none")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)