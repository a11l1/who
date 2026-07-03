import os
import asyncio
import sqlite3
import logging
import qrcode
from io import BytesIO
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# گرفتن مقادیر از Environment Variables
BOT_TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = int(os.environ.get("ADMIN_ID", "0"))

# لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# ============== دیتابیس ==============
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (user_id INTEGER PRIMARY KEY, 
                  username TEXT, 
                  first_name TEXT,
                  joined_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

def add_user(user_id, username, first_name):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("INSERT OR IGNORE INTO users (user_id, username, first_name) VALUES (?, ?, ?)",
              (user_id, username, first_name))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT user_id FROM users")
    users = c.fetchall()
    conn.close()
    return [u[0] for u in users]

def get_user_count():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    count = c.fetchone()[0]
    conn.close()
    return count

# ============== دستورات اصلی ==============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    add_user(user.id, user.username, user.first_name)
    await update.message.reply_text(
        f"سلام {user.first_name}! 👋\n\n"
        "🤖 به ربات QR Code خوش اومدی!\n\n"
        "📝 هر متنی بفرستی → تبدیل به QR Code میشه\n"
        
    )

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🆔 Chat ID شما: `{user.id}`\n"
        f"👤 Name: {user.first_name}",
        parse_mode='Markdown'
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    count = get_user_count()
    await update.message.reply_text(f"📊 آمار ربات:\n\n👥 کل یوزرها: {count}")

# ============== Broadcast ==============
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ دسترسی نداری")
        return
    
    if not context.args:
        await update.message.reply_text(
            "📝 استفاده:\n`/broadcast سلام به همه!`",
            parse_mode='Markdown'
        )
        return
    
    message = " ".join(context.args)
    users = get_all_users()
    
    status_msg = await update.message.reply_text(f"📤 در حال ارسال به {len(users)} نفر...")
    
    success = 0
    failed = 0
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            success += 1
        except Exception:
            failed += 1
        await asyncio.sleep(0.05)
    
    await status_msg.edit_text(
        f"✅ ارسال شد!\n\n"
        f"👥 کل یوزرها: {len(users)}\n"
        f"✅ موفق: {success}\n"
        f"❌ ناموفق: {failed}"
    )

# ============== QR Code ==============
def make_qr(text: str) -> BytesIO:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    bio = BytesIO()
    img.save(bio, 'PNG')
    bio.seek(0)
    return bio

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if not text:
        return
    
    qr_img = make_qr(text)
    await update.message.reply_photo(
        photo=qr_img,
        caption=f"✅ QR Code ساخته شد!\n📝 متن: {text[:50]}{'...' if len(text) > 50 else ''}"
    )


# ============== اجرا ==============
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN تنظیم نشده!")
        return
    
    if not ADMIN_ID:
        print("⚠️ ADMIN_ID تنظیم نشده - دستورات ادمین کار نمیکنه")
    
    init_db()
    print("✅ دیتابیس آماده شد")
    
    app = Application.builder().token(BOT_TOKEN).build()
    
    # دستورات
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("id", get_id))
    app.add_handler(CommandHandler("stats", stats))
    app.add_handler(CommandHandler("broadcast", broadcast))
    
    # پیام‌ها
    app.add_handler(MessageHandler(filters.PHOTO))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    print("🤖 ربات اجرا شد!")
    app.run_polling()

if __name__ == "__main__":
    main()