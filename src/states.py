from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


class Stage(StatesGroup):
    input: State = State()
    choice: State = State()
    columns: State = State()