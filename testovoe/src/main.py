import sys
import os


project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'testovoe.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

import django
django.setup()

from aiogram import executor
import commands
from app import dp
import cart
import payments
import faq



if __name__ == '__main__':
    executor.start_polling(dp)