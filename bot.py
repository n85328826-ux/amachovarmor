import asyncio
import google.generativeai as genai
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# НАСТРОЙКИ — вставьте свои токены
# ==============================
TELEGRAM_TOKEN = "8854935248:AAFldkciTv21faskfdrflwsW-ESeswBL6jM"
GEMINI_API_KEY = "AQ.Ab8RN6Ji94Xfo4mEosZAFSJGv_Z3O5nINgQVwbtTIKhXlGZnww"

# ==============================
# ЧЕК-ЛИСТ
# ==============================
CHECKLIST = """
Ты — помощник мастера по оклейке телефонов защитными плёнками. 
Отвечай на вопросы клиентов вежливо, по делу, коротко (2-5 предложений).

ПРОДУКТЫ И ЦЕНЫ:
- Стандартная пленка: 1500 руб — защита от царапин, при падении может деформироваться
- Усиленная пленка (панцирь): 2500 руб — держит удар, экран не разбивается при падении на асфальт, держится дольше
- Оклейка задней крышки и боков (360°): дополнительная защита корпуса
- Защитные линзы на камеру: 1500 руб — защита выступающих камер
- Защитное стекло Remax: при наличии на модель

КЛЮЧЕВЫЕ АРГУМЕНТЫ:
- Плёнка делается 1 раз в 1–1.5 года
- Усиленная плёнка не трескается при ударах в отличие от стекла
- Чехол царапает телефон изнутри, плёнка держит корпус как новый
- Ремонт камеры от 5000 руб — выгоднее поставить линзы за 1500
- Экран — самое дорогое в телефоне

СТРАТЕГИЯ:
- Всегда вести к выбору: стандарт или усиленная?
- После экрана — предложи защиту корпуса 360°
- После 360° — предложи линзы на камеру
- Задавай вопросы: роняете телефон? даёте детям?

Отвечай только по теме оклейки телефонов.
"""

user_histories = {}

genai.configure(api_key=GEMINI_API_KEY)
gemini = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=CHECKLIST
)

async def ask_gemini(user_id: int, text: str) -> str:
    if user_id not in user_histories:
        user_histories[user_id] = gemini.start_chat(history=[])
    response = user_histories[user_id].send_message(text)
    return response.text

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Здравствуйте! Я помогу с вопросами по защите телефона.\n\n"
        "Спросите о видах плёнок, ценах или защите камер 😊"
    )

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply = await ask_gemini(update.effective_user.id, update.message.text)
        await update.message.reply_text(reply)
    except Exception as e:
        print(f"Ошибка: {e}")
        await update.message.reply_text("Извините, попробуйте ещё раз.")

def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
