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

import ex_reader
from ex_reader import Question_List
questions = Question_List()

# for q in questions.ql:
#     print(q.en())

token = os.getenv('TOKEN')
bot = Bot(token=token)
dp = Dispatcher(bot)

loop = asyncio.get_event_loop()

dbM = DB_manager()
dbM.create_table(User)

morph = pymorphy2.MorphAnalyzer()



# 1. Начало общения с клиентом, выбор языка
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    '''Начало общения с клиентом - добавить в базу, запомнить выбор языка'''
    try:
        dbM.add_record(User, message)
        dbM.session.commit()
    except Exception as ex:
        print(ex)
        dbM.session.rollback()
    inline_btn_1 = InlineKeyboardButton('🇬🇧 English', callback_data='English')
    inline_btn_2 = InlineKeyboardButton('🇩🇪 German', callback_data='German')
    # inline_btn_3 = InlineKeyboardButton('🇷🇺 Russian ', callback_data='Russian')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
    greeting = "Hello!\nWelcome to the CityStore FAQ_Bot.\nChoose the language, please."
    await bot.send_message(message.chat.id, greeting, reply_markup=inline_kb1)

#2. После выбора языка - вывести клавиатуру с выбором категории вопроса
@dp.callback_query_handler(lambda c: c.data == 'English')
async def process_callback_button1(callback_query: types.CallbackQuery):
    dbM.update_user_lang(callback_query.from_user.id,'English')
    print(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,"All right, let's continue. What is your question?")

@dp.callback_query_handler(lambda c: c.data == 'German')
async def process_callback_button2(callback_query: types.CallbackQuery):
    dbM.update_user_lang(callback_query.from_user.id,'German')
    print(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Okay, lass uns weitermachen. Welche Frage haben Sie?')

# @dp.callback_query_handler(lambda c: c.data == 'Russian')
# async def process_callback_button3(callback_query: types.CallbackQuery):
#     dbM.update_user_lang(callback_query.from_user.id,'Russian')
#     print(dbM.get_user_from_id(callback_query.from_user.id))
#     await bot.answer_callback_query(callback_query.id)
#     await bot.send_message(callback_query.from_user.id, 'Хорошо, давайте продолжим. Какой у вас вопрос?')

@dp.message_handler(commands=['lang'])
async def change_language(message: types.Message):
    '''Метод, переводит пользователя в состояние выбора языка, отправляет пользователю клавиатуру для выбора языка'''
    inline_btn_1 = InlineKeyboardButton('🇬🇧 English', callback_data='English')
    inline_btn_2 = InlineKeyboardButton('🇩🇪 German', callback_data='German')
    # inline_btn_3 = InlineKeyboardButton('🇷🇺 Russian ', callback_data='Russian')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
    await bot.send_message(message.chat.id,"Choose language:", reply_markup=inline_kb1)

@dp.message_handler()
async def get_question(message: types.Message):
    '''Находит ответ на вопрос и уточняет помогло ли решение'''
    ans = classify_question(message)
    await bot.send_message(message.chat.id, ans)
    inline_btn_1 = InlineKeyboardButton('Yes', callback_data='Yes')
    inline_btn_2 = InlineKeyboardButton('No', callback_data='No')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
    await bot.send_message(message.chat.id,"Have we resolved your problem?", reply_markup=inline_kb1)

@dp.callback_query_handler(lambda c: c.data == 'Yes')
async def process_callback_yes(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Thank you for your request. We will be glad to see you soon.')

@dp.callback_query_handler(lambda c: c.data == 'No')
async def process_callback_yes(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Send you request to email support@citystore.world. We’ll solve your problem.')    

def classify_question(message):
    '''Функция поиска ответа на вопрос'''
    current_user = dbM.get_user_from_id(message.chat.id)
    text = ' '.join(morph.parse(word)[0].normal_form for word in message.text.split())
    scores = list()
    print(text)
    if current_user.lang == 'English':
        for quest in questions.ql:
            norm_question = ' '.join(morph.parse(word)[0].normal_form for word in quest.en().split('|')[1].strip().split())
            scores.append(fuzz.token_sort_ratio(norm_question.lower(), text.lower()))
        print(scores)
        answer = str(questions.ql[scores.index(max(scores))].en()).split('|')[2].strip()
    elif current_user.lang == 'German':
        for quest in questions.ql:
            norm_question = ' '.join(morph.parse(word)[0].normal_form for word in quest.dt().split('|')[1].strip().split())
            scores.append(fuzz.token_sort_ratio(norm_question.lower(), text.lower()))
        print(scores)
        answer = str(questions.ql[scores.index(max(scores))].dt()).split('|')[2].strip()
    elif current_user.lang == 'Russian':
        for quest in questions.ql:
            norm_question = ' '.join(morph.parse(word)[0].normal_form for word in quest.ru().split('|')[1].strip().split())
            scores.append(fuzz.token_sort_ratio(norm_question.lower(), text.lower()))
        print(scores)
        answer = str(questions.ql[scores.index(max(scores))].ru()).split('|')[2].strip()

    return answer


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
