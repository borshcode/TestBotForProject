from aiogram import Bot, Dispatcher, F
# from aiogram.client.default import DefaultBotProperties
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, ReplyKeyboardRemove
import logging

import asyncio
import os
import sqlite3

from myDB import get_categories, create_tables, get_hash
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
        cursor.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (
            msg.from_user.id,
            '',
            0,
            False
            ))
        
    else:
        # сброс пути
        cursor.execute(
            "UPDATE users SET path = ? WHERE id = ?",
            ('', msg.from_user.id)
        )
    db.commit()
    is_banned = cursor.execute(
        "SELECT is_banned FROM users WHERE id = ?",
        (msg.from_user.id,)
    ).fetchone()[0]
    if first: # проверка на команду start
        await msg.answer(
f'''
Привет, {msg.from_user.first_name}!
Я помогу тебе найти нужные тебе формулы!
Выбери нужную категорию из списка ниже:
''',
        reply_markup=kbs.get_start_keyboard(get_categories(0), is_banned)
        )
    else:
        text = '''
Выбери нужную категорию из списка ниже:
'''
        await msg.answer(
            text, 
            reply_markup=kbs.get_start_keyboard(get_categories(0), is_banned)
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
        

#? функция для отображения текущей формулы (режим обзора новых формул)
async def manager_show_cur_card(msg: Message):
    card_id = cursor.execute(
        "SELECT id_card FROM managers WHERE id = ?",
        (msg.from_user.id,)
    ).fetchone()[0]
    cursor.execute(
        "SELECT * FROM formuls WHERE id = ?",
        (card_id,)
    )
    os.chdir('./Img/')
    card = cursor.fetchone()
    await msg.answer(
f'''
Название (name): {card[2]}
Описание (description): {card[3]}
Ссылка на фото (link): {card[4]}
Путь в БД (path): {card[1]}
''')
    os.chdir('../')
    await msg.answer(
        'Страница редактирования:',
        reply_markup = kbs.get_manager_keyboard()
    )


#? обработка сообщений
@dp.message()
async def message_handler(msg: Message):
    user_id = msg.from_user.id
    # обработка "левых" команд
    if msg.text[0] == '/':
        await msg.answer('Неизвестная команда!')
        return

    #? вход в админку
    cursor.execute("SELECT input_passwd, login FROM admins WHERE id = ?",
            (user_id,)
        )
    admin = cursor.fetchone()
    # проверка: является ли пользователь админом
    if admin != None:
        if admin[0]: # если нужен ввод пароля (для обновления)
            cursor.execute(
                "UPDATE admins SET password = ? WHERE id = ?",
                (get_hash(msg.text), user_id)
            )
            cursor.execute(
                "UPDATE admins SET input_passwd = ? WHERE id = ?",
                (False, user_id)
            )
            db.commit()
            await msg.answer('Пароль успешно обновлен! Для \
входа в админ-панель используйте команду \
/admin')
        if admin[1]: # если нужен ввод пароля (для входа)
            cursor.execute(
                "SELECT password FROM admins WHERE id = ?",
                (user_id,)
            )
            if cursor.fetchone()[0] == get_hash(msg.text):
                cursor.execute(
                    "UPDATE admins SET login = ? WHERE id = ?",
                    (False, user_id)
                )
                cursor.execute(
                    "UPDATE admins SET in_admin = ? WHERE id = ?",
                    (True, user_id)
                )
                cursor.execute(
                    "UPDATE users SET path = ? WHERE id = ?",
                    ('', user_id)
                )
                db.commit()
                await msg.answer('Вы успешно вошли в админ-панель! \
Админ-панель:', reply_markup=kbs.get_admin_keyboard())
                return
            else:
                cursor.execute(
                    "UPDATE admins SET login = ? WHERE id = ?",
                    (False, msg.from_user.id)
                )
                await msg.answer('Неверный пароль!')
                await msg.answer('Вы были выкинуты из админ-панели! Причина: \
Неверный пароль.')
                return
                
        #? админка
        in_admin = cursor.execute(
            "SELECT in_admin FROM admins WHERE id = ?",
            (user_id,)
        ).fetchone()[0]
        if in_admin:
            # если пользователь в админ-панели
            if msg.text == 'Выйти из панели':
                cursor.execute(
                    "UPDATE admins SET in_admin = ? WHERE id = ?",
                    (False, user_id)
                )
                db.commit()
                await msg.answer('Вы успешно вышли из админ-панели')
                await start_handler(msg, False)
                return
            elif msg.text == 'Новые формулы':
                # переход к панели обзора формул
                card_id = cursor.execute(
                    "SELECT id FROM formuls WHERE status = ?",
                    ('CHECK',)
                ).fetchone()
                if card_id != None:
                    # если есть непросмотренные формулы
                    # создание записи админа в таблице managers
                    cursor.execute(
                        "INSERT INTO managers VALUES (?, ?, ?, ?, ?, ?)",
                        (user_id, card_id[0], False, False, '', False)
                    )
                    db.commit()
                    await manager_show_cur_card(msg)
                    del card_id
                    return
                else:
                    await msg.answer('Новых формул нет! Отдыхаем)')
                    return
            
            manager = cursor.execute(
                "SELECT * FROM managers WHERE id = ?",
                (user_id,)
            ).fetchone()

            #? страница эдита формулы
            if manager != None:
                # если админ находится в панели обзора формул
                if msg.text == 'Назад в панель🚪':
                    cursor.execute(
                        "DELETE FROM managers WHERE id = ?",
                        (user_id,)
                    )
                    db.commit()
                    await msg.answer(
                        'Админ-панель:',
                        reply_markup = kbs.get_admin_keyboard()
                    )
                    return
                elif msg.text == '✔️Редактировать и подтвердить✔️':
                    cursor.execute(
                        "UPDATE managers SET manage = ? WHERE id = ?",
                        (True, user_id)
                    )
                    db.commit()
                    path = cursor.execute(
                        "SELECT path FROM formuls WHERE id = ?",
                        (manager[1],)
                    ).fetchone()[0]
                    if path == '':
                        cursor.execute(
                            "UPDATE managers SET input_path = ? WHERE id = ?",
                            (True, user_id)
                        )
                        db.commit()
                        await msg.answer(
                            'Введите путь для формулы ("отмена" для отмены):'
                        )
                        return
                    else:
                        await msg.answer(
                            'Выберите параметр для изменения:',
                            reply_markup=kbs.get_card_edit_keyboard()
                        )
                        return
                elif msg.text == '❌Отклонить❌':
                    cursor.execute(
                        "DELETE FROM formuls WHERE id = ?",
                        (manager[1],)
                    )
                    db.commit()
                    card_id = cursor.execute(
                        "SELECT id FROM formuls WHERE status = ?",
                        ('CHECK',)
                    ).fetchone()
                    if card_id != None:
                        cursor.execute(
                            "UPDATE managers SET id_card = ? WHERE id = ?",
                            (card_id[0], user_id)
                        )
                        db.commit()
                        del card_id
                        await msg.answer('Формула удалена из БД')
                        await manager_show_cur_card(msg)
                    else:
                        cursor.execute(
                            "DELETE FROM managers WHERE id = ?",
                            (user_id,)
                        )
                        await msg.answer(
                            'Новые формулы закончились!\nАдмин-панель:',
                            reply_markup=kbs.get_admin_keyboard()
                        )
                        db.commit()
                    return
                elif msg.text == '📋❌Отклонить и выдать пред.❌📋':
                    # выдача варна и удаление формулы
                    creater_id = cursor.execute(
                        "SELECT creater_id FROM formuls WHERE id = ?",
                        (manager[1],)
                    ).fetchone()[0]
                    warns = cursor.execute(
                        "SELECT warns FROM users WHERE id = ?",
                        (creater_id,)
                    ).fetchone()[0]
                    warns += 1
                    if warns == 3:
                        # если варнов много - бан
                        cursor.execute(
                            "UPDATE users SET is_banned = ? WHERE = ?",
                            (True, creater_id)
                        )
                        db.commit()
                    cursor.execute(
                        "UPDATE users SET warns = ? WHERE id = ?",
                        (warns, creater_id)
                    )
                    cursor.execute(
                        "DELETE FROM formuls WHERE id = ?",
                        (manager[1],)
                    )
                    db.commit()
                    await msg.answer('Предупреждение выдано!')
                    del creater_id

                    # обновление id_card
                    card_id = cursor.execute(
                        "SELECT id FROM formuls WHERE status = ?",
                        ('CHECK',)
                    ).fetchone()
                    if card_id != None:
                        cursor.execute(
                            "UPDATE managers SET id_card = ? WHERE id = ?",
                            (card_id[0], user_id)
                        )
                        db.commit()
                        del card_id
                        await msg.answer('Формула удалена из БД')
                        await manager_show_cur_card(msg)
                    else:
                        cursor.execute(
                            "DELETE FROM managers WHERE id = ?",
                            (user_id,)
                        )
                        await msg.answer(
                            'Новые формулы закончились!\nАдмин-панель:',
                            reply_markup=kbs.get_admin_keyboard()
                        )
                        db.commit()
                    return                
                if manager[3]:
                    # если необходимо ввести путь формулы в БД
                    if msg.text.lower() != 'отмена':
                        cursor.execute(
                            "UPDATE formuls SET path = ? WHERE id = ?",
                            (msg.text, manager[1])
                        )
                        await msg.answer('Путь успешно сохранен!')
                    cursor.execute(
                        "UPDATE managers SET input_path = ? WHERE id = ?",
                        (False, user_id)
                    )
                    db.commit()
                    await manager_show_cur_card(msg)
                    return
                elif not manager[3] and not manager[5] and manager[2]:
                    # если нажата кнопка выбора параметра
                    buttons = [
                        'name',
                        'description',
                        'link',
                        'path'
                    ]
                    if msg.text in buttons:
                        cursor.execute(
                            "UPDATE managers SET input = ? WHERE id = ?",
                            (True, user_id)
                        )
                        cursor.execute(
                            "UPDATE managers SET input_name = ? WHERE id = ?",
                            (msg.text, user_id)
                        )
                        db.commit()
                        await msg.answer(
                            f'Введите новый {msg.text}:'
                        )
                        return
                    elif msg.text == '✔️Опубликовать✔️':
                        cursor.execute(
                            "UPDATE formuls SET status = ? WHERE id = ?",
                            ('OK', manager[1])
                        )
                        cursor.execute(
                            "UPDATE managers SET manage = ? WHERE id = ?",
                            (False, user_id)
                        )
                        card_id = cursor.execute(
                            "SELECT id FROM formuls WHERE status = ?",
                            ('CHECK',)
                        ).fetchone()
                        if card_id != None:
                            cursor.execute(
                                "UPDATE managers SET id_card = ? WHERE id = ?",
                                (card_id[0], user_id)
                            )
                            await manager_show_cur_card(msg)
                        else:
                            cursor.execute(
                                "DELETE FROM managers WHERE id = ?",
                                (user_id,)
                            )
                            await msg.answer(
                                'Новые формулы закончились!\nАдмин-панель:',
                                reply_markup=kbs.get_admin_keyboard()
                            )
                        db.commit()
                        return
                elif manager[5]:
                    # если необходим ввод значения параметра
                    cursor.execute(
                        f"UPDATE formuls SET {manager[4]} = ? WHERE id = ?",
                        (msg.text, manager[1])
                    )
                    cursor.execute(
                        "UPDATE managers SET input_name = ? WHERE id = ?",
                        ('', user_id)
                    )
                    cursor.execute(
                        "UPDATE managers SET input = ? WHERE id = ?",
                        (False, user_id)
                    )
                    db.commit()
                    await manager_show_cur_card(msg)
                    return
                    

    creator = cursor.execute(
        "SELECT input_text FROM creators WHERE id = ?",
        (user_id,)
    ).fetchone()
    #? предложение новой формулы
    # проверка на нахрждении в меню добавления
    if creator == None:
        if msg.text == 'Предложить формулу':
            # заход в --//--
            cursor.execute(
                "INSERT INTO creators VALUES (?, ?, ?, ?, ?)",
                (user_id, 'name', '', '', '')
            )
            db.commit()
            await msg.answer(
                'Введите название формулы ("отмена" для выхода):',
                reply_markup=ReplyKeyboardRemove()
            )
            return
    else:
        if msg.text.lower() == 'отмена':
            # если введена "отмена"
            cursor.execute(
                "DELETE FROM creators WHERE id = ?",
                (user_id,)
            )
            db.commit()
            await start_handler(msg, False)
            return
        if creator[0] == 'name':
            # ввод имени формулы
            cursor.execute(
                "UPDATE creators SET formul_name = ? WHERE id = ?",
                (msg.text, user_id)
            )
            cursor.execute(
                "UPDATE creators SET input_text = ? WHERE id = ?",
                ('description', user_id)
            )
            db.commit()
            await msg.answer(
                'Введите описание формулы ("нет" - пустое описание) \
("отмена" для выхода):'
            )
            return
        elif creator[0] == 'description':
            # ввод описания
            if msg.text.lower() != 'нет':
                cursor.execute(
                    "UPDATE creators SET formul_description = ? WHERE id = ?",
                    (msg.text, user_id)
                )
            else:
                cursor.execute(
                    "UPDATE creators SET formul_description = ? WHERE id = ?",
                    ('', user_id)
                )
            cursor.execute(
                "UPDATE creators SET input_text = ? WHERE id = ?",
                ('link', user_id)
            )
            db.commit()
            await msg.answer(
                'Введите ссылку на фото формулы ("отмена" для выхода):'
            )
            return
        elif creator[0] == 'link':
            # ввод ссылки на фото
            cursor.execute(
                "UPDATE creators SET formul_link = ? WHERE id = ?",
                (msg.text, user_id)
            )
            db.commit()

            # сохранение в БД
            creator = cursor.execute(
                "SELECT formul_name, formul_description, formul_link \
FROM creators WHERE id = ?",
                (user_id,)
            ).fetchone()
            cursor.execute(
                "INSERT INTO formuls(path, name, description, link, status, \
creater_id) VALUES (?, ?, ?, ?, ?, ?)",
                ('', creator[0], creator[1], creator[2], 'CHECK', user_id)
            )
            cursor.execute(
                "DELETE FROM creators WHERE id = ?",
                (user_id,)
            )
            db.commit()

            await msg.answer(
                'Как только Ваша формула пройдет проверку, она будет \
опубликована в соответствующей категории.'
            )
            await start_handler(msg, False)
            download_photos_from_DB()
            return

    
    #? выбор формул
    keyboard = None # переменная под клавиатуру
    file = False
    # получение пути из БД
    old_path = cursor.execute(
        "SELECT path FROM users WHERE id = ?",
        (user_id,)
    ).fetchone()[0]

    # формирование нового пути
    new_path = old_path + msg.text + '/'
    level_names = new_path.split('/')
    level_names.remove('')
    level = len(level_names) # глубина "погружения" :)

    categories = get_categories(level, new_path) # получение новых категорий
    if categories != 1:
        if msg.text in get_categories(level-1):
            keyboard = kbs.get_keyboard(categories) # запись клавиатуры
            
            # обновление пути в профиле пользователя ( БД )
            cursor.execute(
            "UPDATE users SET path = ? WHERE id = ?",
            (new_path, user_id)
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
