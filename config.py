import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "ВАШ_ТОКЕН")
PROXYAPI_KEY = os.getenv("PROXYAPI_KEY", "ВАШ_КЛЮЧ_PROXYAPI")
ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "0"))

YOOKASSA_SHOP_ID = os.getenv("YOOKASSA_SHOP_ID", "")
YOOKASSA_SECRET_KEY = os.getenv("YOOKASSA_SECRET_KEY", "")

FREE_LIMIT = 1
SUBSCRIPTION_PRICE = 599
SUBSCRIPTION_DAYS = 30

GOALS = {
    "lose": "похудеть",
    "gain": "набрать массу",
    "relief": "рельеф",
    "maintain": "поддержание формы"
}

ACTIVITY = {
    "sedentary": "сидячий",
    "moderate": "умеренный",
    "active": "активный",
    "very_active": "очень активный"
}
