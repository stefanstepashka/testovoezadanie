from aiogram.dispatcher.filters.state import State, StatesGroup

from aiogram.dispatcher.filters import Text
from aiogram.types import ParseMode
from aiogram.utils.markdown import hbold, hcode

from aiogram.contrib.middlewares.logging import LoggingMiddleware

from aiogram.dispatcher.filters import Command
from aiogram.dispatcher.filters.state import State, StatesGroup


class CheckoutStates(StatesGroup):
    entering_name = State()
    entering_phone = State()
    entering_other_info = State()


class CatalogState(StatesGroup):
    current_page = State()