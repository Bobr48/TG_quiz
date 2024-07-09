import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
import os
from questions import quiz_data
DB_NAME = 'quiz_bot.db'

async def return_stat(res):
    r, w = 0, 0
    for i in res:
        r_, w_ = i
        r += r_
        w += w_
    try:
        return int((r / (r + w) * 100) // 1)
    except:
        return 0


def generate_options_keyboard(answer_options, right_answer):
    builder = InlineKeyboardBuilder()
    c = 0
    for option in answer_options:
        c += 1
        builder.add(types.InlineKeyboardButton(
            text=option,
            callback_data="right_answer|" + str(c) if option == right_answer else "wrong_answer|" + str(c))
        )

    builder.adjust(1)
    return builder.as_markup()



async def get_question(message, user_id):

    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(user_id)
    correct_index = quiz_data[current_question_index]['correct_option']
    opts = quiz_data[current_question_index]['options']
    kb = generate_options_keyboard(opts, opts[correct_index])
    await message.answer(f"{quiz_data[current_question_index]['question']}", reply_markup=kb)


async def new_quiz(message):
    user_id = message.from_user.id
    current_question_index = 0
    action = 0
    await update_quiz_index(user_id, current_question_index, 0, 0)
    await get_question(message, user_id)


async def get_quiz_index(user_id):
     # Подключаемся к базе данных
     async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT question_index FROM quiz_state WHERE user_id = (?)', (user_id, )) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
async def update_quiz_index(user_id, index, res_w, res_r):
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Вставляем новую запись или заменяем ее, если с данным user_id уже существует

        await db.execute('INSERT OR REPLACE INTO quiz_state (user_id, question_index, res_w, res_r) VALUES (?, ?, ?, ?)', (user_id, index, res_w, res_r))
        # Сохраняем изменения
        await db.commit()

############################################################################################
async def get_res_w_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT res_w FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
async def get_res_r_index(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT res_r FROM quiz_state WHERE user_id = (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchone()
            if results is not None:
                return results[0]
            else:
                return 0
async def get_res_all(user_id):
    # Подключаемся к базе данных
    async with aiosqlite.connect(DB_NAME) as db:
        # Получаем запись для заданного пользователя
        async with db.execute('SELECT res_r, res_w FROM quiz_state WHERE user_id != (?)', (user_id,)) as cursor:
            # Возвращаем результат
            results = await cursor.fetchall()
            results = await return_stat(results)
            if results is not None:
                return results
            else:
                return 0

############################################################################################




async def show_res(message):
     user_id = message.from_user.id
     #current_question_index = 0
     #await update_quiz_index(user_id, current_question_index)
     res_r = await get_res_r_index(user_id)
     res_w = await get_res_w_index(user_id)
     res_all = await get_res_all(user_id)
     if res_all == 0:
         res_all = 'Нет статистики других игроков'
     await message.answer(f"Ваши ответы: Верно: {res_r}, Ошибочно: {res_w} \nОбщий процент побед в викторине не вкулючая Вас: {res_all}")


async def create_table():
    # Создаем соединение с базой данных (если она не существует, она будет создана)
    async with aiosqlite.connect(DB_NAME) as db:
        # Создаем таблицу
        await db.execute('''CREATE TABLE IF NOT EXISTS quiz_state (user_id INTEGER PRIMARY KEY, question_index INTEGER, res_w INTEGER, res_r INTEGER)''')
        # Сохраняем изменения
        await db.commit()
