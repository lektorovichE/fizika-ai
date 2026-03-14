from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_user, get_analyses, delete_user, get_stats, update_user
from config import ADMIN_CHAT_ID
from datetime import datetime

async def handle_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data == "menu_analysis":
        await query.message.reply_text(
            "📸 *Анализ тела*\n\n"
            "Отправь фото в полный рост и я сделаю полный анализ:\n\n"
            "✅ Встань прямо, смотри вперёд\n"
            "✅ Хорошее освещение\n"
            "✅ Шорты или купальник\n"
            "✅ Нейтральный фон (стена, дверь)\n\n"
            "Готов? Отправляй фото! 👇",
            parse_mode="Markdown"
        )

    elif data == "menu_nutrition":
        db_user = await get_user(user_id)
        if not db_user or not db_user.get("onboarding_done"):
            await query.message.reply_text("Сначала пройди настройку — напиши /start")
            return
        await query.message.reply_text(
            "🍽️ *Персональный план питания*\n\n"
            "Отправь фото тела и я составлю план питания специально под тебя — с КБЖУ, примерами блюд и граммовкой.\n\n"
            "📸 Отправь фото прямо сейчас 👇",
            parse_mode="Markdown"
        )

    elif data == "menu_training":
        await query.message.reply_text(
            "💪 *Программа тренировок*\n\n"
            "Отправь фото тела и я составлю программу тренировок на 4 недели — под твой уровень и цель.\n\n"
            "📸 Отправь фото 👇",
            parse_mode="Markdown"
        )

    elif data == "menu_progress":
        analyses = await get_analyses(user_id)
        if not analyses:
            await query.message.reply_text(
                "📊 *Мой прогресс*\n\n"
                "Пока нет данных. Сделай первый анализ!\n\n"
                "📸 Отправь фото 👇",
                parse_mode="Markdown"
            )
            return

        first = analyses[-1]
        last = analyses[0]
        first_date = first["created_at"][:10]
        last_date = last["created_at"][:10]

        text = f"📊 *Твой прогресс*\n\nВсего анализов: {len(analyses)}\n\n"
        if len(analyses) > 1:
            text += f"📅 *Первый анализ* ({first_date}):\n{first['body_fat_range']}\n{first['body_type']}\n\n"
            text += f"📅 *Последний анализ* ({last_date}):\n{last['body_fat_range']}\n{last['body_type']}\n\n"
        else:
            text += f"📅 *Анализ* ({first_date}):\n{first['body_fat_range']}\n{first['body_type']}\n\n"
            text += "_Делай анализы каждую неделю — здесь будет видна динамика!_"

        await query.message.reply_text(text, parse_mode="Markdown")

    elif data == "menu_settings":
        db_user = await get_user(user_id)
        status = db_user.get("subscription_status", "free") if db_user else "free"
        end_date = db_user.get("subscription_end_date", "") if db_user else ""
        end_str = end_date[:10] if end_date else "—"

        keyboard = [
            [InlineKeyboardButton("⚖️ Изменить вес", callback_data="set_weight")],
            [InlineKeyboardButton("📏 Изменить рост", callback_data="set_height")],
            [InlineKeyboardButton("🎯 Изменить цель", callback_data="set_goal")],
            [InlineKeyboardButton("🗑️ Удалить аккаунт", callback_data="delete_account")],
        ]
        sub_text = "✅ Активна" if status == "active" else "❌ Не активна"
        await query.message.reply_text(
            f"⚙️ *Настройки*\n\n"
            f"💎 Подписка: {sub_text}\n"
            f"📅 До: {end_str}\n\n"
            f"Вес: {db_user.get('weight', '—')} кг\n"
            f"Рост: {db_user.get('height', '—')} см",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu_support":
        keyboard = [
            [InlineKeyboardButton("📊 Точность анализа?", callback_data="faq_accuracy")],
            [InlineKeyboardButton("❌ Как отменить подписку?", callback_data="faq_cancel")],
            [InlineKeyboardButton("📸 Фото не анализируется", callback_data="faq_photo")],
            [InlineKeyboardButton("💰 Возврат средств", callback_data="faq_refund")],
            [InlineKeyboardButton("✍️ Написать в поддержку", callback_data="contact_support")],
        ]
        await query.message.reply_text(
            "❓ *Поддержка FizAI*\n\nВыбери вопрос или напиши нам:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "menu_about":
        await query.message.reply_text(
            "ℹ️ *О сервисе FizAI*\n\n"
            "FizAI — AI-тренер нового поколения.\n\n"
            "Просто пришли фото тела — и получи:\n"
            "• Анализ жировой массы\n"
            "• Тип телосложения\n"
            "• Персональный план питания\n"
            "• Программу тренировок на 4 недели\n\n"
            "💎 Premium: 599₽/мес\n\n"
            "По вопросам: /support\n"
            "Политика конфиденциальности: /privacy",
            parse_mode="Markdown"
        )

    elif data == "faq_accuracy":
        await query.message.reply_text(
            "📊 *Точность анализа*\n\n"
            "FizAI даёт приблизительную визуальную оценку с погрешностью ±5%.\n\n"
            "Для точных измерений используй:\n"
            "• Калипер (специальный прибор)\n"
            "• Биоимпедансный анализ в клинике\n\n"
            "Наш анализ — отличный старт чтобы понять свою форму и получить план действий!",
            parse_mode="Markdown"
        )

    elif data == "faq_cancel":
        await query.message.reply_text(
            "❌ *Отмена подписки*\n\n"
            "Напиши нам в поддержку и мы отменим подписку в течение 24 часов.\n\n"
            "Контакт: @fizai_support",
            parse_mode="Markdown"
        )

    elif data == "faq_photo":
        await query.message.reply_text(
            "📸 *Если фото не анализируется:*\n\n"
            "✅ Сделай фото в полный рост\n"
            "✅ Хорошее освещение (не против света)\n"
            "✅ Нейтральный фон (стена, дверь)\n"
            "✅ Шорты или купальник\n"
            "✅ Файл не меньше 500кб\n\n"
            "Попробуй снова! 👇",
            parse_mode="Markdown"
        )

    elif data == "faq_refund":
        await query.message.reply_text(
            "💰 *Возврат средств*\n\n"
            "Мы возвращаем деньги в течение 14 дней с момента оплаты если сервис не работал.\n\n"
            "Напиши нам: @fizai_support",
            parse_mode="Markdown"
        )

    elif data == "contact_support":
        context.user_data["waiting_support"] = True
        await query.message.reply_text(
            "✍️ Напиши свой вопрос и мы ответим в течение 24 часов:"
        )

    elif data == "delete_account":
        keyboard = [
            [InlineKeyboardButton("✅ Да, удалить", callback_data="confirm_delete")],
            [InlineKeyboardButton("❌ Нет, отмена", callback_data="menu_settings")],
        ]
        await query.message.reply_text(
            "⚠️ *Удалить аккаунт?*\n\n"
            "Все твои данные и история анализов будут удалены безвозвратно.",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "confirm_delete":
        await delete_user(user_id)
        await query.message.reply_text(
            "✅ Все твои данные удалены.\n\n"
            "Если захочешь вернуться — напиши /start"
        )

    elif data == "new_scan":
        await query.message.reply_text("Отправляй новое фото 📸")

    elif data == "share_result":
        result = context.user_data.get("last_result", "")
        if result:
            share_text = f"Мой анализ тела от FizAI 🤖\n\n{result[:500]}...\n\nПопробуй сам: @FizAI_bot"
            await query.message.reply_text(
                f"📤 *Скопируй и поделись:*\n\n`{share_text}`",
                parse_mode="Markdown"
            )

    elif data == "subscribe":
        keyboard = [[InlineKeyboardButton("💳 Оплатить 599₽", callback_data="pay_now")]]
        await query.message.reply_text(
            "💎 *FizAI Premium — 599₽/мес*\n\n"
            "✅ Безлимитные анализы тела\n"
            "✅ Полный план питания с КБЖУ\n"
            "✅ Программа тренировок 4 недели\n"
            "✅ AI-тренер в чате 24/7\n"
            "✅ Еженедельный трекинг прогресса\n\n"
            "Нажми кнопку для оплаты:",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "pay_now":
        await query.message.reply_text(
            "💳 Для оплаты напиши в поддержку: @fizai_support\n\n"
            "_Скоро подключим автоматическую оплату через ЮКассу_",
            parse_mode="Markdown"
        )


async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Если ждём вопрос в поддержку
    if context.user_data.get("waiting_support"):
        context.user_data["waiting_support"] = False
        db_user = await get_user(user_id)
        name = db_user.get("first_name", "") if db_user else ""
        try:
            from config import ADMIN_CHAT_ID
            if ADMIN_CHAT_ID:
                await context.bot.send_message(
                    ADMIN_CHAT_ID,
                    f"🆘 Вопрос в поддержку\n"
                    f"От: {name} (@{update.effective_user.username})\n"
                    f"ID: {user_id}\n\n"
                    f"Вопрос: {update.message.text}"
                )
        except Exception:
            pass
        await update.message.reply_text(
            "✅ Вопрос отправлен! Ответим в течение 24 часов."
        )
        return

    await update.message.reply_text(
        "📸 Отправь фото тела и я сделаю анализ!\n\n"
        "Или /start чтобы вернуться в меню."
    )


async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_CHAT_ID:
        return
    stats = await get_stats()
    await update.message.reply_text(
        f"📊 *Статистика FizAI*\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"💎 Активных подписок: {stats['active_subs']}\n"
        f"📸 Всего анализов: {stats['total_analyses']}\n"
        f"💰 Выручка (est): {stats['active_subs'] * 599}₽/мес",
        parse_mode="Markdown"
    )
