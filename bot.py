import telebot
import random
import json

TOKEN = "ТВОЙ_ТОКЕН_ОТ_BOTFATHER"

bot = telebot.TeleBot(TOKEN)

# Загружаем карты из файла cards.json
try:
    with open("cards.json", "r", encoding="utf-8") as file:
        cards = json.load(file)
except Exception as e:
    cards = [{"name": "Ошибка загрузки карт", "description": str(e)}]

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Я бот с метафорическими картами.\nНажми /card, чтобы вытянуть карту 🎴")

@bot.message_handler(commands=['card'])
def send_card(message):
    card = random.choice(cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"], caption=f"🔮 {card['name']}\n\n{card['description']}")
    else:
        bot.send_message(message.chat.id, f"🔮 {card['name']}\n\n{card['description']}")

# Обработка фото для получения file_id
@bot.message_handler(content_types=['photo'])
def get_file_id
