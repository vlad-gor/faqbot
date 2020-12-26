# -*- coding: utf-8 -*-

import os
import logging
import logging.config

import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from dotenv import load_dotenv

from markup import *
from models import User
from db_manager import DB_manager
from analyzer import analyst

# Settings 
if not os.path.exists('logs'):os.makedirs('logs')
logging.config.fileConfig(fname = 'mylogger.conf', disable_existing_loggers=False)
log = logging.getLogger(__name__)

load_dotenv()
bot = Bot(token=os.getenv('TOKEN'))
# For example use simple MemoryStorage for Dispatcher.
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
loop = asyncio.get_event_loop()
dbM = DB_manager()
dbM.create_table(User)

# States
class Form(StatesGroup):
    name = State()
    email = State()
    question = State()

# 1. Начало общения с клиентом, выбор языка
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    '''Начало общения с клиентом - добавить в базу, запомнить выбор языка'''
    try:
        dbM.add_record(User, message)
        dbM.session.commit()
    except Exception as ex:
        # log.error(ex)
        dbM.session.rollback()
    greeting = "Hello!\nWelcome to the CityStore FAQ_Bot.\nChoose the language, please."
    await bot.send_message(message.chat.id, greeting, reply_markup=choose_lang_markup)

@dp.message_handler(commands=['lang'])
async def change_language(message: types.Message):
    await bot.send_message(message.chat.id,"Choose language:", reply_markup=choose_lang_markup)

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

@dp.message_handler()
async def get_question(message: types.Message):
    '''Находит ответ на вопрос и уточняет помогло ли решение'''
    lg = dbM.get_user_from_id(message.chat.id).lang
    # ans = analyst.classify_question_morphy(message, lg)
    ans = analyst.classify_question_spacy(message, lg)
    await bot.send_message(message.chat.id, ans)
    await bot.send_message(message.chat.id,resolved[lg], reply_markup=YesNo1[lg])

@dp.callback_query_handler(lambda c: c.data == 'Yes')
async def process_callback_yes(callback_query: types.CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Thank you for your request. We will be glad to see you soon.')

@dp.callback_query_handler(lambda c: c.data == 'No')
async def process_callback_no(callback_query: types.CallbackQuery):
    '''Если нет предлагается форма заполнения на английском'''
    form_yn = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Заполнить', callback_data='fill_form'),
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
    form_yn = InlineKeyboardMarkup().add(
        InlineKeyboardButton('Заполнить', callback_data='fill_form'),
        InlineKeyboardButton('Отказаться', callback_data='dt_form_no')) # если нет, ничего не происходит
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.from_user.id, 'Senden Sie Ihre Anfrage an support@citystore.world. Wir werden Ihr Problem lösen.')
    await bot.send_message(callback_query.from_user.id, 'Вы хотите отправить письмо отсюда? Заполните форму!(немецкий)', reply_markup=form_yn)

######################### Email Form ###########################

@dp.callback_query_handler(lambda c: c.data == 'fill_form')
async def process_callback_en_form_yes(callback_query: types.CallbackQuery):
    current_user = dbM.get_user_from_id(callback_query.from_user.id)
    await bot.answer_callback_query(callback_query.id)
    await Form.name.set()
    if current_user.lang == 'English':
        await bot.send_message(callback_query.from_user.id,"Как вас зовут:")
    elif current_user.lang == 'German':
        await bot.send_message(callback_query.from_user.id,"Как вас зовут:(немецкий)")

@dp.message_handler(state=Form.name)
async def process_name(message: types.Message, state: FSMContext):
    current_user = dbM.get_user_from_id(message.chat.id)
    async with state.proxy() as data:
        data['name'] = message.text
    await Form.next()
    if current_user.lang == 'English':
        await bot.send_message(message.chat.id,"Ваш email:")
    elif current_user.lang == 'German':
        await bot.send_message(message.chat.id,"Ваш email:(немецкий)")

@dp.message_handler(state=Form.email)
async def process_mail(message: types.Message, state: FSMContext):
    current_user = dbM.get_user_from_id(message.chat.id)
    async with state.proxy() as data:
        data['email'] = message.text
    await Form.next()
    if current_user.lang == 'English':
        await bot.send_message(message.chat.id,"Ваш вопрос:")
    elif current_user.lang == 'German':
        await bot.send_message(message.chat.id,"Ваш вопрос:(немецкий)")

@dp.message_handler(state=Form.question)
async def process_question(message: types.Message, state: FSMContext):
    current_user = dbM.get_user_from_id(message.chat.id)
    async with state.proxy() as data:
        data['question'] = message.text   
    if current_user.lang == 'English':
        await bot.send_message(message.chat.id,
        f'Ваше письмо отправлено.\nName: {data["name"]}\nEmail: {data["email"]}\nQuestion: {data["question"]}')
    elif current_user.lang == 'German':
        await bot.send_message(message.chat.id,
        f'Ваше письмо отправлено.(немецкий)\nName: {data["name"]}\nEmail: {data["email"]}\nQuestion: {data["question"]}')
    # Finish conversation
    await state.finish()

#######################################################################

if __name__ == '__main__':
    executor.start_polling(dp, loop=loop, skip_updates=True)
