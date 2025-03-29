import telebot
import random
import json
import os
from flask import Flask, request

TOKEN = "7852344235:AAHy7AZrf2bJ7Zo0wvRHVi7QgNASgvbUvtI"  # ВСТАВЬ сюда свой токен
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
    bot.send_message(message.chat.id, "Привет! Я бот с метафорическими картами 🎴\nНапиши /card, чтобы вытянуть карту.")

# Команда /card
@bot.message_handler(commands=['card'])
def send_card(message):
    card = random.choice(cards)

    if "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)
        bot.send_message(message.chat.id, f"{card['name']}\n\n{card['description']}")
    elif "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"], caption=f"{card['name']}\n\n{card['description']}")
    else:
        bot.send_message(message.chat.id, f"{card['name']}\n\n{card['description']}")

# Получение file_id, если переслать фото
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_id = message.photo[-1].file_id
    bot.send_message(message.chat.id, f"file_id: {file_id}")

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

@bot.message_handler(commands=['test'])
def test(message):
    bot.send_photo(message.chat.id, "AgACAgIAAyEFAASW95Q3AAMCZ-grWGJPNQABtpBnOV1AfZUImVIMAAKo8zEbA-NASwmJMG6lHi6QAQADAgADeQADNgQ", caption="Тестовое изображение")

