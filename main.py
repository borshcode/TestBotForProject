from aiogram import Bot, Dispatcher, F
# from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile
import logging

import asyncio

from db import Json
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
async def start_handler(msg: Message):
    await msg.answer(
        f'''
Привет, {msg.from_user.first_name}!
Я помогу тебе найти нужные тебе формулы!
Выбери нужную категорию из списка ниже:
''',
        reply_markup=kbs.start_kb
    )


# обработчики нажатий на кнопку
@dp.message(F.text == '🧮АЛГЕБРА🧮')
async def algebra_handler(msg: Message):
    formuls.load()
    path = formuls.content['Алгебра']['Формулы сокращенного умножения']['Квадрат суммы']
    print(path)
    await msg.answer_photo(FSInputFile(path))


@dp.message(F.text == '📏ГЕОМЕТРИЯ📏')
async def geometry_handler(msg: Message):
    pass



if __name__ == '__main__':
    formuls = Json('formuls.json')
    formuls.load()
    print(formuls.content)
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
