import telebot
import random

TOKEN = "7852344235:AAHy7AZrf2bJ7Zo0wvRHVi7QgNASgvbUvtI"

bot = telebot.TeleBot(TOKEN)

cards = [
    {"name": "Карта 1", "description": "Описание карты 1"},
    {"name": "Карта 2", "description": "Описание карты 2"},
    {"name": "Карта 3", "description": "Описание карты 3"},
]

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id, "Привет! Нажми /card, чтобы получить случайную карту.")

@bot.message_handler(commands=['card'])
def send_card(message):
    card = random.choice(cards)
    bot.send_message(message.chat.id, f"Твоя карта: {card['name']}\n\n{card['description']}")

bot.polling()


@bot.message_handler(content_types=['photo'])
def get_file_id(message):
    if message.forward_from or message.forward_from_chat:
        # Это пересланное сообщение
        file_id = message.photo[-1].file_id
        bot.send_message(message.chat.id, f"Вот file_id пересланной картинки:\n{file_id}")
    else:
        # Просто фото
        file_id = message.photo[-1].file_id
        bot.send_message(message.chat.id, f"Вот file_id картинки:\n{file_id}")

def get_file_id(message):
    file_id = message.photo[-1].file_id
    bot.send_message(message.chat.id, f"Вот file_id этой картинки:\n{file_id}")
