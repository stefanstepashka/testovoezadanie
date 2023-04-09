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

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testovoe.settings")

import django
django.setup()

from testovoeapi.models import Cart, CartItem


category_cd = CallbackData("category", "category_id", "action")

subcategory_cd = CallbackData("subcategory", "subcategory_id", "action")
product_cd = CallbackData("product", "subcategory_id", "action", "product_id", "page")
checkout_cd = CallbackData("checkout", "user_id")



async def get_categories(page=1):
    return await api(f'categories/?page={page}')

async def get_subcategories(category_id):
    response = await api("subcategories/", {"category": category_id})
    subcategories = response["results"]
    return subcategories

async def has_next_page(subcategory_id, current_page):
    next_page_products = await get_products(subcategory_id, current_page + 1)
    return len(next_page_products) > 0


async def get_product_by_id(product_id):
    return await api(f'products/{product_id}/')

async def get_products(subcategory_id, page=1):

    return await api(f'products/?subcategory={subcategory_id}&page={page}')

async def get_product(subcategory_id, page=1):
    return await api(f'products/?subcategory={subcategory_id}&page={page}')


CHANNEL_ID = "@StefiOceanBot"

async def is_user_in_channel(user_id):
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ["creator", "administrator", "member"]
    except BadRequest:
        return True

@dp.message_handler(Command("start"))
async def start_command_handler(message: types.Message):
    user_id = message.from_user.id
    is_member = await is_user_in_channel(user_id)

    if is_member:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            InlineKeyboardButton("Каталог", callback_data="catalog"),
            InlineKeyboardButton("Корзина", callback_data="cart"),
            InlineKeyboardButton("FAQ", switch_inline_query_current_chat="faq ")
        )
        await message.answer("Добро пожаловать! Выберите действие:", reply_markup=keyboard)
    else:
        await message.answer("Пожалуйста, подпишитесь на канал @StefiOceanBot, чтобы получить доступ к боту.")


@dp.callback_query_handler(category_cd.filter(action="show_subcategories"))
async def show_subcategories(query: types.CallbackQuery, callback_data: dict):
    category_id = int(callback_data["category_id"])
    action = callback_data["action"]

    subcategories = await get_subcategories(category_id)
    if not subcategories:
        await query.message.answer("No subcategories in this category.")
        return

    keyboard = InlineKeyboardMarkup(row_width=2)
    print("In show_subcategories")
    print(callback_data)
    for subcategory in subcategories:
        keyboard.add(InlineKeyboardButton(subcategory["name"],
                                          callback_data=subcategory_cd.new(subcategory_id=subcategory["id"],
                                                                           action="show_products")))  # Removed page=1

    await query.message.answer("Select a subcategory:", reply_markup=keyboard)


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


@dp.callback_query_handler(subcategory_cd.filter(action="show_products"))
async def show_products(query: types.CallbackQuery, callback_data: dict):
    subcategory_id = int(callback_data["subcategory_id"])
    action = callback_data["action"]

    page = int(callback_data.get("page", 1))
    print(f"Subcategory ID: {subcategory_id}")
    # Fetch product data
    products = await get_products(subcategory_id, page)
    print(f"Products: {products}")
    if not products:
        await query.message.answer("No products in this subcategory.")
        return

    # Prepare product caption
    keyboard = InlineKeyboardMarkup()
    product_caption = f"Products in this subcategory (Page {page}):\n\n"
    for product in products:
        product_caption += f"{product['name']}\n{product['description']}\n\n"

        add_to_cart_button = InlineKeyboardButton(f"Add {product['name']} to cart",
                                                  callback_data=product_cd.new(subcategory_id=subcategory_id,
                                                                               action="add_to_cart",
                                                                               product_id=product["id"],
                                                                               page=page))
        keyboard.row(add_to_cart_button)


    nav_keyboard = InlineKeyboardMarkup()
    if page > 1:
        nav_keyboard.add(InlineKeyboardButton("Previous", callback_data=product_cd.new(subcategory_id=subcategory_id,
                                                                                       action="show_products",
                                                                                       product_id=0,
                                                                                       page=page - 1)))
    if await has_next_page(subcategory_id, page):
        nav_keyboard.add(InlineKeyboardButton("Next", callback_data=product_cd.new(subcategory_id=subcategory_id,
                                                                                   action="show_products",
                                                                                   product_id=0,
                                                                                   page=page + 1)))

    keyboard.row(*nav_keyboard.inline_keyboard[0])

    # Send product list with the navigation buttons
    await query.message.answer(text=product_caption, reply_markup=keyboard)


