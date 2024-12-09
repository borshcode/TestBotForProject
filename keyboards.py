from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

start_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🧮АЛГЕБРА🧮')
        ],
        [
            KeyboardButton(text='📏ГЕОМЕТРИЯ📏')
        ]
    ],
    resize_keyboard=True
)