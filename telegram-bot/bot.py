import os
import re
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, CallbackContext, CommandHandler

# Ensure TOKEN is set correctly
TOKEN = os.getenv("BOT_TOKEN")
AFFILIATE_TAG = "vivekpandey97-21"

def convert_amazon_link(url):
    """Converts an Amazon link to an affiliate link."""
    if "amazon" in url:
        if "tag=" not in url:
            return url + f"&tag={AFFILIATE_TAG}"
        else:
            return re.sub(r'tag=[^&]+', f'tag={AFFILIATE_TAG}', url)
    return url

async def handle_message(update: Update, context: CallbackContext):
    """Handles incoming messages and modifies Amazon links."""
    message_text = update.message.text
    urls = re.findall(r'(https?://[^\s]+)', message_text)
    
    new_text = message_text
    for url in urls:
        new_text = new_text.replace(url, convert_amazon_link(url))
    
    if new_text != message_text:
        await update.message.reply_text(new_text)

async def start(update: Update, context: CallbackContext):
    """Start command response."""
    await update.message.reply_text("Hello! Send me an Amazon link, and I'll convert it into an affiliate link.")

def main():
    """Starts the bot."""
    if not TOKEN:
        raise ValueError("BOT_TOKEN environment variable is not set. Please set it before running the script.")

    app = Application.builder().token(TOKEN).build()

    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
