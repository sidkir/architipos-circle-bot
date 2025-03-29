import telebot
import random
import json
import os
from flask import Flask, request

TOKEN = "ТВОЙ_ТОКЕН_ОТ_BOTFATHER"
bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Загружаем карты
try:
    with open("cards.json", "r", encoding="utf-8") as file:
        cards = json.load(file)
except Exception as e:
    cards = [{"name": "Ошибка загрузки карт", "description": str(e)}]

# Команды
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Я бот с метафорическими картами. Напиши /card 🎴")

@bot.message_handler(commands=['card'])
def send_card(message):
    card = random.choice(cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"], caption=f"🔮 {card['name']}\n\n{card['description']}")
    else:
        bot.send_message(message.chat.id, f"🔮 {card['name']}\n\n{card['description']}")

# Получение file_id
@bot.message_handler(content_types=['photo'])
def get_file_id(message):
    file_id = message.photo[-1].file_id
    bot.send_message(message.chat.id, f"file_id: {file_id}")

# Webhook route
@app.route(f"/{TOKEN}", methods=['POST'])
def webhook():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "OK", 200

# Запуск Flask-сервера
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")
    app.run(host="0.0.0.0", port=port)
