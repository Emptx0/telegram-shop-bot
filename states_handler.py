from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    choosing_user = State()
