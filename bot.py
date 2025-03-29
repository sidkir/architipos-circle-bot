import telebot
import random
import json
import os
from flask import Flask, request

TOKEN = "7852344235:AAHy7AZrf2bJ7Zo0wvRHVi7QgNASgvbUvtI"  # <-- вставь сюда свой токен
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Загружаем карты из файла
try:
    with open("cards.json", "r", encoding="utf-8") as f:
        cards = json.load(f)
except Exception as e:
    cards = [{"name": "Ошибка", "description": str(e)}]

# Команда /start
@bot.message_handler(commands=['card'])
def send_card(message):
    card = random.choice(cards)

    if "file_ids" in card:
        # Отправляем все картинки по очереди
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)
        # Потом отправляем текст
        bot.send_message(message.chat.id, f"{card['name']}\n\n{card['description']}")

    elif "file_id" in card:
        # Если только одна картинка
        bot.send_photo(message.chat.id, card["file_id"], caption=f"{card['name']}\n\n{card['description']}")

    else:
        # Если нет картинок
        bot.send_message(message.chat.id, f"{card['name']}\n\n{card['description']}")
