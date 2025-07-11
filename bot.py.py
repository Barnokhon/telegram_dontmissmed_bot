from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler
from datetime import time, timedelta, datetime

# Шаги диалога
NAME, TIMES, DAYS = range(3)

# Обработка /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Привет! Назови лекарство.")
    return NAME

async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["medicine"] = update.message.text
    await update.message.reply_text("Укажи время приёма (через запятую, например: 7:00, 13:00, 18:00)")
    return TIMES

async def get_times(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["times"] = [t.strip() for t in update.message.text.split(",")]
    await update.message.reply_text("Сколько дней напоминать?")
    return DAYS

async def get_days(update: Update, context: ContextTypes.DEFAULT_TYPE):
    days = int(update.message.text)
    medicine = context.user_data["medicine"]
    times = context.user_data["times"]
    user_id = update.message.chat_id

    # создаем задания
    for t in times:
        hour, minute = map(int, t.split(":"))
        for day in range(days):
            job_time = time(hour=hour, minute=minute)
            context.job_queue.run_once(
                send_reminder,
                when=timedelta(days=day, hours=hour - datetime.now().hour, minutes=minute - datetime.now().minute),
                chat_id=user_id,
                name=f"{medicine}_{t}_day{day}",
                data=medicine
            )

    await update.message.reply_text(f"Я напомню тебе о приёме {medicine} {len(times)} раз в день в течение {days} дней.")
    return ConversationHandler.END

async def send_reminder(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    await context.bot.send_message(chat_id=job.chat_id, text=f"🔔 Напоминание: пора принять {job.data} 💊")

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Окей, отменено.")
    return ConversationHandler.END

def main():
    TOKEN = "8038849070:AAHWj_SGKU3WKkI6eK4gc_8931f9yQrOmhI"
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            TIMES: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_times)],
            DAYS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_days)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)s

    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
