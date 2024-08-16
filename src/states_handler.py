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

    choosing_item = State()

    changing_item_name = State()
    changing_item_price = State()
    changing_item_desc = State()
    changing_item_amount = State()
    image_uploading = State()
