from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Command, Text
from aiogram.types import Message, CallbackQuery
from aiogram.utils.callback_data import CallbackData
from data_fetcher import api
from main import dp
from aiogram import Bot, types
import os
remove_item_cd = CallbackData("remove_item", "cart_item_id")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "testovoe.settings")
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"
import django
django.setup()
checkout_cd = CallbackData("checkout", "user_id")
from channels.db import database_sync_to_async
from aiogram.dispatcher import FSMContext
from states import QuantityState
from aiogram.dispatcher.filters.state import State, StatesGroup
from testovoeapi.models import Cart, CartItem, Order

@database_sync_to_async
def get_cart_items(user_id):
    cart = Cart.objects.get(user_id=user_id)
    cart_items = CartItem.objects.filter(cart=cart)
    return cart_items

@database_sync_to_async
def remove_item_from_cart(cart_item_id):
    cart_item = CartItem.objects.get(id=cart_item_id)
    cart_item.delete()

async def show_cart(query: types.CallbackQuery):
    user_id = query.from_user.id
    cart_items = await get_cart_items(user_id)

    if not cart_items:
        await query.message.answer("Ваша корзина пуста.")
        return

    cart_text = "Ваша корзина:\n\n"
    keyboard = InlineKeyboardMarkup()

    for cart_item in cart_items:
        cart_text += f"{cart_item.product.name} (Количество: {cart_item.quantity})\n\n"
        remove_button = InlineKeyboardButton(f"Удалить {cart_item.product.name}", callback_data=remove_item_cd.new(cart_item_id=cart_item.id))
        keyboard.row(remove_button)


    checkout_button = InlineKeyboardButton("Оформить заказ", callback_data=checkout_cd.new(user_id=user_id))
    keyboard.row(checkout_button)

    await query.message.answer(text=cart_text, reply_markup=keyboard)

@dp.callback_query_handler(text="cart")
async def show_cart_handler(query: types.CallbackQuery):
    await show_cart(query)

@dp.callback_query_handler(remove_item_cd.filter())
async def remove_item(query: types.CallbackQuery, callback_data: dict):
    cart_item_id = int(callback_data["cart_item_id"])


    await remove_item_from_cart(cart_item_id)


    await query.answer(f"Item {cart_item_id} removed from your cart!")

    await show_cart(query)






@database_sync_to_async
def create_order(user_id):

    cart = Cart.objects.get(user_id=user_id)
    cart_items = CartItem.objects.filter(cart=cart)


    total_amount = sum(item.product.price * item.quantity for item in cart_items)


    order = Order(user_id=user_id, cart=cart, total_amount=total_amount, status="pending")
    order.save()

    return order.order_id, total_amount



@database_sync_to_async
def get_or_create_cart(user_id):
    cart, _ = Cart.objects.get_or_create(user_id=user_id)
    return cart

@database_sync_to_async
def add_product_to_cart_sync(cart, product_id, quantity=1):
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product_id=product_id)
    if not created:
        cart_item.quantity += quantity
    else:
        cart_item.quantity = quantity

    cart_item.save()


async def add_product_to_cart(cart, product_id, quantity=1):
    await add_product_to_cart_sync(cart, product_id, quantity)





from cart import show_cart
@dp.message_handler(lambda message: message.text.isdigit(), state=QuantityState.waiting_for_quantity)
async def process_quantity(message: types.Message, state: FSMContext):
    quantity = int(message.text)

    async with state.proxy() as data:
        product_id = data['product_id']
        subcategory_id = data['subcategory_id']
        page = data['page']

        cart = await get_or_create_cart(message.from_user.id)
        await add_product_to_cart(cart, product_id, quantity)

        await message.answer(f"Product {product_id} added to your cart with quantity {quantity}!")

        fake_query = types.CallbackQuery(id="0", from_user=message.from_user, chat_instance="0", message=message)
        fake_query.from_user = message.from_user  # Set the from_user attribute explicitly

        await show_cart(fake_query)
    await state.finish()