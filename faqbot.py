 # -*- coding: utf-8 -*-

import os
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from models import User
from db_manager import DB_manager
from fuzzywuzzy import fuzz
import pymorphy2
from dotenv import load_dotenv
load_dotenv()

token = os.getenv('TOKEN')
bot = Bot(token=token)
dp = Dispatcher(bot)

loop = asyncio.get_event_loop()

dbM = DB_manager()
dbM.create_table(User)

current_user = None

morph = pymorphy2.MorphAnalyzer()

with open("base/questions1.txt", "r", encoding='utf8') as f_:
    questions1 = f_.readlines()

with open("base/questions2.txt", "r", encoding='utf8') as f_:
    questions2 = f_.readlines()

with open("base/questions3.txt", "r", encoding='utf8') as f_:
    questions3 = f_.readlines()

def classify_question(text, status):
    text = ' '.join(morph.parse(word)[0].normal_form for word in text.split())
    scores = list()

    if status=='User':
        for question in questions1:
            norm_question = ' '.join(morph.parse(word)[0].normal_form for word in question.split())
            scores.append(fuzz.token_sort_ratio(norm_question.lower(), text.lower()))
        # print(scores)
        answer = questions1[scores.index(max(scores))]
    elif status=='Vendor':
        for question in questions2:
            norm_question = ' '.join(morph.parse(word)[0].normal_form for word in question.split())
            scores.append(fuzz.token_sort_ratio(norm_question.lower(), text.lower()))
        # print(scores)
        answer = questions2[scores.index(max(scores))] 
    elif status=='Distributor':
        for question in questions3:
            norm_question = ' '.join(morph.parse(word)[0].normal_form for word in question.split())
            scores.append(fuzz.token_sort_ratio(norm_question.lower(), text.lower()))
        # print(scores)
        answer = questions3[scores.index(max(scores))]

    return f"Ответ на вопрос: {answer}"


@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    # print(message)
    try:
        dbM.add_record(User, message)
        dbM.session.commit()
    except Exception as ex:
        # print(ex)
        dbM.session.rollback()
    # print(dbM.get_user_from_id(message.chat.id))
    await bot.send_message(message.chat.id,
    """Hello!
I am a chat bot of the company 'Unknown Company'. 
I am ready to answer your questions.

If you need to change the language, type 
/lang.
If you need to change the status, type 
/status.

By default, the language of our communication is English,
and your status is User.
    """
   )

@dp.message_handler(commands=['help'])
async def send_welcome(message: types.Message):
    await message.reply("Help")

@dp.callback_query_handler(lambda c: c.data == 'English')
async def process_callback_button1(callback_query: types.CallbackQuery):
    dbM.update_user_lang(callback_query.from_user.id,'English')
    # print(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "All right, let's continue. What is your question?")

@dp.callback_query_handler(lambda c: c.data == 'German')
async def process_callback_button2(callback_query: types.CallbackQuery):
    dbM.update_user_lang(callback_query.from_user.id,'German')
    # print(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Okay, lass uns weitermachen. Welche Frage haben Sie?')

@dp.callback_query_handler(lambda c: c.data == 'Russian')
async def process_callback_button3(callback_query: types.CallbackQuery):
    dbM.update_user_lang(callback_query.from_user.id,'Russian')
    # print(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Хорошо, давайте продолжим. Какой у вас вопрос?')


@dp.callback_query_handler(lambda c: c.data == 'User')
async def process_callback_button4(callback_query: types.CallbackQuery):
    dbM.update_user_status(callback_query.from_user.id,'User')
    # print(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, "Status switched to: User")

@dp.callback_query_handler(lambda c: c.data == 'Vendor')
async def process_callback_button5(callback_query: types.CallbackQuery):
    dbM.update_user_status(callback_query.from_user.id,'Vendor')
    # print(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Status switched to: Vendor')

@dp.callback_query_handler(lambda c: c.data == 'Distributor')
async def process_callback_button6(callback_query: types.CallbackQuery):
    dbM.update_user_status(callback_query.from_user.id,'Distributor')
    # print(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Status switched to: Distributor')


@dp.message_handler(commands=['lang'])
async def change_language(message: types.Message):
    '''Метод, переводит пользователя в состояние выбора языка, отправляет пользователю клавиатуру для выбора языка'''
    inline_btn_1 = InlineKeyboardButton('🇬🇧 English', callback_data='English')
    inline_btn_2 = InlineKeyboardButton('🇩🇪 German', callback_data='German')
    inline_btn_3 = InlineKeyboardButton('🇷🇺 Russian ', callback_data='Russian')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2, inline_btn_3)
    await bot.send_message(message.chat.id,"Choose language:", reply_markup=inline_kb1)

@dp.message_handler(commands=['status'])
async def change_language(message: types.Message):
    '''Метод, переводит пользователя в состояние выбора статуса, отправляет пользователю клавиатуру для выбора статуса'''
    inline_btn_4 = InlineKeyboardButton('User', callback_data='User')
    inline_btn_5 = InlineKeyboardButton('Vendor', callback_data='Vendor')
    inline_btn_6 = InlineKeyboardButton('Distributor', callback_data='Distributor')
    inline_kb2 = InlineKeyboardMarkup().add(inline_btn_4, inline_btn_5, inline_btn_6)
    await bot.send_message(message.chat.id,"Choose status:", reply_markup=inline_kb2)

@dp.message_handler()
async def get_question(message: types.Message):
    # print(message)
    global current_user
    current_user = dbM.get_user_from_id(message.chat.id)
    ans = classify_question(message.text, current_user.status)
    await bot.send_message(message.chat.id, ans)

if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
