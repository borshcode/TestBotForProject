from aiogram import Bot, Dispatcher, F
# from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import logging

import asyncio
import os
import sqlite3

from myJson import Json
from downloadPhoto import download_photos_from_json, download_photos_from_DB,\
    get_name
import config as cfg
import keyboards as kbs


#? База Данных: инициализация
db = sqlite3.connect('database.db')
cursor = db.cursor()

def create_tables():
    cursor.execute("""CREATE TABLE IF NOT EXISTS users (
        id INT,
        is_banned BOOL
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS admins (
        id INT,
        nickname TEXT,
        password TEXT,
        in_admin BOOL,
        input_passwd BOOL,
        login BOOL
    )""")
    cursor.execute("""CREATE TABLE IF NOT EXISTS formuls (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        path TEXT,
        name TEXT,
        description TEXT,
        link TEXT,
        status TEXT
    )""")
    db.commit()


#? БОТ
# default=DefaultBotProperties(parse_mode='HTML')
bot = Bot(cfg.TOKEN) # создание экземпляра бота
dp = Dispatcher() # создание экзепляра диспетчера


#? запуск бота
async def main():
    # игнор команд, которые были даны в отключке
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot) # запуск бота


#? обработка команды /start
@dp.message(Command('start'))
async def start_handler(msg: Message, first: bool = True):
    # print(msg.from_user.username) #TODO: отладка, при релизе убрать
    cursor.execute("SELECT * FROM users WHERE id = ?", (msg.from_user.id,))
    if cursor.fetchone() == None:
        cursor.execute("INSERT INTO users VALUES (?, ?)", (
            msg.from_user.id,
            False
            ))
        db.commit()
    if first: # проверка на команду start
        await msg.answer(
f'''
Привет, {msg.from_user.first_name}!
Я помогу тебе найти нужные тебе формулы!
Выбери нужную категорию из списка ниже:
''',
        reply_markup=kbs.get_keyboard(formuls.content, False)
        )
    else:
        text = f'''
Выбери нужную категорию из списка ниже:
'''
        await msg.answer(text, reply_markup=kbs.get_keyboard(
            formuls.content,
            False
            ))


# обработчики нажатий на кнопки
@dp.message(F.text == 'На главное меню')
async def go_to_start_handler(msg: Message):
    await start_handler(msg, False) # возврат главному меню


#? админ-панель
@dp.message(Command('admin'))
async def admin_handler(msg: Message):
    cursor.execute("SELECT * FROM admins WHERE id = ?", (msg.from_user.id,))
    admin = cursor.fetchone()
    if admin == None:
        await msg.answer('Неизвестная команда!')
        return
    if admin[2] == '':
        await msg.answer(f'Добро пожаловать, {msg.from_user.first_name}!\n\
Придумайте пароль для входа в админ-панель:')
        cursor.execute(
            "UPDATE admins SET input_passwd = ? WHERE id = ?",
            (True, msg.from_user.id)
        )
        db.commit()
    else:
        await msg.answer(f'{msg.from_user.first_name}, введите Ваш пароль:')
        cursor.execute(
            "UPDATE admins SET login = ? WHERE id = ?",
            (True, msg.from_user.id)
        )
        db.commit()


#? обработка сообщений
@dp.message()
async def show_formul_handler(msg: Message):
    if msg.text[0] == '/':
        await msg.answer('Неизвестная команда!')
        return
    keys = list(formuls.content.keys())
    keyboard = None # сюда запишем клавиатуру
    for key in keys: # заходим в выбор предметов
        if msg.text in keys:
            
            keyboard = kbs.get_keyboard(formuls.content[msg.text])
            break
        keys1 = list(formuls.content[key].keys())
        for key1 in keys1: # заходим в выбор категории
            if msg.text in keys1:
                # получаем клавиатуру формул
                keyboard = kbs.get_keyboard(formuls.content[key][msg.text])
                break
            keys2 = list(formuls.content[key][key1].keys())
            if msg.text in keys2:
                os.chdir('./Img/')
                try: # игнор ошибки
                    # отправка описания
                    await msg.answer(formuls.content[key][key1][msg.text][1])
                except IndexError:
                    pass
                # отправка формулы
                await msg.answer_photo(FSInputFile(get_name(
                                    formuls.content[key][key1][msg.text][0]
                                    )))
                os.chdir('../')
                return
    
    if keyboard != None:
        # отправка клавиатуры
        await msg.answer('Выберите:', reply_markup=keyboard)
    else:
        cursor.execute("SELECT input_passwd, login FROM admins WHERE id = ?",
                        (msg.from_user.id,)
                        )
        admin = cursor.fetchone()
        if admin != None:
            if admin[0]:
                cursor.execute(
                    "UPDATE admins SET password = ? WHERE id = ?",
                    (msg.text, msg.from_user.id)
                )
                cursor.execute(
                    "UPDATE admins SET input_passwd = ? WHERE id = ?",
                    (False, msg.from_user.id)
                )
                db.commit()
                await msg.answer('Пароль успешно обновлен! Для \
входа в админ-панель используйте команду \
/admin')
            if admin[1]:
                cursor.execute(
                    "SELECT password FROM admins WHERE id = ?",
                    (msg.from_user.id,)
                )
                if cursor.fetchone()[0] == msg.text:
                    cursor.execute(
                        "UPDATE admins SET login = ? WHERE id = ?",
                        (False, msg.from_user.id)
                    )
                    cursor.execute(
                        "UPDATE admins SET in_admin = ? WHERE id = ?",
                        (True, msg.from_user.id)
                    )
                    db.commit()
                    await msg.answer('Вы успешно вошли в систему! \
Админ-панель:', reply_markup=kbs.get_admin_keyboard())


#? вход в программу
if __name__ == '__main__':
    create_tables()
    # download_photos_from_json()
    download_photos_from_DB()
    # formuls = Json('formuls.json') # созданиме экземпляра класса Json
    # formuls.load() # загрузка Json-файла
    logging.basicConfig(level=logging.INFO) # запуск логирования
    asyncio.run(main())
