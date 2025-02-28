import os
import re
import time
import requests
import asyncio
import schedule
import logging
from bs4 import BeautifulSoup
from telegram import Bot

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# ✅ Telegram Bot Config
BOT_TOKEN = "7989619436:AAH7dN-pgUwVBFlcqB0DwTUSbpMlP9aiTdY"
CHANNEL_ID = "@deal_creator"  # Use @your_channel or chat ID

# ✅ Amazon Affiliate Tag
AFFILIATE_TAG = "vivekpandey97-21"

# ✅ Amazon Deals URL
AMAZON_DEALS_URL = "https://www.amazon.in/"

# ✅ Function to Convert Amazon Links to Affiliate Links
def convert_amazon_link(url):
    """Converts an Amazon product link to an affiliate link."""
    match = re.search(r"(dp/|gp/product/)([A-Z0-9]+)", url)
    if match:
        asin = match.group(2)
        return f"https://www.amazon.in/dp/{asin}/?tag={AFFILIATE_TAG}"
    return url

# ✅ Function to Scrape Amazon Deals
def scrape_amazon_deals():
    """Scrapes Amazon for the best deals with high discounts."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(AMAZON_DEALS_URL, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        logging.error(f"❌ Failed to fetch Amazon deals: {e}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    
    # ✅ Extracting product deals (Modify as per Amazon structure)
    deals = []
    products = soup.find_all("div", class_="a-section a-spacing-none a-spacing-top-micro")

    for product in products:
        try:
            title = product.find("span", class_="a-size-base-plus").text.strip()
            discount_element = product.find("span", class_="a-size-mini a-color-base")
            price_element = product.find("span", class_="a-price-whole")
            link_element = product.find("a", class_="a-link-normal")

            if not discount_element or not link_element or not price_element:
                continue  # Skip if required data is missing

            discount_text = discount_element.text.strip()
            price_text = price_element.text.strip()
            link = "https://www.amazon.in" + link_element["href"]

            # ✅ Extract percentage discount (if available)
            discount_match = re.search(r"(\d+)%", discount_text)
            discount_value = int(discount_match.group(1)) if discount_match else 0

            if discount_value >= 50:  # ✅ Set threshold (changeable)
                affiliate_link = convert_amazon_link(link)
                deals.append({
                    "title": title,
                    "discount": f"{discount_value}%",
                    "price": f"₹{price_text}",
                    "link": affiliate_link
                })

        except Exception as e:
            logging.warning(f"Skipping a product due to an error: {e}")
            continue

    return deals

# ✅ Function to Send Deals to Telegram Channel
# ✅ Async Function to Send Deals to Telegram
async def send_deals_to_telegram():
    """Fetches deals and sends them to the Telegram channel asynchronously."""
    bot = Bot(token=BOT_TOKEN)
    deals = scrape_amazon_deals()

    if not deals:
        logging.info("No high-discount deals found.")
        return

    for deal in deals:
        message = (
            f"🔥 *{deal['title']}* 🔥\n"
            f"💰 Price: {deal['price']}\n"
            f"💸 Discount: {deal['discount']}\n"
            f"🔗 [Buy Now]({deal['link']})"
        )

        try:
            await bot.send_message(chat_id=CHANNEL_ID, text=message, parse_mode="Markdown", disable_web_page_preview=True)
            logging.info(f"✅ Sent deal: {deal['title']}")
            await asyncio.sleep(2)  # ✅ Prevent hitting Telegram rate limits

        except Exception as e:
            logging.error(f"❌ Failed to send message: {e}")

# ✅ Schedule Task to Run Every 5 Minutes
schedule.every(5).minutes.do(lambda: asyncio.run(send_deals_to_telegram()))

# ✅ Run the Bot
logging.info("🤖 Bot is running... Fetching deals every 5 minutes...")
while True:
    schedule.run_pending()
    time.sleep(60)
