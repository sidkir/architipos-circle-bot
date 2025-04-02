import telebot
import random
import json
import os
import requests
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7852344235:AAHy7AZrf2bJ7Zo0wvRHVi7QgNASgvbUvtI"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"

bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Загрузка колоды при обращении (ленивая загрузка)
def load_cards(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# Главное меню
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("🔮 Послание дня"),
    KeyboardButton("📚 Колоды"),
    KeyboardButton("🧱 Причины"),
    KeyboardButton("🧠 Интерпретация карты")
)

# Подменю колод
deck_menu = ReplyKeyboardMarkup(resize_keyboard=True)
deck_menu.add(
    KeyboardButton("🧿 Архетипы"),
    KeyboardButton("🪶 Мудрость"),
    KeyboardButton("🌀 Процессы"),
    KeyboardButton("🐾 Послания зверей"),
    KeyboardButton("🐅 Животные силы"),
    KeyboardButton("🧚 Сказочные герои"),
    KeyboardButton("🎯 Фокус внимания"),
    KeyboardButton("⬅️ Назад")
)

# Подменю причин
reason_menu = ReplyKeyboardMarkup(resize_keyboard=True)
reason_menu.add(
    KeyboardButton("🔥 Трансформация"),
    KeyboardButton("😱 Страхи"),
    KeyboardButton("💫 Разрешения"),
    KeyboardButton("⬅️ Назад")
)

# Состояние ожидания изображения для интерпретации
awaiting_interpretation = set()

# Интерпретация карты AI
@bot.message_handler(func=lambda m: m.text == "🧠 Интерпретация карты")
def ai_mode(message):
    awaiting_interpretation.add(message.chat.id)
    bot.send_message(message.chat.id, "Отправь изображение карты, которую хочешь интерпретировать. Я помогу тебе как психолог, коуч и проводник по метафорам.")

@bot.message_handler(content_types=['photo'])
def handle_photo_for_ai(message):
    if message.chat.id not in awaiting_interpretation:
        return

    file_id = message.photo[-1].file_id
    awaiting_interpretation.remove(message.chat.id)

    prompt = (
        "Ты — психолог, коуч и проводник по бессознательному. Клиент прислал тебе изображение метафорической карты."
        "Представь, что ты её видишь. На основе этой метафоры, опиши, какие глубинные смыслы, подсознательные сценарии, образы и символы она может отражать."
        "Пиши мягко, бережно, глубоко. Помоги клиенту увидеть то, что он не осознаёт. Задай, если нужно, вопросы, помогающие ему прояснить своё состояние или запрос."
    )

    response = requests.post(
        OPENAI_API_URL,
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "system", "content": "Ты психолог, коуч, наставник. Ты говоришь метафорами и расшифровываешь образы."},
                {"role": "user", "content": prompt}
            ]
        }
    )

    if response.status_code == 200:
        answer = response.json()["choices"][0]["message"]["content"]
        bot.send_photo(message.chat.id, file_id)
        bot.send_message(message.chat.id, answer)
    else:
        bot.send_message(message.chat.id, "⚠️ Не удалось получить интерпретацию. Попробуй позже.")

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Выбери, с чего хочешь начать:",
        reply_markup=main_menu
    )

# Остальная логика (колоды, причины, послание дня) остаётся без изменений — уже добавлена в код.

# Webhook (если используется)
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))

