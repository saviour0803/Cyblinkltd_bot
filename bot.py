import telebot
from telebot.types import InlineQueryResultArticle, InputTextMessageContent
import requests
import uuid
from datetime import datetime
import os

# Correct way — secrets from Render env vars
BOT_TOKEN = os.environ '8214837266:AAHLVEX6j0l6-zuiKWM4GA1ker-Ery4jd5w'
VERIFICATION_API_URL = os.environ 'https://api.ninslip.com/verify'
API_KEY = os.environ 'b59bb13b7d445b79ad1bfd336c55d4ba507e47f5db8e506be46ef9b14c1ca3e7'
CHANNEL_ID = os.environ '-1002771187567'

bot = telebot.TeleBot(BOT_TOKEN)

@bot.inline_handler(lambda query: len(query.query) >= 3)
def handle_inline_query(inline_query):
    query = inline_query.query.strip()
    print(f"Received query: {query}")

    results = []
    try:
        payload = {"nin": query} if query.startswith(("1","2","3","4","5","6","7","8","9")) and len(query) == 11 else {"bvn": query}
        headers = {"Authorization": f"Token {API_KEY}", "Content-Type": "application/json"}

        r = requests.post(VERIFICATION_API_URL, json=payload, headers=headers, timeout=15)
        data = r.json()
        print(f"API response: {data}")

        if r.status_code == 200 and data.get("status") == "success":
            d = data["data"]
            name = f"{d.get('firstName','')} {d.get('lastName','')}".strip()
            photo = d.get("passportPhotoUrl", "")
            dob = d.get("dateOfBirth", "N/A")
            phone = d.get("phoneNumber", "N/A")

            text = f"VERIFIED\n\nName: {name}\nDOB: {dob}\nPhone: {phone}\nNIN/BVN: {query}"

            results.append(InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title=f"{name}",
                description=f"{dob} • {phone}",
                thumb_url=photo,
                input_message_content=InputTextMessageContent(message_text=text)
            ))

            # Post to channel
            bot.send_message(CHANNEL_ID, f"New Verification\nName: {name}\nNumber: ||{query}||", parse_mode="MarkdownV2")
            if photo:
                bot.send_photo(CHANNEL_ID, photo, caption="Photo")

        else:
            msg = data.get("message", "Not found")
            results.append(InlineQueryResultArticle(
                id="1", title="Not found", description=msg,
                input_message_content=InputTextMessageContent(f"{msg}")
            ))
    except Exception as e:
        print(f"Error: {e}")
        results.append(InlineQueryResultArticle(
            id="error", title="Error", description="Try again",
            input_message_content=InputTextMessageContent("Temporary error")
        ))

    bot.answer_inline_query(inline_query.id, results, cache_time=1)

print("Bot is running...")
bot.infinity_polling()
