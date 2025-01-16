from aiogram import Bot, Dispatcher, F
# from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import logging

import asyncio
import os
import sqlite3

from myJson import Json
from downloadPhoto import download_photo, get_name
import config as cfg
import keyboards as kbs


#? База Данных: инициализация
db = sqlite3.connect('database.db')
cursor = db.cursor()

cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    id INT,
    is_admin BOOL,
    is_banned BOOL
)""")
db.commit()


#? БОТ
# default=DefaultBotProperties(parse_mode='HTML')
bot = Bot(cfg.TOKEN) # создание экземпляра бота
dp = Dispatcher() # создание экзепляра диспетчера


async def main(): # запуск бота
    # игнор команд, которые были даны в отключке
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot) # запуск бота


# обработка команды /start
@dp.message(Command('start'))
async def start_handler(msg: Message, first: bool = True):
    # print(msg.from_user.id) #TODO: отладка, при релизе убрать
    cursor.execute("SELECT * FROM users WHERE id = ?", (msg.from_user.id,))
    if cursor.fetchone() == None:
        cursor.execute("INSERT INTO users VALUES (?, ?, ?)", (
            msg.from_user.id,
            False,
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


#TODO: добавить админ-панель


@dp.message()
async def show_formul_handler(msg: Message):
    #TODO: сделать игнор неизвестных
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
                await msg.answer_photo(FSInputFile(get_name(
                                    formuls.content[key][key1][msg.text][0]
                                    ))) # отправка формулы
                os.chdir('../')
                return
            
    await msg.answer('Выберите:', reply_markup=keyboard) # отправка клавиатуры


#? вход в программу
if __name__ == '__main__':
    download_photo()
    formuls = Json('formuls.json') # созданиме экземпляра класса Json
    formuls.load() # загрузка Json-файла
    logging.basicConfig(level=logging.INFO) # запуск логирования
    asyncio.run(main())
