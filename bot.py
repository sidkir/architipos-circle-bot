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
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"], caption=f"{card['name']}\n\n{card['description']}")
    else:
        bot.send_message(message.chat.id, f"{card['name']}\n\n{card['description']}")
