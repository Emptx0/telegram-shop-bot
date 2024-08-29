from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):

    # User management
    choosing_user = State()

    # Categories management
    choosing_cat = State()
    creating_cat = State()
    renaming_cat = State()

    # Item management
    add_item_name = State()
    add_item_price = State()

    choosing_item = State()

    changing_item_name = State()
    changing_item_price = State()
    changing_item_desc = State()
    changing_item_amount = State()
    deleting_item = State()
    image_uploading = State()


class CustomerStates(StatesGroup):
    viewing_item = State()
    add_to_cart = State()

    # Order
    email_address = State()
    home_address = State()

    select_currency = State()
    payment = State()
