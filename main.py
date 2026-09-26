import os
import io
import time
import qrcode
import logging
from threading import Thread
from flask import Flask
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, BotCommand
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
)

# Render Keep-Alive Web Server
flask_app = Flask('')

@flask_app.route('/')
def home():
    return "Bot is Alive 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    flask_app.run(host='0.0.0.0', port=port)

# Logging Setup
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# ==================== CONFIGURATION ====================
BOT_TOKEN = "8864301920:AAHX16NY3NPi7s3OusmykPdNhiKPsVItZ48"
YOUR_UPI_ID = "Raushan93@fam"
ADMIN_CHAT_ID = 8642732017

OWNER_USERNAME = "@T1XDEVIL"
SETUP_LINK = "https://t.me/ALLAPKSETUP"

USERS_FILE = "users.txt"
USER_SELECTIONS = {}
ADMIN_TEMP_DATA = {}

APPS_LIST = {
    "app_dev": "DEVIL LOADER",
    "app_safe": "SAFE LOADER",
    "app_trx": "TRX PREMIUM",
    "app_dra": "DRACO MOD",
    "app_jal": "JALBA LOADER",
    "app_prem": "PREMIUM LOADER",
    "app_ddos": "SERVER DDOS",
    "app_mars": "MARS LOADER",
    "app_ios": "IOS HACK",
    "app_jaladm": "JALBA ADMIN",
    "app_kill": "KILL LOADER"
}

CONQUEROR_IMAGE = "https://telegra.ph/file/0c9e8d4cfbe3ad70a48a9.jpg"

PLANS = {
    "5h": {"name": "5 Hours", "price": 40},
    "1d": {"name": "1 Day", "price": 80},
    "3d": {"name": "3 Days", "price": 150},
    "7d": {"name": "7 Days", "price": 300},
    "30d": {"name": "30 Days", "price": 600},
    "60d": {"name": "60 Days", "price": 800}
}

# ==================== HELPER FUNCTIONS ====================

