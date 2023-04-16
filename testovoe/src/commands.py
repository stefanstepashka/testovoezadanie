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
from aiogram.dispatcher.filters import Text
from typing import Union

from states import QuantityState
from aiogram.dispatcher.filters.state import State, StatesGroup
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testovoe.settings")

import django
django.setup()




category_cd = CallbackData("category", "category_id", "action")
pagination_cd = CallbackData("pagination", "subcategory_id", "page")

subcategory_cd = CallbackData("subcategory", "subcategory_id", "action")
product_cd = CallbackData("product", "subcategory_id", "action", "product_id", "page")
checkout_cd = CallbackData("checkout", "user_id")



async def get_categories(page=1):
    return await api(f'categories/?page={page}')

async def get_subcategories(category_id):
    response = await api("subcategories/", {"category": category_id})
    subcategories = response["results"]
    return subcategories


async def has_next_page(subcategory_id, current_page, items_per_page=3):
    next_page_products = await get_products(subcategory_id, current_page + 1, items_per_page)
    print(f"Next page products: {next_page_products}")
    return next_page_products is not None and len(next_page_products) > 0


async def get_product_by_id(product_id):
    return await api(f'products/{product_id}/')

async def get_products(subcategory_id, page=1, items_per_page=3):
    response = await api(f'products/?subcategory={subcategory_id}&page={page}&limit={items_per_page}')
    print(f"API response: {response}")
    if 'results' in response:
        return response['results']
    elif 'detail' in response and response['detail'] == 'Invalid page.':
        return None
    else:
        return []
async def get_product(subcategory_id, page=1, items_per_page=3):
    response = await api(f'products/?subcategory={subcategory_id}&page={page}&limit={items_per_page}')
    return response['results']


async def is_user_in_channel(user_id: int, chat_id: str) -> bool:
    try:
        member_status = await bot.get_chat_member(chat_id=chat_id, user_id=user_id)
        return member_status.is_chat_member() or member_status.is_chat_administrator()

    except:
        return True




@dp.message_handler(Command("start"))
async def start_command_handler(message: types.Message):
    user_id = message.from_user.id
    channel_username = 5017748209
    is_member = await is_user_in_channel(user_id, channel_username)
    chat_id = message.chat.id
    print(chat_id)
    print(f"User {user_id} status: {is_member}")
    if is_member:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("Каталог", callback_data="catalog"),
            InlineKeyboardButton("Корзина", callback_data="cart"),
            InlineKeyboardButton("FAQ", switch_inline_query_current_chat="")
        )
        await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard)
    else:
        await message.answer(f"Пожалуйста, подпишитесь на канал {channel_username}, чтобы получить доступ к боту.")


@dp.callback_query_handler(category_cd.filter(action="show_subcategories"))
async def show_subcategories(query: types.CallbackQuery, callback_data: dict):
    category_id = int(callback_data["category_id"])
    action = callback_data["action"]

    subcategories = await get_subcategories(category_id)
    if not subcategories:
        await query.message.answer(f"Нет подкатегорий.")
        return

    keyboard = InlineKeyboardMarkup(row_width=2)

    print(callback_data)
    for subcategory in subcategories:
        keyboard.add(InlineKeyboardButton(subcategory["name"],
                                          callback_data=subcategory_cd.new(subcategory_id=subcategory["id"],
                                                                           action="show_products")))  # Removed page=1

    await query.message.answer("Выберите подкатегорию:", reply_markup=keyboard)


async def get_prev_and_next_product_ids(subcategory_id, current_product_id):
    products = await get_products(subcategory_id)
    prev_id, next_id = None, None

    for i, product in enumerate(products):
        if product["id"] == current_product_id:
            if i > 0:
                prev_id = products[i - 1]["id"]
            if i < len(products) - 1:
                next_id = products[i + 1]["id"]
            break

    return prev_id, next_id


from data_fetcher import resize_image
@dp.callback_query_handler(subcategory_cd.filter(action="show_products"))
async def show_products(chat: Union[types.CallbackQuery, types.Message], callback_data: dict):
    subcategory_id = int(callback_data["subcategory_id"])
    action = callback_data["action"]

    page = int(callback_data.get("page", 1))

    products = await get_products(subcategory_id, page)
    if not products:
        await chat.message.answer("Нет продуктов в этой подкатегории.")
        return


    for product in products:
        product_caption = f"{product['name']}\n\n{product['description']}\n\n"
        keyboard = InlineKeyboardMarkup()
        add_to_cart_button = InlineKeyboardButton("Добавить в корзину",
                                                  callback_data=product_cd.new(subcategory_id=subcategory_id,
                                                                               action="add_to_cart",
                                                                               product_id=product["id"],
                                                                               page=page))
        keyboard.row(add_to_cart_button)

        nav_buttons = []
        if page > 1:
            nav_buttons.append(InlineKeyboardButton("Previous", callback_data=product_cd.new(subcategory_id=subcategory_id,
                                                                                            action="show_products",
                                                                                            product_id=0,
                                                                                            page=page - 1)))
        if await has_next_page(subcategory_id, page, items_per_page=3):
            nav_buttons.append(InlineKeyboardButton("Next", callback_data=product_cd.new(subcategory_id=subcategory_id,
                                                                                        action="show_products",
                                                                                        product_id=0,
                                                                                        page=page + 1)))

        keyboard.row(*nav_buttons)


        resized_image = await resize_image(product['image'])

        if isinstance(chat, types.CallbackQuery):
            await chat.message.answer_photo(photo=resized_image, caption=product_caption, reply_markup=keyboard)
            await chat.answer()
        else:
            await chat.answer_photo(photo=resized_image, caption=product_caption, reply_markup=keyboard)
