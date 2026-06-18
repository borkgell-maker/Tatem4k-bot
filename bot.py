import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8965750450:AAFFaTpPtnIu9Yi9z8Z7tHFMmNRknLflpPU"

PHOTO_MAIN = "tatem4k_logo.png"
PHOTO_ARCHIVE = "exclusive_builds.jpg"
ADMIN_PASSWORD = "zpxocivuby123A"
USERS_FILE = "users.txt"
BUYERS_FILE = "potential_buyers.txt"

def read_list(filename):
    if not os.path.exists(filename):
        return []
    with open(filename, "r", encoding="utf-8") as f:
        return [l for l in f.read().splitlines() if l.strip()]

def save_list(filename, items):
    with open(filename, "w", encoding="utf-8") as f:
        f.write("\n".join(items))

def add_user(user):
    username = f"@{user.username}" if user.username else f"id:{user.id}"
    users = read_list(USERS_FILE)
    if username not in users:
        users.append(username)
        save_list(USERS_FILE, users)
    return len(users)

def add_buyer(user):
    username = f"@{user.username}" if user.username else f"id:{user.id}"
    buyers = read_list(BUYERS_FILE)
    if username not in buyers:
        buyers.append(username)
        save_list(BUYERS_FILE, buyers)

def get_counts():
    return len(read_list(USERS_FILE)), len(read_list(BUYERS_FILE))

async def show_main_menu(message, is_edit=False):
    keyboard = [
        [InlineKeyboardButton("🗂 Архивы", callback_data="archives")],
        [InlineKeyboardButton("🛟 Поддержка", url="https://t.me/tatem4kmanager")],
        [InlineKeyboardButton("⚙️ Панель для админов", callback_data="admin")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = (
        '<tg-emoji emoji-id="5424972470023104089">☺️</tg-emoji> <b>Привет, здесь есть Топовые сборки Майнкрафт</b> '
        '<tg-emoji emoji-id="5406745015365943482">☺️</tg-emoji>\n\n'
        'что есть <tg-emoji emoji-id="5406745015365943482">☺️</tg-emoji>'
    )
    with open(PHOTO_MAIN, "rb") as photo:
        await message.reply_photo(
            photo=photo,
            caption=text,
            parse_mode="HTML",
            reply_markup=reply_markup
        )

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    add_user(update.message.from_user)
    context.user_data.clear()
    await show_main_menu(update.message)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "archives":
        add_buyer(query.from_user)
        keyboard = [
            [InlineKeyboardButton("💳 Приобрести", url="https://t.me/tribute/app?startapp=sX5S")],
            [InlineKeyboardButton("↩️ Назад", callback_data="back_to_menu")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = (
            '<tg-emoji emoji-id="5296369303661067030">☺️</tg-emoji> <b>Приватный канал с 50+ эксклюзивных сборок</b>, '
            'их можно удобно скачать через облако, некоторые даже не получится найти в открытом доступе, оставил их ниже '
            '<tg-emoji emoji-id="5406745015365943482">☺️</tg-emoji>\n\n'
            '<tg-emoji emoji-id="5325547803936572038">☺️</tg-emoji> В любой валюте <b>2.79$/125грн/200 руб</b>\n'
            '<tg-emoji emoji-id="5206607081334906820">☺️</tg-emoji> <b>Ежедневно</b> выходят новые сборки\n'
            '<tg-emoji emoji-id="5440457429147997980">☺️</tg-emoji> Оплата <b>картой</b> '
            '<tg-emoji emoji-id="5472250091332993630">☺️</tg-emoji> '
            '/криптой <tg-emoji emoji-id="5832577678300943429">☺️</tg-emoji>'
        )
        with open(PHOTO_ARCHIVE, "rb") as photo:
            await query.message.reply_photo(
                photo=photo,
                caption=text,
                parse_mode="HTML",
                reply_markup=reply_markup
            )

    elif query.data == "back_to_menu":
        context.user_data.clear()
        await show_main_menu(query.message)

    elif query.data == "admin":
        context.user_data["waiting_password"] = True
        await query.message.reply_text("🔐 Введите пароль администратора:")

    elif query.data == "admin_all_users":
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, "rb") as f:
                await query.message.reply_document(document=f, filename="все_пользователи.txt")
        else:
            await query.message.reply_text("База пользователей пуста.")

    elif query.data == "admin_buyers":
        if os.path.exists(BUYERS_FILE):
            with open(BUYERS_FILE, "rb") as f:
                await query.message.reply_document(document=f, filename="потенциальные_покупатели.txt")
        else:
            await query.message.reply_text("Потенциальных покупателей пока нет.")

    elif query.data == "admin_broadcast":
        context.user_data["waiting_broadcast"] = True
        keyboard = [[InlineKeyboardButton("↩️ Назад", callback_data="back_to_admin_panel")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            "📢 Введи сообщение которое я отправлю всем пользователям которые когда либо запускали этот бот:",
            reply_markup=reply_markup
        )

    elif query.data == "back_to_admin_panel":
        context.user_data.clear()
        users_count, buyers_count = get_counts()
        keyboard = [
            [InlineKeyboardButton("👥 Все пользователи", callback_data="admin_all_users")],
            [InlineKeyboardButton("🛒 Потенциальные покупатели", callback_data="admin_buyers")],
            [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_text(
            f"✅ <b>Панель администратора</b>\n\n"
            f"👤 Пользователей: <b>{users_count}</b>\n"
            f"🛒 Потенциальных покупателей: <b>{buyers_count}</b>",
            parse_mode="HTML",
            reply_markup=reply_markup
        )

async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # Игнорируем /start и слово "старт"
    if text.lower() in ["старт", "/start"]:
        return

    # Ввод пароля
    if context.user_data.get("waiting_password"):
        context.user_data["waiting_password"] = False
        if text == ADMIN_PASSWORD:
            users_count, buyers_count = get_counts()
            keyboard = [
                [InlineKeyboardButton("👥 Все пользователи", callback_data="admin_all_users")],
                [InlineKeyboardButton("🛒 Потенциальные покупатели", callback_data="admin_buyers")],
                [InlineKeyboardButton("📢 Рассылка", callback_data="admin_broadcast")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await update.message.reply_text(
                f"✅ <b>Панель администратора</b>\n\n"
                f"👤 Пользователей: <b>{users_count}</b>\n"
                f"🛒 Потенциальных покупателей: <b>{buyers_count}</b>",
                parse_mode="HTML",
                reply_markup=reply_markup
            )
        else:
            await update.message.reply_text("❌ Неверный пароль!")
        return

    # Рассылка
    if context.user_data.get("waiting_broadcast"):
        context.user_data["waiting_broadcast"] = False
        users = read_list(USERS_FILE)
        sent = 0
        failed = 0
        all_user_ids = read_list("user_ids.txt")
        for uid in all_user_ids:
            try:
                await context.bot.send_message(chat_id=int(uid), text=text)
                sent += 1
            except Exception:
                failed += 1
        await update.message.reply_text(
            f"✅ Рассылка завершена!\n📤 Отправлено: <b>{sent}</b>\n❌ Не доставлено: <b>{failed}</b>",
            parse_mode="HTML"
        )
        return

def add_user(user):
    username = f"@{user.username}" if user.username else f"id:{user.id}"
    users = read_list(USERS_FILE)
    if username not in users:
        users.append(username)
        save_list(USERS_FILE, users)

    # Сохраняем ID отдельно для рассылки
    user_ids = read_list("user_ids.txt")
    if str(user.id) not in user_ids:
        user_ids.append(str(user.id))
        save_list("user_ids.txt", user_ids)

    return len(users)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()