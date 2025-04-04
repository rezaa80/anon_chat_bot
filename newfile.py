import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, CallbackContext
import json
import logging
import re

# تنظیمات ربات
API_TOKEN = "توکن_شما"
rubika_channel_link = "https://rubika.ir/cliipp_ahangg"
admin_id = "nazari_a90"  # آیدی تلگرام ادمین
users = {}
profile_data = {}
ACTIVE_CHATS = {}
user_levels = {}
user_coins = {}

# وضعیت‌های چت
START, CHAT_TYPE, CUSTOM_CHAT, FIND_PEOPLE, PROFILE, COINS = range(6)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# ذخیره‌سازی اطلاعات کاربران
def save_user_data():
    with open("users_data.json", "w") as file:
        json.dump(users, file)

def load_user_data():
    global users
    try:
        with open("users_data.json", "r") as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}

# دستور شروع
async def start(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    users[user_id] = {"state": START, "level": 1, "coins": 0, "profile_completed": False}
    save_user_data()
    await update.message.reply_text(
        "سلام! به ربات چت ناشناس خوش آمدید!\n"
        "لطفاً برای شروع به کانال روبیکا بپیوندید و سپس دکمه زیر را بزنید.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("عضویت در کانال روبیکا", url=rubika_channel_link)],
            [InlineKeyboardButton("من عضو شدم", callback_data="joined")]
        ])
    )

# چک کردن عضویت در کانال روبیکا
async def check_joined(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    if not users[user_id].get('profile_completed'):
        await update.callback_query.answer("لطفاً پروفایل خود را تکمیل کنید.")
        return
    users[user_id]['state'] = CHAT_TYPE
    save_user_data()
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "شما به کانال روبیکا پیوستید!\n"
        "لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("چت تصادفی", callback_data="random_chat")],
            [InlineKeyboardButton("چت سفارشی", callback_data="custom_chat")],
            [InlineKeyboardButton("پروفایل", callback_data="profile")],
            [InlineKeyboardButton("خرید سکه", callback_data="coins")],
            [InlineKeyboardButton("پشتیبانی", callback_data="support")]
        ])
    )

# تکمیل پروفایل
async def complete_profile(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    users[user_id]['profile_completed'] = True
    save_user_data()
    await update.message.reply_text("پروفایل شما با موفقیت تکمیل شد. حالا می‌توانید از ربات استفاده کنید.")

# خرید سکه
async def buy_coins(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "لطفاً برای خرید سکه دستور زیر را وارد کنید:\n100 سکه = 10,000 تومان"
    )
    await update.callback_query.message.reply_text(
        "شماره کارت: 6219-8618-1971-3750\n"
        "به نام: منیر شعبانی\n"
        "بعد از واریز فیش را ارسال کنید."
    )

# ارسال پیام به ادمین برای تایید فیش
async def send_payment_info(payment_info: str):
    message = f"یک کاربر فیش پرداختی فرستاده است:\n{payment_info}"
    await context.bot.send_message(chat_id=admin_id, text=message)

# زمانی که فیش واریز ارسال می‌شود
async def handle_payment(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    payment_info = update.message.text
    # ارسال فیش واریز به ادمین
    await send_payment_info(payment_info)

    # منتظر تایید از ادمین
    await update.message.reply_text("فیش شما برای بررسی به ادمین ارسال شد. منتظر تایید باشید.")

# چت تصادفی
async def random_chat(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    users[user_id]['state'] = "random_chat"
    save_user_data()
    await update.callback_query.answer()
    await update.callback_query.edit_message_text("در حال اتصال به یک کاربر تصادفی...")

# چت سفارشی
async def custom_chat(update: Update, context: CallbackContext):
    user_id = update.callback_query.from_user.id
    users[user_id]['state'] = "custom_chat"
    save_user_data()
    await update.callback_query.answer()
    await update.callback_query.edit_message_text(
        "چت سفارشی را انتخاب کنید:\n"
        "1. چت با دختر\n"
        "2. چت با پسر\n"
        "3. جستجو براساس مکان"
    )

# تنظیمات اصلی
def main():
    load_user_data()
    application = Application.builder().token(API_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(check_joined, pattern="joined"))
    application.add_handler(CallbackQueryHandler(random_chat, pattern="random_chat"))
    application.add_handler(CallbackQueryHandler(custom_chat, pattern="custom_chat"))
    application.add_handler(CallbackQueryHandler(buy_coins, pattern="coins"))
    application.add_handler(MessageHandler(filters.TEXT, handle_payment))  # ارسال فیش واریز به ربات
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, complete_profile))  # تکمیل پروفایل
    # سایر دستورات...

    application.run_polling()

if __name__ == "__main__":
    main()