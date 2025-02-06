from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_keyboard(path: dict, go_to_main: bool = True) -> ReplyKeyboardMarkup:
    keyboard = []
    keys = list(path.keys())
    for key in keys:
        keyboard.append([KeyboardButton(text=key)])
    if go_to_main:
        keyboard.append([KeyboardButton(text='На главное меню')])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text='Новые формулы'),
                KeyboardButton(text='Сменить пароль'),
            ],
            [KeyboardButton(text='Выйти из панели')]
        ]
    )
    return keyboard


def get_manager_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='✔️Редактировать и подтвердить✔️')],
            [KeyboardButton(text='❌Отклонить❌')],
            [KeyboardButton(text='📋❌Отклонить и выдать пред.❌📋')],
            [
                KeyboardButton(text='Следующая ➡️'),
                KeyboardButton(text='Назад в панель🚪')
            ]
        ]
    )