def save_user(user_id):
    users = get_all_users()
    if str(user_id) not in users:
        with open(USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def get_all_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return list(set(line.strip() for line in f.readlines() if line.strip()))

def build_grid_keyboard(buttons_list, cols=2):
    return [buttons_list[i:i + cols] for i in range(0, len(buttons_list), cols)]

async def post_init(application: Application):
    commands = [
        BotCommand("start", "🛒 Main Menu"),
        BotCommand("setup", "📥 Download & Setup Guide"),
        BotCommand("help", "🆘 Support / Contact"),
        BotCommand("panel", "👑 Admin Menu")
    ]
    await application.bot.set_my_commands(commands)

# ==================== HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    save_user(user_id)

    app_buttons = [InlineKeyboardButton(f"📱 {name}", callback_data=app_id) for app_id, name in APPS_LIST.items()]
    keyboard = build_grid_keyboard(app_buttons, cols=2)
    keyboard.append([
        InlineKeyboardButton("📥 App Setup", url=SETUP_LINK),
        InlineKeyboardButton("🆘 Help", callback_data="help_support")
    ])

    await update.message.reply_text(
        "👋 Welcome to Key Store!\n\nAapko kis APK ki Key chahiye, niche select karein:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def setup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📥 Download & Setup Channel", url=SETUP_LINK)]]
    await update.message.reply_text("⚙️ APP SETUP & DOWNLOAD GUIDE\n\nChannel join karein:", reply_markup=InlineKeyboardMarkup(keyboard))

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"🆘 HELP & SUPPORT\n\n👑 Owner: {OWNER_USERNAME}\n📌 Message bhejne ke liye text type karein.")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user_id = query.from_user.id

    if data == "back_main":
        app_buttons = [InlineKeyboardButton(f"📱 {v}", callback_data=k) for k, v in APPS_LIST.items()]
        keyboard = build_grid_keyboard(app_buttons, cols=2)
        keyboard.append([InlineKeyboardButton("📥 App Setup", url=SETUP_LINK), InlineKeyboardButton("🆘 Help", callback_data="help_support")])
        await query.delete_message()
        await context.bot.send_message(chat_id=user_id, text="👋 Welcome to Key Store!", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data in APPS_LIST:
        app_name = APPS_LIST[data]
        plan_buttons = [InlineKeyboardButton(f"{p['name']} - ₹{p['price']}", callback_data=f"select_{data}_{k}") for k, p in PLANS.items()]
        keyboard = build_grid_keyboard(plan_buttons, cols=2)
        keyboard.append([InlineKeyboardButton("🔙 Back Menu", callback_data="back_main")])
        
        await query.delete_message()
        try:
            await context.bot.send_photo(chat_id=user_id, photo=CONQUEROR_IMAGE, caption=f"📱 App: {app_name}\n\n👇 Select Plan:", reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception:
            await context.bot.send_message(chat_id=user_id, text=f"📱 App: {app_name}\n\n👇 Select Plan:", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    if data.startswith("select_"):
        parts = data.split("_")
        app_code = f"{parts[1]}_{parts[2]}"
        plan_code = parts[3]
        app_name = APPS_LIST.get(app_code, "Key")
        plan_info = PLANS.get(plan_code, {"name": "", "price": 0})

        USER_SELECTIONS[user_id] = f"{app_name} ({plan_info['name']})"

        upi_url = f"upi://pay?pa={YOUR_UPI_ID}&pn=KeyStore&am={plan_info['price']}&cu=INR"
        qr = qrcode.make(upi_url)
        img_bytes = io.BytesIO()
        qr.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        msg = f"🛒 Selected: {app_name} - {plan_info['name']}\n💰 Amount: ₹{plan_info['price']}\n\n📌 Payment karke screenshot bhejien."
        await query.delete_message()
        await context.bot.send_photo(chat_id=user_id, photo=img_bytes, caption=msg)
        return

    if user_id == ADMIN_CHAT_ID:
        if data == "adm_broadcast_confirm":
            users = get_all_users()
            pending = ADMIN_TEMP_DATA.get(user_id)
            if not pending:
                await query.edit_message_text("❌ Session expired.")
                return

            msg_type, media_id, caption = pending["type"], pending["media"], pending["caption"]
            await query.edit_message_text(f"📢 Broadcasting to {len(users)} users...")

            succ, fail = 0, 0
            for uid in users:
                try:
                    if msg_type == "photo":
                        await context.bot.send_photo(chat_id=int(uid), photo=media_id, caption=caption)
                    else:
                        await context.bot.send_message(chat_id=int(uid), text=caption)
                    succ += 1
                except Exception:
                    fail += 1

            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"✅ Broadcast Completed!\nSuccess: {succ} | Failed: {fail}")
            ADMIN_TEMP_DATA.pop(user_id, None)

        elif data == "adm_cancel":
            ADMIN_TEMP_DATA.pop(user_id, None)
            await query.edit_message_text("❌ Action Cancelled.")

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_CHAT_ID:
        return
    users = get_all_users()
    msg = (
        f"👑 ADMIN CONTROL PANEL\n\n"
        f"📊 Total Joined Users: {len(users)}\n\n"
        f"🔑 Key Send Command:\n"
        f"<code>/send USER_ID YOUR_KEY</code>\n\n"
        f"📢 Broadcast: Photo or Text bhejien."
    )
    await update.message.reply_text(msg, parse_mode="HTML")

async def send_key_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.from_user.id != ADMIN_CHAT_ID:
        return

    if len(context.args) < 2:
        await update.message.reply_text("❌ Format: /send USER_ID YOUR_KEY_OR_MSG")
        return

    target_id = context.args[0]
    message_text = " ".join(context.args[1:])

    try:
        await context.bot.send_message(chat_id=int(target_id), text=message_text)
        await update.message.reply_text(f"✅ Message sent to {target_id}!")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to send!\nError: {e}")

# ==================== PHOTO AND MESSAGE HANDLER ====================

async def handle_media_and_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    save_user(user.id)

    if user.id == ADMIN_CHAT_ID:
        media_id = update.message.photo[-1].file_id if update.message.photo else None
        caption = update.message.caption or update.message.text or ""
        msg_type = "photo" if update.message.photo else "text"

        ADMIN_TEMP_DATA[user.id] = {"type": msg_type, "media": media_id, "caption": caption}

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📢 Broadcast To ALL Users", callback_data="adm_broadcast_confirm")],
            [InlineKeyboardButton("❌ Cancel", callback_data="adm_cancel")]
        ])

        await update.message.reply_text("⚡ Post received for Broadcast. Select action:", reply_markup=keyboard)
        return

    username_str = f"@{user.username}" if user.username else "No Username"
    selected_plan = USER_SELECTIONS.get(user.id, "Not Selected")

    if update.message.photo:
        photo_id = update.message.photo[-1].file_id
        
        admin_notification = (
            f"📩 <b>NEW PAYMENT SCREENSHOT!</b>\n\n"
            f"👤 <b>User:</b> {username_str}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"🛒 <b>Pack:</b> {selected_plan}\n\n"
            f"👇 <b>Tap on command below to COPY:</b>\n"
            f"<code>/send {user.id} YOUR_KEY_HERE</code>"
        )
        
        try:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=photo_id,
                caption=admin_notification,
                parse_mode="HTML"
            )
            await update.message.reply_text("✅ Screenshot Admin ko bhej diya gaya hai! Kuch der me key bhej di jayegi.")
        except Exception as e:
            logging.error(f"Failed to forward photo to admin: {e}")
            await update.message.reply_text("❌ Server Error: Admin tak screenshot nahi pahunch saka.")

    elif update.message.text:
        text_msg = update.message.text
        admin_notification = (
            f"📩 <b>NEW USER MESSAGE!</b>\n\n"
            f"👤 <b>User:</b> {username_str}\n"
            f"🆔 <b>User ID:</b> <code>{user.id}</code>\n"
            f"💬 <b>Message:</b> {text_msg}\n\n"
            f"👇 <b>Tap on command below to COPY:</b>\n"
            f"<code>/send {user.id} YOUR_REPLY_HERE</code>"
        )
        try:
            await context.bot.send_message(
                chat_id=ADMIN_CHAT_ID,
                text=admin_notification,
                parse_mode="HTML"
            )
            await update.message.reply_text("✅ Message Admin ko bhej diya gaya hai!")
        except Exception as e:
            logging.error(f"Failed to forward message to admin: {e}")

# ==================== MAIN APPLICATION ====================

def run_bot():
    Thread(target=run_flask).start()

    app = Application.builder().token(BOT_TOKEN).post_init(post_init).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setup", setup_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("panel", admin_panel))
    app.add_handler(CommandHandler("send", send_key_command))

    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_media_and_messages))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    run_bot()
