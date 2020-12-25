# -*- coding: utf-8 -*-

import os
import logging
import logging.config

import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import ReplyKeyboardRemove, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv

from models import User
from db_manager import DB_manager
from analyzer import analyst

# Settings 
if not os.path.exists('logs'):os.makedirs('logs')
logging.config.fileConfig(fname = 'mylogger.conf', disable_existing_loggers=False)
log = logging.getLogger(__name__)

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher(bot)
loop = asyncio.get_event_loop()
dbM = DB_manager()
dbM.create_table(User)

# 1. Начало общения с клиентом, выбор языка
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    '''Начало общения с клиентом - добавить в базу, запомнить выбор языка'''
    try:
        dbM.add_record(User, message)
        dbM.session.commit()
    except Exception as ex:
        log.error(ex)
        dbM.session.rollback()
    inline_btn_1 = InlineKeyboardButton('🇬🇧 English', callback_data='English')
    inline_btn_2 = InlineKeyboardButton('🇩🇪 German', callback_data='German')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
    greeting = "Hello!\nWelcome to the CityStore FAQ_Bot.\nChoose the language, please."
    await bot.send_message(message.chat.id, greeting, reply_markup=inline_kb1)

#2. После выбора языка - вывести клавиатуру с выбором категории вопроса
@dp.callback_query_handler(lambda c: c.data == 'English')
async def process_callback_button1(callback_query: types.CallbackQuery):
    dbM.update_user_lang(callback_query.from_user.id,'English')
    log.info(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,"All right, let's continue. What is your question?")

@dp.callback_query_handler(lambda c: c.data == 'German')
async def process_callback_button2(callback_query: types.CallbackQuery):
    dbM.update_user_lang(callback_query.from_user.id,'German')
    log.info(dbM.get_user_from_id(callback_query.from_user.id))
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Okay, lass uns weitermachen. Welche Frage haben Sie?')

@dp.message_handler(commands=['lang'])
async def change_language(message: types.Message):
    '''Метод, переводит пользователя в состояние выбора языка, отправляет пользователю клавиатуру для выбора языка'''
    inline_btn_1 = InlineKeyboardButton('🇬🇧 English', callback_data='English')
    inline_btn_2 = InlineKeyboardButton('🇩🇪 German', callback_data='German')
    inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
    await bot.send_message(message.chat.id,"Choose language:", reply_markup=inline_kb1)

@dp.message_handler()
async def get_question(message: types.Message):
    '''Находит ответ на вопрос и уточняет помогло ли решение'''
    current_user = dbM.get_user_from_id(message.chat.id)
    if current_user.lang == 'English':
        ans = analyst.classify_question_morphy(message, current_user.lang)
        await bot.send_message(message.chat.id, ans)
        inline_btn_1 = InlineKeyboardButton('Yes', callback_data='Yes')
        inline_btn_2 = InlineKeyboardButton('No', callback_data='No')
        inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
        await bot.send_message(message.chat.id,"Have we resolved your problem?", reply_markup=inline_kb1)
    elif current_user.lang == 'German':
        ans = analyst.classify_question_morphy(message, current_user.lang)
        await bot.send_message(message.chat.id, ans)
        inline_btn_1 = InlineKeyboardButton('Ja', callback_data='Ja')
        inline_btn_2 = InlineKeyboardButton('Nein', callback_data='Nein')
        inline_kb1 = InlineKeyboardMarkup().add(inline_btn_1, inline_btn_2)
        await bot.send_message(message.chat.id,"Haben wir Ihr Problem gelöst?", reply_markup=inline_kb1)

@dp.callback_query_handler(lambda c: c.data == 'Yes')
async def process_callback_yes(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Thank you for your request. We will be glad to see you soon.')

@dp.callback_query_handler(lambda c: c.data == 'No')
async def process_callback_no(callback_query: types.CallbackQuery):
    '''Если нет предлагается форма заполнения на английском'''
    form_yn = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Заполнить', callback_data='en_form_yes'),
        InlineKeyboardButton('Отказаться', callback_data='en_form_no')) # если нет, ничего не происходит
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Send you request to email support@citystore.world. We’ll solve your problem.')
    await bot.send_message(callback_query.from_user.id, 'Вы хотите отправить письмо отсюда? Заполните форму!', reply_markup=form_yn)  

@dp.callback_query_handler(lambda c: c.data == 'Ja')
async def process_callback_yes(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Danke für ihre Anfrage. Wir freuen uns, Sie in naher Zukunft zu sehen.')

@dp.callback_query_handler(lambda c: c.data == 'Nein')
async def process_callback_no(callback_query: types.CallbackQuery):
    '''Если нет предлагается форма заполнения на немецком'''
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Senden Sie Ihre Anfrage an support@citystore.world. Wir werden Ihr Problem lösen.')

@dp.callback_query_handler(lambda c: c.data == 'en_form_yes')
async def process_callback_no(callback_query: types.CallbackQuery):
    '''Если нет предлагается форма заполнения на английском'''
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id,"Работает хендлер")


if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