#Категории
@dp.callback_query_handler(text="catalog")
async def catalog_callback_handler(query: types.CallbackQuery, state: FSMContext):
    await state.update_data(current_page=1)
    categories_data = await get_categories()
    categories = categories_data["results"]
    keyboard = InlineKeyboardMarkup()

    for category in categories:
        keyboard.add(InlineKeyboardButton(category["name"],
        callback_data=category_cd.new(category_id=category["id"], action="show_subcategories")))

    if categories_data["previous"]:
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data="prev_page"))
    if categories_data["next"]:
        keyboard.add(InlineKeyboardButton("Вперед ➡️", callback_data="next_page"))

    await query.message.answer("Выберите категорию:", reply_markup=keyboard)











#Пагинация для категорий
@dp.callback_query_handler(text="prev_page")
async def prev_page_callback_handler(query: types.CallbackQuery, state: FSMContext):

    data = await state.get_data()
    current_page = data.get("current_page", 1)

    current_page -= 1
    await state.update_data(current_page=current_page)


    categories_data = await get_categories(page=current_page)
    categories = categories_data["results"]

    keyboard = InlineKeyboardMarkup()

    for category in categories:
        keyboard.add(InlineKeyboardButton(category["name"],
        callback_data=category_cd.new(category_id=category["id"], action="show")))

    if categories_data["previous"]:
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data="prev_page"))
    if categories_data["next"]:
        keyboard.add(InlineKeyboardButton("Вперед ➡️", callback_data="next_page"))

    await query.message.edit_text("Выберите категорию:", reply_markup=keyboard)



@dp.callback_query_handler(text="next_page")
async def next_page_callback_handler(query: types.CallbackQuery, state: FSMContext):

    user_data = await state.get_data()
    current_page = user_data.get("current_page", 1)


    new_page = current_page + 1
    await state.update_data(current_page=new_page)


    categories_data = await get_categories(page=new_page)
    categories = categories_data["results"]

    keyboard = InlineKeyboardMarkup()

    for category in categories:
        keyboard.add(InlineKeyboardButton(category["name"],
        callback_data=category_cd.new(category_id=category["id"], action="show")))


    if categories_data["previous"]:
        keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data="prev_page"))
    if categories_data["next"]:
        keyboard.add(InlineKeyboardButton("Вперед ➡️", callback_data="next_page"))

    await query.message.answer("Выберите категорию:", reply_markup=keyboard)

from channels.db import database_sync_to_async



@database_sync_to_async
def get_or_create_cart(user_id):
    cart, _ = Cart.objects.get_or_create(user_id=user_id)
    return cart

@database_sync_to_async
def add_product_to_cart_sync(cart, product_id, quantity=1):
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
    if not created:
        cart_item.quantity += quantity
        cart_item.save()


async def add_product_to_cart(cart, product_id, quantity=1):
    await add_product_to_cart_sync(cart, product_id, quantity)


@dp.callback_query_handler(product_cd.filter(action="add_to_cart"))
async def add_to_cart(query: types.CallbackQuery, callback_data: dict):
    product_id = int(callback_data["product_id"])
    subcategory_id = int(callback_data["subcategory_id"])
    page = int(callback_data.get("page", 1))

    cart = await get_or_create_cart(query.from_user.id)

    await add_product_to_cart(cart, product_id)


    await query.answer(f"Product {product_id} added to your cart!")


    await show_products(query, {
        "subcategory_id": subcategory_id,
        "action": "show_products",
        "page": page
    })