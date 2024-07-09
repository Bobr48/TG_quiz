import aiosqlite
import asyncio
import logging
from aiogram import Bot, Router, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
import os
from functions import return_stat, generate_options_keyboard, get_question, new_quiz, get_quiz_index, update_quiz_index, get_res_w_index, get_res_r_index, get_res_all, show_res, create_table
from questions import quiz_data
router = Router()


@router.callback_query(F.data.startswith("right_"))
async def right_answer(callback: types.CallbackQuery):
    action = int(callback.data.split("|")[1]) - 1
    #await update_quiz_answer(callback.from_user.id, action)

    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )
    current_question_index = await get_quiz_index(callback.from_user.id)
    res_w = await get_res_w_index(callback.from_user.id)
    res_r = await get_res_r_index(callback.from_user.id)
    res_r += 1
    await callback.message.answer(f"Верно! \nВаш ответ: {quiz_data[current_question_index]['options'][int(action)]}")

    #await callback.message.answer("Верно!")
    current_question_index = await get_quiz_index(callback.from_user.id)
    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, res_w, res_r)



    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


@router.callback_query(F.data.startswith("wrong_"))
async def wrong_answer(callback: types.CallbackQuery):
    action = int(callback.data.split("|")[1]) - 1

    #await update_quiz_answer(callback.from_user.id, action)
    await callback.bot.edit_message_reply_markup(
        chat_id=callback.from_user.id,
        message_id=callback.message.message_id,
        reply_markup=None
    )

    res_w = await get_res_w_index(callback.from_user.id)
    res_r = await get_res_r_index(callback.from_user.id)
    res_w += 1
    # Получение текущего вопроса из словаря состояний пользователя
    current_question_index = await get_quiz_index(callback.from_user.id)
    correct_option = quiz_data[current_question_index]['correct_option']
    await callback.message.answer(f"Ваш ответ: {quiz_data[current_question_index]['options'][int(action)]}")
    await callback.message.answer(f"Неправильно. Правильный ответ: {quiz_data[current_question_index]['options'][correct_option]}")

    # Обновление номера текущего вопроса в базе данных
    current_question_index += 1
    await update_quiz_index(callback.from_user.id, current_question_index, res_w, res_r)


    if current_question_index < len(quiz_data):
        await get_question(callback.message, callback.from_user.id)
    else:
        await callback.message.answer("Это был последний вопрос. Квиз завершен!")


# Хэндлер на команду /start
@router.message(Command("start"))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(types.KeyboardButton(text="Начать игру"))
    builder.add(types.KeyboardButton(text="Показать ответы"))
    await message.answer("Добро пожаловать в квиз!", reply_markup=builder.as_markup(resize_keyboard=True))


# Хэндлер на команду /help
@router.message(Command("help"))
async def cmd_start(message: types.Message):
    await message.answer("Добро пожаловать в квиз!, /start - запуск, /asnwer - статистика, /quiz - начать Квиз")



# Хэндлер на команду /answer
@router.message(F.text=="Показать ответы")
@router.message(Command("answer"))
async def cmd_answer(message: types.Message):
    await show_res(message)

# Хэндлер на команду /quiz
@router.message(F.text=="Начать игру")
@router.message(Command("quiz"))
async def cmd_quiz(message: types.Message):

    await message.answer(f"Давайте начнем квиз!")
    await new_quiz(message)
