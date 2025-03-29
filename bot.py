import telebot
import random
import json
import os
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

# Токен от BotFather
TOKEN = "7852344235:AAHy7AZrf2bJ7Zo0wvRHVi7QgNASgvbUvtI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Загружаем карты из файла (Архетипы)
try:
    with open("cards.json", "r", encoding="utf-8") as f:
        cards = json.load(f)
except Exception as e:
    cards = [{"name": "Ошибка", "description": str(e)}]

# Загружаем притчи (Мудрые подсказки)
try:
    with open("wise_cards.json", "r", encoding="utf-8") as f:
        wise_cards = json.load(f)
except:
    wise_cards = []

# Загружаем пользователей, если есть
users = set()
if os.path.exists("users.txt"):
    with open("users.txt", "r") as f:
        users = set(line.strip() for line in f)

# Клавиатура с двумя кнопками
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("🧿 Архетипы"),
    KeyboardButton("🪶 Мудрая подсказка")
)

# Команда /start
@bot.message_handler(commands=['start'])
def start(message):
    users.add(str(message.chat.id))
    with open("users.txt", "w") as f:
        for uid in users:
            f.write(uid + "\n")

    bot.send_message(
        message.chat.id,
        "Сформулируйте свой запрос и выберите:",
        reply_markup=menu
    )

# Кнопка "Архетипы"
@bot.message_handler(func=lambda msg: msg.text == "🧿 Архетипы")
def send_archetype_card(message):
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
        bot.send_message(message.chat.id, "Только текстовая карта")

# Кнопка "Мудрая подсказка"
@bot.message_handler(func=lambda msg: msg.text == "🪶 Мудрая подсказка")
def send_wise_card(message):
    if not wise_cards:
        bot.send_message(message.chat.id, "Пока нет мудрых подсказок 🧐")
        return
    card = random.choice(wise_cards)
    bot.send_message(message.chat.id, card["text"])

# Команда /card (альтернатива кнопке)
@bot.message_handler(commands=['card'])
def send_card(message):
    send_archetype_card(message)

# Команда /count_users
@bot.message_handler(commands=['count_users'])
def count_users(message):
    bot.send_message(message.chat.id, f"👥 Уникальных пользователей: {len(users)}")

# Экспорт cards.json
@bot.message_handler(commands=['export'])
def export_cards(message):
    try:
        with open("cards.json", "r", encoding="utf-8") as f:
            bot.send_document(message.chat.id, f, visible_file_name="cards.json")
    except Exception as e:
        bot.send_message(message.chat.id, f"⚠️ Не удалось экспортировать файл: {str(e)}")

# Временное хранилище для первой картинки
temp_photos = {}

# Обработка фото — сбор пары
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    chat_id = message.chat.id
    file_id = message.photo[-1].file_id

    bot.send_message(chat_id, f"📎 file_id: {file_id}")

    if chat_id in temp_photos:
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

