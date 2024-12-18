from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_keyboard(path: dict, go_to_main: bool = True) -> ReplyKeyboardMarkup:
    keyboard = []
    keys = list(path.keys())
    print(keys)
    for key in keys:
        keyboard.append([KeyboardButton(text=key)])
    if go_to_main:
        keyboard.append([KeyboardButton(text='На главное меню')])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )