import telebot
import random
import json
import os
from flask import Flask, request

TOKEN = "7852344235:AAHy7AZrf2bJ7Zo0wvRHVi7QgNASgvbUvtI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Загружаем карты из файла
try:
    with open("cards.json", "r", encoding="utf-8") as f:
        cards = json.load(f)
except Exception as e:
    cards = [{"name": "Ошибка", "description": str(e)}]

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот с метафорическими картами 🎴\n\n"
        "🃏 /card — случайная карта (или пара)\n"
        "📎 Перешли 2 фото — добавлю их в колоду\n"
        "📤 /export — скачать базу карт"
    )

# Команда /card
@bot.message_handler(commands=['card'])
def send_card(message):
    if not cards:
        bot.send_message(message.chat.id, "Колода пока пуста 😕")
        return

    card = random.choice(cards)

    if "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)
    elif "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    else:
        bot.send_message(message.chat.id, "🔸 Только текстовая карта (без изображений)")

# Команда /export
@bot.message_handler(commands=['export'])
def export_cards(message):
    try:
        with open("cards.json", "r", encoding="utf-8") as f:
            bot.send_document(message.chat.id, f, visible_file_name="cards.json")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Не удалось экспортировать файл: {str(e)}")

# Временное хранилище первой картинки
temp_photos = {}

# Обработка фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id

    bot.send_message(chat_id, f"📎 file_id: {file_id}")

    if chat_id in temp_photos:
        # Вторая картинка — создать пару
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

# Запуск сервера
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

