from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
import google.generativeai as genai

# ==============================
# НАСТРОЙКИ — вставьте свои токены
# ==============================
TELEGRAM_TOKEN = "8854935248:AAFldkciTv21faskfdrflwsW-ESeswBL6jM"  # токен от @BotFather
GEMINI_API_KEY = "AQ.Ab8RN6Ji94Xfo4mEosZAFSJGv_Z3O5nINgQVwbtTIKhXlGZnww"        # ключ от aistudio.google.com

# ==============================
# ЧЕК-ЛИСТ (база знаний бота)
# ==============================
CHECKLIST = """
Ты — помощник мастера по оклейке телефонов защитными плёнками. 
Отвечай на вопросы клиентов вежливо, по делу, коротко (2-5 предложений).
Используй психологический подход из скрипта продаж.

ПРОДУКТЫ И ЦЕНЫ:
- Стандартная пленка: 1500 руб — защита от царапин, при падении может деформироваться
- Усиленная пленка (панцирь): 2500 руб — держит удар, экран не разбивается при падении на асфальт, усиленный клеевой состав, держится дольше
- Оклейка задней крышки и боков (360°): дополнительная защита корпуса
- Защитные линзы на камеру: 1500 руб — защита выступающих камер от трещин и царапин
- Защитное стекло Remax: при наличии на модель телефона

КЛЮЧЕВЫЕ АРГУМЕНТЫ:
- Плёнка делается 1 раз в 1–1.5 года, не нуждается в постоянной замене как стекло
- Усиленная плёнка не трескается при ударах в отличие от стекла
- Покрывает весь корпус, включая бока
- Чехол царапает телефон изнутри (пыль и песчинки), плёнка держит корпус как новый
- Ремонт камеры: от 5000 руб за линзу, ставят копию, телефон вскрывается → выгоднее поставить линзы за 1500
- Экран — самое дорогое в телефоне, его важно защитить

СТРАТЕГИЯ ОТВЕТОВ:
- Горячий клиент (уже клеил): предложи перейти на панцирь, упомяни скидку
- Холодный клиент (новый): сначала объясни что такое полиуретановая защита, потом сравни варианты
- Если просит стекло, а его нет: предложи плёнку как замену
- Всегда вести к выбору: "стандарт или усиленная?" — не к "да/нет"
- После согласия на экран — предложи защиту корпуса (360°)
- После согласия на 360° — предложи линзы на камеру

Не навязывай, но задавай уточняющие вопросы:
- "Вы роняете телефон?"
- "Даёте детям?"
- "Важно чтобы телефон выглядел как новый?"

Отвечай только по теме оклейки телефонов. На посторонние вопросы вежливо скажи что специализируешься только на защите телефонов.
"""

# ==============================
# ХРАНЕНИЕ ИСТОРИИ ДИАЛОГОВ
# ==============================
user_histories = {}

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=CHECKLIST
)

async def ask_gemini(user_id: int, user_message: str) -> str:
    """Отправляет сообщение в Gemini и возвращает ответ"""

    # Инициализируем историю для нового пользователя
    if user_id not in user_histories:
        user_histories[user_id] = model.start_chat(history=[])

    chat = user_histories[user_id]
    response = chat.send_message(user_message)
    return response.text


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик входящих сообщений"""
    user_id = update.effective_user.id
    user_text = update.message.text

    await context.bot.send_chat_action(
        chat_id=update.effective_chat.id,
        action="typing"
    )

    try:
        reply = await ask_gemini(user_id, user_text)
        await update.message.reply_text(reply)
    except Exception as e:
        await update.message.reply_text(
            "Извините, произошла ошибка. Попробуйте ещё раз или обратитесь к мастеру напрямую."
        )
        print(f"Ошибка: {e}")


async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Приветственное сообщение"""
    await update.message.reply_text(
        "👋 Здравствуйте! Я помогу вам с вопросами по защите телефона.\n\n"
        "Спросите меня о:\n"
        "• Видах защитных плёнок\n"
        "• Ценах и отличиях\n"
        "• Защите камер и корпуса\n\n"
        "Чем могу помочь? 😊"
    )


def main():
    """Запуск бота"""
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", handle_start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен! Нажмите Ctrl+C для остановки.")
    app.run_polling()


if __name__ == "__main__":
    main()
