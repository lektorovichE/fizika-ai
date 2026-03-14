from telegram import Update
from telegram.ext import ContextTypes

PRIVACY_TEXT = """📄 *Политика конфиденциальности FizAI*

*Какие данные мы собираем:*
• Имя, возраст, вес, рост, цель — только для работы сервиса
• Telegram ID и username — для идентификации
• История анализов (текст) — для трекинга прогресса

*Фотографии:*
🔒 Фотографии НЕ сохраняются на наших серверах. Они передаются напрямую в OpenAI API для анализа и сразу удаляются.

*Передача данных третьим лицам:*
Мы передаём данные только:
• OpenAI — для анализа фото (только само фото, без личных данных)
• ЮКасса — для обработки платежей (только платёжная информация)

Мы НЕ продаём и НЕ передаём данные другим третьим лицам.

*Хранение данных:*
Данные хранятся до тех пор, пока ты пользуешься сервисом или пока не удалишь аккаунт.

*Удаление данных:*
Ты можешь удалить все свои данные командой /delete\_my\_data

*Контакт по вопросам персональных данных:*
@fizai_support"""

async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(PRIVACY_TEXT, parse_mode="Markdown")

async def delete_my_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = [
        [InlineKeyboardButton("✅ Да, удалить все данные", callback_data="confirm_delete")],
        [InlineKeyboardButton("❌ Отмена", callback_data="menu_settings")],
    ]
    await update.message.reply_text(
        "⚠️ *Удалить все данные?*\n\n"
        "Имя, возраст, вес, рост, история анализов — всё будет удалено безвозвратно.",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
