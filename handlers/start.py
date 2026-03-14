from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from database import get_user, create_user, update_user

# Состояния онбординга
ASK_NAME, ASK_AGE, ASK_WEIGHT, ASK_HEIGHT, ASK_GOAL, ASK_ACTIVITY = range(6)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await create_user(user.id, user.username or "", user.first_name)
    db_user = await get_user(user.id)

    if db_user and db_user.get("onboarding_done"):
        await show_main_menu(update, context)
        return ConversationHandler.END

    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я *FizAI* — твой личный AI-тренер и диетолог.\n\n"
        "📸 Пришли фото тела и я скажу:\n"
        "• Диапазон жировой массы\n"
        "• Тип телосложения\n"
        "• Персональный план питания\n"
        "• Программу тренировок на 4 недели\n\n"
        "Давай сначала познакомимся. *Как тебя зовут?*",
        parse_mode="Markdown"
    )
    return ASK_NAME

async def got_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["first_name"] = update.message.text.strip()
    await update.message.reply_text(
        f"Отлично, {context.user_data['first_name']}! 💪\n\n*Сколько тебе лет?*",
        parse_mode="Markdown"
    )
    return ASK_AGE

async def got_age(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        age = int(update.message.text.strip())
        if not 10 <= age <= 100:
            raise ValueError
        context.user_data["age"] = age
    except ValueError:
        await update.message.reply_text("Введи корректный возраст (например: 17)")
        return ASK_AGE

    await update.message.reply_text("*Твой вес в кг?* (например: 89)", parse_mode="Markdown")
    return ASK_WEIGHT

async def got_weight(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        weight = float(update.message.text.strip().replace(",", "."))
        if not 30 <= weight <= 300:
            raise ValueError
        context.user_data["weight"] = weight
    except ValueError:
        await update.message.reply_text("Введи корректный вес (например: 89)")
        return ASK_WEIGHT

    await update.message.reply_text("*Твой рост в см?* (например: 180)", parse_mode="Markdown")
    return ASK_HEIGHT

async def got_height(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        height = float(update.message.text.strip().replace(",", "."))
        if not 100 <= height <= 250:
            raise ValueError
        context.user_data["height"] = height
    except ValueError:
        await update.message.reply_text("Введи корректный рост (например: 180)")
        return ASK_HEIGHT

    keyboard = [
        [InlineKeyboardButton("🔥 Похудеть", callback_data="goal_lose")],
        [InlineKeyboardButton("💪 Набрать массу", callback_data="goal_gain")],
        [InlineKeyboardButton("✨ Рельеф", callback_data="goal_relief")],
        [InlineKeyboardButton("⚖️ Поддержание формы", callback_data="goal_maintain")],
    ]
    await update.message.reply_text(
        "*Какая твоя цель?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ASK_GOAL

async def got_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    goal = query.data.replace("goal_", "")
    context.user_data["goal"] = goal

    keyboard = [
        [InlineKeyboardButton("🪑 Сидячий (офис, мало движения)", callback_data="act_sedentary")],
        [InlineKeyboardButton("🚶 Умеренный (прогулки, редкий спорт)", callback_data="act_moderate")],
        [InlineKeyboardButton("🏃 Активный (спорт 3-4 раза/нед)", callback_data="act_active")],
        [InlineKeyboardButton("⚡ Очень активный (спорт каждый день)", callback_data="act_very_active")],
    ]
    await query.message.reply_text(
        "*Твой уровень активности?*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return ASK_ACTIVITY

async def got_activity(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    activity = query.data.replace("act_", "")
    user_id = query.from_user.id

    await update_user(
        user_id,
        first_name=context.user_data.get("first_name", query.from_user.first_name),
        age=context.user_data.get("age"),
        weight=context.user_data.get("weight"),
        height=context.user_data.get("height"),
        goal=context.user_data.get("goal"),
        activity_level=activity,
        onboarding_done=1
    )

    goal_map = {"lose": "похудеть", "gain": "набрать массу", "relief": "рельеф", "maintain": "поддержание формы"}
    goal_text = goal_map.get(context.user_data.get("goal", ""), "")

    await query.message.reply_text(
        f"✅ *Отлично! Данные сохранены:*\n\n"
        f"👤 Имя: {context.user_data.get('first_name')}\n"
        f"📅 Возраст: {context.user_data.get('age')} лет\n"
        f"⚖️ Вес: {context.user_data.get('weight')} кг\n"
        f"📏 Рост: {context.user_data.get('height')} см\n"
        f"🎯 Цель: {goal_text}\n\n"
        f"Теперь отправь фото тела и я сделаю полный анализ! 📸\n\n"
        f"🎁 *Первый анализ бесплатно*",
        parse_mode="Markdown"
    )
    await show_main_menu_message(query.message)
    return ConversationHandler.END

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await show_main_menu_message(update.message)

async def show_main_menu_message(message):
    keyboard = [
        [InlineKeyboardButton("📸 Анализ тела", callback_data="menu_analysis")],
        [InlineKeyboardButton("📋 Мой план питания", callback_data="menu_nutrition"),
         InlineKeyboardButton("💪 Тренировки", callback_data="menu_training")],
        [InlineKeyboardButton("📊 Мой прогресс", callback_data="menu_progress")],
        [InlineKeyboardButton("⚙️ Настройки", callback_data="menu_settings"),
         InlineKeyboardButton("❓ Поддержка", callback_data="menu_support")],
        [InlineKeyboardButton("📄 О сервисе", callback_data="menu_about")],
    ]
    await message.reply_text(
        "🏠 *Главное меню FizAI*\n\nВыбери что хочешь сделать:",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def get_onboarding_handler():
    return ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_name)],
            ASK_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_age)],
            ASK_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_weight)],
            ASK_HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, got_height)],
            ASK_GOAL: [CallbackQueryHandler(got_goal, pattern="^goal_")],
            ASK_ACTIVITY: [CallbackQueryHandler(got_activity, pattern="^act_")],
        },
        fallbacks=[CommandHandler("start", start)],
        allow_reentry=True
    )