async def send_product(chat, product, subcategory_id, page, keyboard):
    product_caption = f"{product['name']}\n\n{product['description']}\n\n"
    resized_image = await resize_image(product['image'])
    if isinstance(chat, types.CallbackQuery):
        await chat.message.answer_photo(photo=resized_image, caption=product_caption, reply_markup=keyboard)
        await chat.answer()
    else:
        await chat.answer_photo(photo=resized_image, caption=product_caption, reply_markup=keyboard)






@dp.callback_query_handler(subcategory_cd.filter(action="show_products"))
async def show_products_handler(chat: Union[types.CallbackQuery, types.Message], callback_data: dict):
    print("show_products_handler called")
    await show_products(chat, callback_data)
@dp.callback_query_handler(product_cd.filter(action="show_products"))
async def show_products_pagination(chat: types.CallbackQuery, callback_data: dict):
    subcategory_id = int(callback_data["subcategory_id"])
    page = int(callback_data.get("page", 1))
    await show_products(chat, {"subcategory_id": subcategory_id, "action": "show_products", "page": page})

#Категории

@dp.callback_query_handler(text="catalog")
async def catalog_callback_handler(query: types.CallbackQuery, state: FSMContext):
    await state.update_data(current_page=1)
    categories_data = await get_categories()
    categories = categories_data["results"]
    keyboard = InlineKeyboardMarkup()
    if not categories:
        await query.message.answer("Категории отсутствуют.")
        return
    for category in categories:
        keyboard.add(InlineKeyboardButton(category["name"],
        callback_data=category_cd.new(category_id=category["id"], action="show_subcategories")))

    if categories_data["previous"]:
        keyboard.add(
            InlineKeyboardButton("⬅️ Назад", callback_data=pagination_cd.new(subcategory_id="catalog", page="prev")))
    if categories_data["next"]:
        keyboard.add(
            InlineKeyboardButton("Вперед ➡️", callback_data=pagination_cd.new(subcategory_id="catalog", page="next")))

    await query.message.answer("Выберите категорию:", reply_markup=keyboard)











#Пагинация для категорий
@dp.callback_query_handler(pagination_cd.filter(subcategory_id="catalog", page="prev"))
async def prev_page_callback_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    data = await state.get_data()
    current_page = data.get("current_page", 1)

    current_page -= 1
    await state.update_data(current_page=current_page)

    categories_data = await get_categories(page=current_page)
    categories = categories_data["results"]

    keyboard = InlineKeyboardMarkup()

    for category in categories:
        keyboard.add(InlineKeyboardButton(category["name"],
        callback_data=category_cd.new(category_id=category["id"], action="show_subcategories")))

    if categories_data["previous"]:
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data=pagination_cd.new(subcategory_id="catalog", page="prev")))
    if categories_data["next"]:
        keyboard.add(InlineKeyboardButton("Вперед ➡️", callback_data=pagination_cd.new(subcategory_id="catalog", page="next")))

    await query.message.edit_text("Выберите категорию:", reply_markup=keyboard)


@dp.callback_query_handler(pagination_cd.filter(subcategory_id="catalog", page="next"))
async def next_page_callback_handler(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    user_data = await state.get_data()
    current_page = user_data.get("current_page", 1)

    new_page = current_page + 1
    await state.update_data(current_page=new_page)

    categories_data = await get_categories(page=new_page)
    categories = categories_data["results"]

    keyboard = InlineKeyboardMarkup()

    for category in categories:
        keyboard.add(InlineKeyboardButton(category["name"],
        callback_data=category_cd.new(category_id=category["id"], action="show_subcategories")))

    if categories_data["previous"]:
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data=pagination_cd.new(subcategory_id="catalog", page="prev")))
    if categories_data["next"]:
        keyboard.add(InlineKeyboardButton("Вперед ➡️", callback_data=pagination_cd.new(subcategory_id="catalog", page="next")))

    await query.message.edit_text("Выберите категорию:", reply_markup=keyboard)

from channels.db import database_sync_to_async


@dp.callback_query_handler(product_cd.filter(action="add_to_cart"))
async def add_to_cart(query: types.CallbackQuery, callback_data: dict, state: FSMContext):
    product_id = int(callback_data["product_id"])
    subcategory_id = int(callback_data["subcategory_id"])
    page = int(callback_data.get("page", 1))

    async with state.proxy() as data:
        data['product_id'] = product_id
        data['subcategory_id'] = subcategory_id
        data['page'] = page

    await query.answer("Напишите количество")
    await QuantityState.waiting_for_quantity.set()
