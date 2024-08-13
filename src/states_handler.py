from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    choosing_user = State()

    choosing_cat = State()
    creating_cat = State()
    renaming_cat = State()
