import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ==============================
# НАСТРОЙКИ — вставьте свои токены
# ==============================
TELEGRAM_TOKEN = "8854935248:AAFldkciTv21faskfdrflwsW-ESeswBL6jM"
OPENROUTER_API_KEY = "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"  # sk-or-...

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

async def ask_openrouter(user_id: int, text: str) -> str:
    if user_id not in user_histories:
        user_histories[user_id] = []

    user_histories[user_id].append({"role": "user", "content": text})

    if len(user_histories[user_id]) > 20:
        user_histories[user_id] = user_histories[user_id][-20:]

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "mistralai/mistral-7b-instruct:free",
                "messages": [
                    {"role": "system", "content": CHECKLIST},
                    *user_histories[user_id]
                ]
            }
        )
        data = response.json()
        reply = data["choices"][0]["message"]["content"]

    user_histories[user_id].append({"role": "assistant", "content": reply})
    return reply

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Здравствуйте! Я помогу с вопросами по защите телефона.\n\n"
        "Спросите о видах плёнок, ценах или защите камер 😊"
    )

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
    try:
        reply = await ask_openrouter(update.effective_user.id, update.message.text)
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
