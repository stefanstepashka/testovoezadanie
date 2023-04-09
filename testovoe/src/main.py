from aiogram import executor
import commands
from app import dp
import cart
import payments
import faq

if __name__ == '__main__':
    executor.start_polling(dp)