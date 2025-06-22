from aiogram.fsm.state import State, StatesGroup

class CreateTask(StatesGroup):
    NAME = State()
    DESCRIPTION = State()