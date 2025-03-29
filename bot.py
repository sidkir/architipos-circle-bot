import telebot
import random
import json
import os
from flask import Flask, request

TOKEN = "ТВОЙ_ТОКЕН_СЮДА"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Загружаем карты
try:
    with open("cards.json", "r", encoding="utf-8") as f:
        cards = json.load(f)
except Exception as e:
    cards = [{"name": "Ошибка загрузки карт", "description": str(e)}]

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я бот с метафорическими картами. Нажми /card 🎴")

# Команда /card
@bot.message_handler(commands=['card'])
def send_card(message):
    card = random.choice(cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"], caption=f"🔮 {card['name']}\n\n{card['description']}")
    else:
        bot.send_message(message.chat.id, f"🔮 {card['name']}\n\n{card['description']}")

# Обработка изображений для получения file_id
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    file_id = message.photo[-1].file_id
    bot.send_message(message.chat.id, f"file_id: {file_id}")

# Webhook для Telegram
@app.route(f'/{TOKEN}', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Установка Webhook при запуске
if __name__ == '__main__':
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

