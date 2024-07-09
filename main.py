
import aiosqlite
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import F
import os

import dotenv

import questions
import hendlers
from functions import return_stat, generate_options_keyboard, get_question, new_quiz, get_quiz_index, update_quiz_index, get_res_w_index, get_res_r_index, get_res_all, show_res, create_table

# Включаем логирование, чтобы не пропустить важные сообщения
logging.basicConfig(level=logging.INFO)

# Замените "YOUR_BOT_TOKEN" на токен, который вы получили от BotFather
dotenv.load_dotenv()

API_TOKEN =os.getenv('API_TOKEN')
# Объект бота
bot = Bot(token=API_TOKEN)
# Диспетчер
dp = Dispatcher()
dp.include_router(hendlers.router)
# Зададим имя базы данных


# Структура квиза
quiz_data = questions.quiz_data




# Запуск процесса поллинга новых апдейтов
async def main():

    # Запускаем создание таблицы базы данных
    await create_table()

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
