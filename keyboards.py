from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import sqlite3

db = sqlite3.connect('database.db')
cursor = db.cursor()

def get_keyboard(cats: list, go_to_main: bool = True) -> ReplyKeyboardMarkup:
    keyboard = []
    for cat in cats:
        keyboard.append([KeyboardButton(text=cat)])
    if go_to_main:
        keyboard.append([KeyboardButton(text='На главное меню')])
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True
    )


def get_start_keyboard(
        cats: list,
        is_banned: bool = False
    ) -> ReplyKeyboardMarkup:
    keyboard = []
    for cat in cats:
        keyboard.append([KeyboardButton(text=cat)])
    if not is_banned:
        keyboard.append([KeyboardButton(text='Предложить формулу')])

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
        ],
        resize_keyboard=True
    )
    return keyboard


def get_manager_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='✔️Редактировать и подтвердить✔️')],
            [KeyboardButton(text='❌Отклонить❌')],
            [KeyboardButton(text='📋❌Отклонить и выдать пред.❌📋')],
            [
                KeyboardButton(text='Назад в панель🚪')
            ]
        ],
        resize_keyboard=True
    )


def get_card_edit_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text='name')],
            [KeyboardButton(text='description')],
            [KeyboardButton(text='link')],
            [KeyboardButton(text='path')],
            [
                KeyboardButton(text='✔️Опубликовать✔️')
            ]
        ],
        resize_keyboard=True
    )


def get_null_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[]
    )
