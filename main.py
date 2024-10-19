import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext, CallbackQueryHandler
import asyncio

# База данных для продуктов и чек-лист
product_list = []
checklist = []
current_message_id = None  # ID текущего сообщения со списком

# Команда /start
async def start(update: Update, context: CallbackContext) -> None:
    await update.message.reply_text('Привет! Введи продукт или список продуктов для добавления в чек-лист.')

# Обновление или создание сообщения со списком
async def update_list_message(context: CallbackContext, chat_id: int) -> None:
    global current_message_id, checklist

    if checklist:
        text = "Список продуктов:\n" + '\n'.join(checklist)
    else:
        text = "Чек-лист пуст."

    if current_message_id:
        try:
            await context.bot.edit_message_text(text=text, chat_id=chat_id, message_id=current_message_id)
        except Exception:
            current_message_id = None

    if not current_message_id:
        message = await context.bot.send_message(chat_id=chat_id, text=text)
        current_message_id = message.message_id

# Обработка введенного текста (добавление продуктов)
async def add_products(update: Update, context: CallbackContext) -> None:
    global product_list, checklist
    products = update.message.text.split('\n')
    new_products = []

    for product in products:
        product = product.strip()
        if product and product not in product_list:
            product_list.append(product)
            checklist.append(product)
            new_products.append(product)

    await update_list_message(context, update.message.chat_id)

    # Удаляем сообщение с продуктами
    await update.message.delete()

# Команда для очищения списка
async def clear_list(update: Update, context: CallbackContext) -> None:
    global checklist
    checklist = []
    await update_list_message(context, update.message.chat_id)

    # Удаляем сообщение с командой
    await update.message.delete()


# Команда для удаления отдельного продукта с кнопками
async def remove_item(update: Update, context: CallbackContext) -> None:
    global checklist

    if not checklist:
        await update.message.reply_text("Список продуктов пуст.")
        return

    # Создаем кнопки для каждого продукта
    keyboard = [[InlineKeyboardButton(product, callback_data=product)] for product in checklist]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text("Выбери продукт для удаления:", reply_markup=reply_markup)

    # Удаляем сообщение с командой
    await update.message.delete()

    # Обработка нажатий на кнопки
async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    product_to_remove = query.data

    if product_to_remove in checklist:
        checklist.remove(product_to_remove)
        await query.edit_message_text(text=f"Удален пункт: {product_to_remove}")

    await update_list_message(context, query.message.chat_id)

# Основная функция запуска бота
async def run_bot() -> None:
    token = os.getenv("BOT_TOKEN")
    application = Application.builder().token(token).build()

    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("clear", clear_list))
    application.add_handler(CommandHandler("remove", remove_item))
    application.add_handler(CallbackQueryHandler(button))
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
