from local_settings import API_KEY
import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage


logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_KEY)
dp = Dispatcher(bot, storage=MemoryStorage())