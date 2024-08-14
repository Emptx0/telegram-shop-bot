from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):

    # User management
    choosing_user = State()

    # Categories management
    choosing_cat = State()
    creating_cat = State()
    renaming_cat = State()

    # Item management
    item_name = State()
    item_price = State()
    item_desc = State()
    item_amount = State()
    image_uploading = State()

    choosing_item = State()
