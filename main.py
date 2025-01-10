from aiogram import Bot, Dispatcher, F
# from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import logging

import asyncio
import os

from db import Json
from downloadPhoto import download_photo, get_name
import config as cfg
import keyboards as kbs


# default=DefaultBotProperties(parse_mode='HTML')
bot = Bot(cfg.TOKEN) # создание экземпляра бота
dp = Dispatcher() # создание экзепляра диспетчера


async def main(): # запуск бота
    await bot.delete_webhook(drop_pending_updates=True) # игнор команд, которые были даны в отключке
    await dp.start_polling(bot) # запуск бота


# обработка команды /start
@dp.message(Command('start'))
async def start_handler(msg: Message, first: bool = True):
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
        await msg.answer(text, reply_markup=kbs.get_keyboard(formuls.content, False))


# обработчики нажатий на кнопки
@dp.message(F.text == 'На главное меню')
async def go_to_start_handler(msg: Message):
    await start_handler(msg, False) # возврат главному меню


@dp.message()
async def show_formul_handler(msg: Message):
    keys = list(formuls.content.keys())
    keyboard = None # сюда запишем клавиатуру
    for key in keys: # заходим в выбор предметов
        if msg.text in keys:
            keyboard = kbs.get_keyboard(formuls.content[msg.text]) # получаем клавиатуру категорий
            break
        keys1 = list(formuls.content[key].keys())
        for key1 in keys1: # заходим в выбор категории
            if msg.text in keys1:
                keyboard = kbs.get_keyboard(formuls.content[key][msg.text]) # получаем клавиатуру формул
                break
            keys2 = list(formuls.content[key][key1].keys())
            if msg.text in keys2:
                os.chdir('./Img/')
                try: # игнор ошибки
                    await msg.answer(formuls.content[key][key1][msg.text][1]) # отправка описания
                except IndexError:
                    pass
                await msg.answer_photo(FSInputFile(get_name(formuls.content[key][key1][msg.text][0]))) # отправка формулы
                os.chdir('../')
                return
            
    await msg.answer('Выберите:', reply_markup=keyboard) # отправка клавиатуры


if __name__ == '__main__':
    download_photo()
    formuls = Json('formuls.json') # созданиме экземпляра класса Json
    formuls.load() # загрузка Json-файла
    logging.basicConfig(level=logging.INFO) # запуск логирования
    asyncio.run(main())
