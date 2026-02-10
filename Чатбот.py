# simple_ai_bot.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes
)
from groq import Groq
import logging

# Отключаем лишние логи
logging.getLogger("httpx").setLevel(logging.WARNING)

# 🔑 ТОКЕНЫ
TELEGRAM_TOKEN = "8500698089:AAGiQippPjuIjppiAMqlzAQBXPdNNibn1FE"
GROQ_API_KEY = "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"

# Инициализация Groq
groq_client = Groq(api_key=GROQ_API_KEY)

# Основное меню
def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💬 Задать вопрос", callback_data="text")],
        [InlineKeyboardButton("💻 Написать код", callback_data="code")],
        [InlineKeyboardButton("❓ Инструкции", callback_data="help")]
    ])

# Инструкция
HELP_TEXT = (
    "<b>🧠 Как пользоваться ботом</b>\n\n"
    "💬 <b>Задать вопрос</b>\n"
    "→ Нажми кнопку или просто напиши:\n"
    "«Как устроен мозг?»\n\n"
    
    "💻 <b>Написать код</b>\n"
    "→ Нажми кнопку или опиши задачу:\n"
    "«Функция на Python для сортировки списка»\n\n"
    
    "✨ Бот понимает русский язык и отвечает мгновенно!"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Привет! Я умный ИИ-помощник.\nВыберите, что хотите сделать:",
        reply_markup=get_menu()
    )

# Обработка нажатий на кнопки
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    action = query.data

    # Удаляем кнопки
    await query.edit_message_reply_markup(reply_markup=None)

    if action == "help":
        await query.message.reply_text(HELP_TEXT, parse_mode="HTML")
        await query.message.reply_text("Выберите действие:", reply_markup=get_menu())
    else:
        context.user_data["mode"] = action
        if action == "text":
            await query.message.reply_text("💬 Введите ваш вопрос:")
        elif action == "code":
            await query.message.reply_text("💻 Опишите задачу для кода:")

# Обработка сообщений
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Если есть активный режим (после нажатия кнопки)
    if "mode" in context.user_data:
        mode = context.user_data.pop("mode")
        user_text = update.message.text

        msg = await update.message.reply_text("🧠 Обрабатываю...")
        try:
            if mode == "code":
                system_prompt = (
                    "Ты эксперт-программист. Напиши чистый, рабочий код с пояснениями. "
                    "Укажи язык программирования. Отвечай только по делу."
                )
            else:  # mode == "text"
                system_prompt = (
                    "Ты умный, дружелюбный и полезный помощник. "
                    "Отвечай чётко, по делу и на русском языке."
                )

            chat = groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text}
                ],
                max_tokens=800
            )
            await msg.edit_text(chat.choices[0].message.content)
        except Exception as e:
            await msg.edit_text(f"❌ Ошибка: {str(e)}")
        return

    # Обычное сообщение (без выбора кнопки)
    if update.message.text and update.message.text.startswith("/"):
        if update.message.text == "/start":
            await start(update, context)
        else:
            await update.message.reply_text("❓ Неизвестная команда. Используйте /start.")
        return

    # Обычный чат
    msg = await update.message.reply_text("🧠 Думаю...")
    try:
        chat = groq_client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": update.message.text}],
            max_tokens=800
        )
        await msg.edit_text(chat.choices[0].message.content)
    except Exception as e:
        await msg.edit_text(f"❌ Ошибка: {str(e)}")

# Запуск
def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("✅ Бот запущен! Напишите /start")
    app.run_polling()

if __name__ == "__main__":
    main()