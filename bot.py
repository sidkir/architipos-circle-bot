import telebot
import random
import json
import os
from flask import Flask, request

# Токен от BotFather
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
        "🃏 Отправь /card — получишь случайную карту (пару)\n"
        "📎 Перешли 2 изображения — бот сам добавит их в колоду\n"
        "📤 Отправь /export — и получишь весь cards.json"
    )

# Команда /card — случайная карта/пара
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

# Команда /test — тестовая картинка
@bot.message_handler(commands=['test'])
def test(message):
    bot.send_photo(
        message.chat.id,
        "AgACAgIAAyEFAASW95Q3AAMCZ-grWGJPNQABtpBnOV1AfZUImVIMAAKo8zEbA-NASwmJMG6lHi6QAQADAgADeQADNgQ",
        caption="Тестовая картинка"
    )

# Команда /export — отправить файл cards.json
@bot.message_handler(commands=['export'])
def export_cards(message):
    try:
        with open("cards.json", "r", encoding="utf-8") as f:
            bot.send_document(message.chat.id, f, visible_file_name="cards.json")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Не удалось экспортировать файл: {str(e)}")

# Временное хранилище для первой картинки (при сборе пары)
temp_photos = {}

# Обработка изображений: сбор пар + вывод file_id
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id

    # Показываем file_id
    bot.send_message(chat_id, f"📎 file_id: {file_id}")

    if chat_id in temp_photos:
        # Вторая картинка — создаём пару
        pair = {
            "file_ids": [
                temp_photos[chat_id],
                file_id
            ]
        }

        # Загружаем старые карты
        try:
            with open("cards.json", "r", encoding="utf-8") as f:
                cards_data = json.load(f)
