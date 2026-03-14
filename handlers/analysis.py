from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user, create_user, save_analysis
from services.ai_service import analyze_body_photo
from config import FREE_LIMIT
import logging

logger = logging.getLogger(__name__)

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    db_user = await get_user(user_id)

    if not db_user:
        await create_user(user_id, update.effective_user.username or "", update.effective_user.first_name)
        db_user = await get_user(user_id)

    # Проверка лимита
    is_premium = db_user.get("subscription_status") == "active"
    used = db_user.get("free_analyses_used", 0)

    if not is_premium and used >= FREE_LIMIT:
        keyboard = [[InlineKeyboardButton("💎 Premium — 599₽/мес", callback_data="subscribe")]]
        await update.message.reply_text(
            "😔 *Бесплатный анализ уже использован.*\n\n"
            "Оформи *FizAI Premium* за 599₽/мес и получи:\n"
            "✅ Безлимитные анализы тела\n"
            "✅ Персональный план питания\n"
            "✅ Программу тренировок\n"
            "✅ AI-тренер 24/7\n"
            "✅ Еженедельный трекинг прогресса",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    # Предупреждение о конфиденциальности
    await update.message.reply_text(
        "🔒 *Конфиденциальность:*\n"
        "Фото обрабатывается только для анализа и не сохраняется на наших серверах.\n\n"
        "⏳ Анализирую... (15-20 сек)",
        parse_mode="Markdown"
    )

    try:
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        image_bytes = await file.download_as_bytearray()

        result = await analyze_body_photo(bytes(image_bytes), db_user)

        # Сохраняем результат
        body_fat = ""
        body_type = ""
        for line in result.split("\n"):
            if "жировой массы" in line.lower():
                body_fat = line
            if "телосложения" in line.lower():
                body_type = line

        await save_analysis(user_id, result, body_fat, body_type)

        db_user = await get_user(user_id)
        scans_left = FREE_LIMIT - db_user.get("free_analyses_used", 0)

        if not is_premium:
            footer = f"\n\n_Бесплатных анализов осталось: {max(0, scans_left)}_"
        else:
            footer = "\n\n_Premium активен ✅_"

        keyboard = []
        if not is_premium:
            keyboard.append([InlineKeyboardButton("💎 Premium — 599₽/мес", callback_data="subscribe")])
        keyboard.append([InlineKeyboardButton("📸 Новый анализ", callback_data="new_scan")])
        keyboard.append([InlineKeyboardButton("📊 Мой прогресс", callback_data="menu_progress")])
        keyboard.append([InlineKeyboardButton("📤 Поделиться результатом", callback_data="share_result")])

        # Сохраняем результат для шаринга
        context.user_data["last_result"] = result

        await update.message.reply_text(
            result + footer,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        logger.error(f"Ошибка анализа для {user_id}: {e}")
        await update.message.reply_text(
            "❌ Не удалось проанализировать фото.\n\n"
            "Попробуй:\n"
            "• Улучши освещение\n"
            "• Встань на нейтральный фон\n"
            "• Пришли фото в полный рост\n\n"
            "И попробуй снова 👇"
        )
