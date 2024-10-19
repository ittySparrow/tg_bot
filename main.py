import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import asyncio

# База данных для продуктов и чек-лист
product_list = []
checklist = []

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    print(f"Chat ID: {update.message.chat_id}")
    await update.message.reply_text('Привет! Введи продукт или список продуктов через запятую для добавления в чек-лист.')

# Обработка введенного текста (добавление продуктов)
async def add_products(update: Update, context: CallbackContext) -> None:
    global product_list, checklist
    products = update.message.text.split(',')
    new_products = []

    # Обработка каждого продукта
    for product in products:
        product = product.strip()
        if product and product not in product_list:
            product_list.append(product)
            checklist.append(product)
            new_products.append(product)

    if new_products:
        await update.message.reply_text(f"Добавлены продукты: {', '.join(new_products)}")
    else:
        await update.message.reply_text("Все продукты уже в списке или пустые.")

# Команда для показа текущего чек-листа
async def show_checklist(update: Update, context: CallbackContext) -> None:
    if checklist:
        await update.message.reply_text(f"Текущий чек-лист:\n{chr(10).join(checklist)}")
    else:
        await update.message.reply_text("Чек-лист пуст.")

# Команда для отправки списка продуктов мужу
async def send_to_husband(update: Update, context: CallbackContext) -> None:
    husband_chat_id = os.getenv("CHAT_ID")
    if checklist:
        await context.bot.send_message(chat_id=husband_chat_id, text=f"Список продуктов:\n{chr(10).join(checklist)}")
        await update.message.reply_text("Чек-лист отправлен.")
    else:
        await update.message.reply_text("Чек-лист пуст.")

# Основная функция запуска бота
async def run_bot() -> None:
    token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(token).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", show_checklist))
    application.add_handler(CommandHandler("send", send_to_husband))

    # Обработчик сообщений с продуктами
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, add_products))

    # Запуск бота
    await application.initialize()  # Инициализация бота
    await application.start()        # Запуск бота
    await application.updater.start_polling()  # Старт процесса polling

if __name__ == '__main__':
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    loop.run_until_complete(run_bot())
    loop.run_forever()
