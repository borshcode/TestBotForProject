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
bot = Bot(cfg.TOKEN)
dp = Dispatcher()


async def main(): # запуск бота
    await bot.delete_webhook(drop_pending_updates=True) # игнор команд, которые были даны в отключке
    await dp.start_polling(bot)


# обработка команды /start
@dp.message(Command('start'))
async def start_handler(msg: Message, first: bool = True):
    formuls.load()
    if first:
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
    await start_handler(msg, False)


@dp.message()
async def show_formul_handler(msg: Message):
    keys = list(formuls.content.keys())
    keyboard = None
    for key in keys: # заходим в выбор предметов
        if msg.text in keys:
            keyboard = kbs.get_keyboard(formuls.content[msg.text])
            break
        keys1 = list(formuls.content[key].keys())
        for key1 in keys1: # заходим в выбор категории
            if msg.text in keys1:
                keyboard = kbs.get_keyboard(formuls.content[key][msg.text])
                break
            keys2 = list(formuls.content[key][key1].keys())
            if msg.text in keys2:
                os.chdir('./Img/')
                await msg.answer_photo(FSInputFile(get_name(formuls.content[key][key1][msg.text])))
                os.chdir('../')
                return
            
    await msg.answer('Выберите:', reply_markup=keyboard)


if __name__ == '__main__':
    download_photo()
    formuls = Json('formuls.json')
    formuls.load()
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
