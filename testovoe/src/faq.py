import os

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.callback_data import CallbackData
from aiogram.utils.exceptions import BadRequest
from data_fetcher import api
from main import dp
from src.app import bot

import uuid
faq_list = [
    {
        'question': 'Как добавлять вещи в корзину?',
        'answer': 'Через бота.'
    },
    {
        'question': 'Как стать успешным?',
        'answer': 'Трудиться.'
    }
]



@dp.inline_handler()
async def faq_inline_query(inline_query: types.InlineQuery):
    query = inline_query.query.strip()

    # Создаем список с ответами в формате InlineQueryResultArticle
    results = []
    for faq in faq_list:
        # Проверяем, содержит ли вопрос запрос пользователя
        if query.lower() in faq['question'].lower():

            result = types.InlineQueryResultArticle(
                id=f"{inline_query.from_user.id}_{faq['question']}",
                title=faq['question'],
                input_message_content=types.InputTextMessageContent(message_text=faq['answer'])
            )
            results.append(result)

    # Отправляем ответы пользователю
    await inline_query.answer(results)