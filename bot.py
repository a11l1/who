from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
import qrcode
import io
import os

TOKEN = os.environ.get("BOT_TOKEN", "8928152886:AAEYGCI6TBjvIUkZJh9XxK-vxLZG_sagI30")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 سلام!\n"
        "هر لینک یا متنی بفرست، QR Code میسازم! 🔲"
    )

async def make_qr(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        img = qrcode.make(text)
        bio = io.BytesIO()
        img.save(bio, format='PNG')
        bio.seek(0)
        await update.message.reply_photo(
            photo=bio,
            caption=f"✅ QR ساخته شد!"
        )
    except Exception as e:
        await update.message.reply_text(f"❌ ارور: {e}")

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, make_qr))
    print("🤖 ربات روشن شد!")
    app.run_polling()