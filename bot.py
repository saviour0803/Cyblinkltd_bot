import telebot
from telebot.types import InlineQueryResultArticle, InputTextMessageContent
import requests
import uuid
from datetime import datetime

# Load from environment variables
BOT_TOKEN = os.environ 8214837266:AAHLVEX6j0l6-zuiKWM4GA1ker-Ery4jd5w
VERIFICATION_API_URL = os.environ https://api.ninslip.com/nin/
API_KEY = os.environ b59bb13b7d445b79ad1bfd336c55d4ba507e47f5db8e506be46ef9b14c1ca3e7
CHANNEL_ID = os.environ -1002771187567

import os
bot = telebot.TeleBot(BOT_TOKEN)

@bot.inline_handler(lambda query: len(query.query) >= 11)
def handle_inline_query(inline_query):
    query_text = inline_query.query.strip()

    try:
        headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
        payload = {"nin": query_text} if query_text.isdigit() and len(query_text) == 11 else {"bvn": query_text}

        response = requests.post(VERIFICATION_API_URL, json=payload, headers=headers, timeout=10)
        data = response.json()

        if response.status_code == 200 and data.get("success", False):
            person = data["data"]
            full_name = f"{person.get('first_name','')} {person.get('last_name','')}".strip()
            photo_url = person.get("photo") or person.get("image", "")
            dob = person.get("birth_date") or person.get("date_of_birth", "Not found")
            phone = person.get("mobile") or person.get("phone_number", "Not found")

            result_text = f"✅ VERIFIED\n\n" \
                          f"Name: {full_name}\n" \
                          f"DOB: {dob}\n" \
                          f"Phone: {phone}\n" \
                          f"Number: {query_text}"

            results = [
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title=f"✅ {full_name}",
                    description=f"{dob} • {phone}",
                    thumb_url=photo_url or None,
                    input_message_content=InputTextMessageContent(result_text)
                )
            ]

            # Post to channel on success
            channel_msg = f"✅ New Verification\n\n" \
                          f"Name: {full_name}\n" \
                          f"Number: ||{query_text}||\n" \
                          f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            bot.send_message(CHANNEL_ID, channel_msg, parse_mode="MarkdownV2")

            if photo_url:
                bot.send_photo(CHANNEL_ID, photo_url, caption="Verification photo")

        else:
            error_msg = data.get("message", "Verification failed")
            results = [
                InlineQueryResultArticle(
                    id=str(uuid.uuid4()),
                    title="❌ Not found",
                    description=error_msg,
                    input_message_content=InputTextMessageContent(f"❌ {error_msg}")
                )
            ]
    except Exception as e:
        results = [
            InlineQueryResultArticle(
                id=str(uuid.uuid4()),
                title="❌ Error",
                description="Try again soon",
                input_message_content=InputTextMessageContent("Sorry, service issue.")
            )
        ]

    bot.answer_inline_query(inline_query.id, results, cache_time=1)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "👋 Welcome to Cyblink NIN/BVN Bot!\n\nType @cyblinkltd_bot + 11-digit number anywhere.\nExample: @cyblinkltd_bot 12345678901")

print("Bot starting...")
bot.infinity_polling()
