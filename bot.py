import telebot
import random
import json
import os
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7852344235:AAHy7AZrf2bJ7Zo0wvRHVi7QgNASgvbUvtI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Загружаем карты (архетипы)
try:
    with open("cards.json", "r", encoding="utf-8") as f:
        cards = json.load(f)
except:
    cards = []

# Клавиатура с одной кнопкой
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(KeyboardButton("🧿 Архетипы"))

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Сформулируйте свой запрос и нажмите кнопку:",
        reply_markup=menu
    )

# Обработка кнопки "Архетипы"
@bot.message_handler(func=lambda msg: msg.text == "🧿 Архетипы")
def send_archetype_card(message):
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 😕")
        return

    card = random.choice(cards)
    if "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)
    elif "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# 👉 Скрытые функции (не описаны пользователю, но работают)

# Экспорт cards.json
@bot.message_handler(commands=['export'])
def export_cards(message):
    try:
        with open("cards.json", "r", encoding="utf-8") as f:
            bot.send_document(message.chat.id, f, visible_file_name="cards.json")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Не удалось экспортировать: {str(e)}")

# Временное хранилище первой картинки
temp_photos = {}

# Получение фото, сохранение пар
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id

    # Покажи file_id
    bot.send_message(chat_id, f"📎 file_id: {file_id}")

    if chat_id in temp_photos:
        pair = {"file_ids": [temp_photos[chat_id], file_id]}

        try:
            with open("cards.json", "r", encoding="utf-8") as f:
                cards_data = json.load(f)
        except:
            cards_data = []

        cards_data.append(pair)

        try:
            with open("cards.json", "w", encoding="utf-8") as f:
                json.dump(cards_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            bot.send_message(chat_id, f"⚠️ Ошибка сохранения: {e}")
            return

        bot.send_message(chat_id, "✅ Пара сохранена!")
        temp_photos.pop(chat_id)
    else:
        temp_photos[chat_id] = file_id
        bot.send_message(chat_id, "📥 Первая картинка получена. Отправь вторую.")

# Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Запуск
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
