import os
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

DATA_FILE = "data.json"


def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "reply": "👋 হ্যালো! আপনার মেসেজটি পেয়েছি।",
            "channel": "https://t.me/RIYAJUL_EARN_HUB",
            "keywords": {}
        }

    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


data = load_data()


def is_owner(update):
    return update.effective_user and update.effective_user.id == OWNER_ID


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=data["channel"])]
    ]

    await update.message.reply_text(
        "👋 আসসালামু আলাইকুম!\n\n"
        "আপনার মেসেজটি পেয়েছি।\n"
        "কিছুক্ষণ পর আমাদের পক্ষ থেকে উত্তর দেওয়া হবে।",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def setreply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    if not context.args:
        await update.message.reply_text(
            "❌ ব্যবহার:\n/setreply আপনার Auto Reply Message"
        )
        return

    data["reply"] = " ".join(context.args)
    save_data(data)

    await update.message.reply_text(
        "✅ Auto Reply সফলভাবে পরিবর্তন করা হয়েছে।"
    )


async def setchannel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    if not context.args:
        await update.message.reply_text(
            "❌ ব্যবহার:\n/setchannel https://t.me/YourChannel"
        )
        return

    data["channel"] = context.args[0]
    save_data(data)

    await update.message.reply_text(
        "✅ Channel Link সফলভাবে পরিবর্তন করা হয়েছে।"
    )


async def addkeyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ ব্যবহার:\n/addkeyword keyword reply message"
        )
        return

    keyword = context.args[0].lower()
    reply = " ".join(context.args[1:])

    data["keywords"][keyword] = reply
    save_data(data)

    await update.message.reply_text(
        f"✅ Keyword `{keyword}` সফলভাবে যোগ হয়েছে।",
        parse_mode="Markdown"
    )


async def delkeyword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    if not context.args:
        await update.message.reply_text(
            "❌ ব্যবহার:\n/delkeyword keyword"
        )
        return

    keyword = context.args[0].lower()

    if keyword in data["keywords"]:
        del data["keywords"][keyword]
        save_data(data)

        await update.message.reply_text(
            f"✅ `{keyword}` মুছে দেওয়া হয়েছে।",
            parse_mode="Markdown"
        )
    else:
        await update.message.reply_text(
            "❌ এই Keyword পাওয়া যায়নি।"
        )


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_owner(update):
        return

    keywords = "\n".join(
        f"• {k}" for k in data["keywords"].keys()
    )

    if not keywords:
        keywords = "কোনো Keyword নেই"

    await update.message.reply_text(
        "⚙️ BOT SETTINGS\n\n"
        f"📢 Channel:\n{data['channel']}\n\n"
        f"💬 Default Reply:\n{data['reply']}\n\n"
        f"🔑 Keywords:\n{keywords}"
    )


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()

    # Commands বাদ
    if text.startswith("/"):
        return

    reply = None

    # Keyword check
    for keyword, keyword_reply in data["keywords"].items():
        if keyword in text:
            reply = keyword_reply
            break

    # Default reply
    if reply is None:
        reply = data["reply"]

    keyboard = [
        [InlineKeyboardButton("📢 JOIN CHANNEL", url=data["channel"])]
    ]

    await update.message.reply_text(
        reply,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setreply", setreply))
    app.add_handler(CommandHandler("setchannel", setchannel))
    app.add_handler(CommandHandler("addkeyword", addkeyword))
    app.add_handler(CommandHandler("delkeyword", delkeyword))
    app.add_handler(CommandHandler("settings", settings))

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            message_handler
        )
    )

    print("🤖 Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
