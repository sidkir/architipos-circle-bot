import telebot
import random
import json
import os
from flask import Flask, request

TOKEN = "ТВОЙ_ТОКЕН_ОТ_BOTFATHER"  # <-- вставь сюда свой токен
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
    bot.send_message(message.chat.id, "Привет! Я бот с метафорическими картами 🎴\nНапиши /card, чтобы вытянуть_
