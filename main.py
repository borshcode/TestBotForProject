from aiogram import Bot, Dispatcher, F
# from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import logging

import asyncio
import os
import sqlite3

from myJson import Json
from myDB import get_categories, create_tables
from downloadPhoto import *
import config as cfg
import keyboards as kbs


#? База Данных: инициализация
db = sqlite3.connect('database.db')
cursor = db.cursor()


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
    # проверка, зареган ли юзер?
    cursor.execute("SELECT * FROM users WHERE id = ?", (msg.from_user.id,))
    if cursor.fetchone() == None:
        # регистрация юзера в БД
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?, ?)", (
            msg.from_user.id,
            '',
            0,
            False,
            False
            ))
        
    else:
        # сброс пути
        cursor.execute(
            "UPDATE users SET path = ? WHERE id = ?",
            ('', msg.from_user.id)
        )
    db.commit()
    if first: # проверка на команду start
        await msg.answer(
f'''
Привет, {msg.from_user.first_name}!
Я помогу тебе найти нужные тебе формулы!
Выбери нужную категорию из списка ниже:
''',
        reply_markup=kbs.get_start_keyboard(get_categories(0))
        )
    else:
        text = '''
Выбери нужную категорию из списка ниже:
'''
        await msg.answer(
            text, 
            reply_markup=kbs.get_start_keyboard(get_categories(0))
        )


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
async def message_handler(msg: Message):
    # обработка "левых" команд
    if msg.text[0] == '/':
        await msg.answer('Неизвестная команда!')
        return

    #? вход в админку
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
                await msg.answer('Вы успешно вошли в админ-панель! \
Админ-панель:', reply_markup=kbs.get_admin_keyboard())
            else:
                cursor.execute(
                    "UPDATE admins SET login = ? WHERE id = ?",
                    (False, msg.from_user)
                )
                await msg.answer('Неверный пароль!')
                await msg.answer('Вы были выкинуты из админ-панели! Причина: \
Неверный пароль.')
                return
                
        #? админка
        in_admin = cursor.execute(
            "SELECT in_admin FROM admins WHERE id = ?",
            (msg.from_user.id,)
        ).fetchone()
        if in_admin:
            if msg.text == 'Выйти из панели':
                cursor.execute(
                    "UPDATE admins SET in_admin = ? WHERE id = ?",
                    (False, msg.from_user.id)
                )
                db.commit()
                await msg.answer('Вы успешно вышли из админ-панели')
                await start_handler(msg, False)
            elif msg.text == 'Новые формулы':
                cursor.execute(
                    "UPDATE admins SET manager = ? WHERE id = ?",
                    (True, msg.from_user.id)
                )
                db.commit()

    if msg.text == 'Предложить формулу':
        pass
    
    #? выбор формул
    keyboard = None # переменная под клавиатуру
    file = False
    # получение пути из БД
    old_path = cursor.execute(
        "SELECT path FROM users WHERE id = ?",
        (msg.from_user.id,)
    ).fetchone()[0]

    # формирование нового пути
    new_path = old_path + msg.text + '/'
    level_names = new_path.split('/')
    level_names.remove('')
    level = len(level_names) # глубина "погружения" :)

    categories = get_categories(level, new_path) # получение новых категорий
    if categories != 1:
        keyboard = kbs.get_keyboard(categories) # запись клавиатуры
        
        # обновление пути в профиле пользователя ( БД )
        cursor.execute(
        "UPDATE users SET path = ? WHERE id = ?",
        (new_path, msg.from_user.id)
        )
        db.commit()
    else:
        file = True
        # получение описания и ссылки из БД
        data = cursor.execute(
            "SELECT description, link FROM formuls \
            WHERE path = ? AND name = ?",
            (old_path, msg.text)
        ).fetchone()
        description, file_link = data[0], data[1]

    if file:
        # отправка фото и описания
        os.chdir('./Img/')
        await msg.answer_photo(FSInputFile(get_name(file_link)))
        if description:
            await msg.answer(description)
        os.chdir('../')

        

    if keyboard != None:
        # отправка клавиатуры
        await msg.answer('Выберите:', reply_markup=keyboard)

#? вход в программу
if __name__ == '__main__':
    create_tables()
    download_photos_from_DB()
    logging.basicConfig(level=logging.INFO) # запуск логирования
    asyncio.run(main())
