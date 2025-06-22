from aiogram.fsm.state import State, StatesGroup

class CreateTask(StatesGroup):
    NAME = State()
    DESCRIPTION = State()

class AddNote(StatesGroup):
    BODY = State()

class SettingsLink(StatesGroup):
    LINK = State()
    TIME = State()