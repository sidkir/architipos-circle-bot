import telebot
import random
import json
import os
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7852344235:AAHy7AZrf2bJ7Zo0wvRHVi7QgNASgvbUvtI"
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
    KeyboardButton("🧱 Причины")
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

# /start
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Выбери, с чего хочешь начать:",
        reply_markup=main_menu
    )

# Главное меню
@bot.message_handler(func=lambda m: m.text == "📚 Колоды")
def show_decks(message):
    bot.send_message(
        message.chat.id,
        "Задумайся над своим запросом. Выбери колоду и нажми на нее, держа в голове свой вопрос. Ты получишь метафорический ответ.",
        reply_markup=deck_menu
    )

@bot.message_handler(func=lambda m: m.text == "🧱 Причины")
def show_reasons(message):
    bot.send_message(
        message.chat.id,
        "Выбери, с чем хочешь поработать:",
        reply_markup=reason_menu
    )

@bot.message_handler(func=lambda m: m.text == "🔮 Послание дня")
def daily_message(message):
    all_files = [
        "cards.json", "wise_cards.json", "processes.json",
        "wise_animales.json", "power_animals.json",
        "focus_cards.json", "fairytale_heroes.json"
    ]
    all_cards = []
    for file in all_files:
        all_cards.extend(load_cards(file))
    card = random.choice(all_cards)
    if "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)
    elif "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    elif "text" in card:
        bot.send_message(message.chat.id, card["text"])
    bot.send_message(message.chat.id, "Эта карта показывает то, что здесь и сейчас тебе важно увидеть, понять. Это послание тебе. Какое оно? Что говорит тебе эта карта?")

# Назад
@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def go_back(message):
    bot.send_message(message.chat.id, "Возвращаюсь в главное меню:", reply_markup=main_menu)

# Обработчики колод
@bot.message_handler(func=lambda m: m.text == "🧿 Архетипы")
def handle_archetypes(message):
    cards = load_cards("cards.json")
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 🧿")
        return
    card = random.choice(cards)
    if "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)
    elif "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

@bot.message_handler(func=lambda m: m.text == "🪶 Мудрость")
def handle_wisdom(message):
    cards = load_cards("wise_cards.json")
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 🪶")
        return
    card = random.choice(cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    else:
        bot.send_message(message.chat.id, "Карта без изображения 🪶")

@bot.message_handler(func=lambda m: m.text == "🌀 Процессы")
def handle_process(message):
    cards = load_cards("processes.json")
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 🌀")
        return
    card = random.choice(cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

@bot.message_handler(func=lambda m: m.text == "🐾 Послания зверей")
def handle_animals(message):
    cards = load_cards("wise_animales.json")
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 🐾")
        return
    card = random.choice(cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

@bot.message_handler(func=lambda m: m.text == "🐅 Животные силы")
def handle_power_animals(message):
    cards = load_cards("power_animals.json")
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 🐅")
        return
    card = random.choice(cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

@bot.message_handler(func=lambda m: m.text == "🧚 Сказочные герои")
def handle_fairytale(message):
    cards = load_cards("fairytale_heroes.json")
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 🧚")
        return
    card = random.choice(cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

@bot.message_handler(func=lambda m: m.text == "🎯 Фокус внимания")
def handle_focus(message):
    cards = load_cards("focus_cards.json")
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 🎯")
        return
    card = random.choice(cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# Причины: Трансформация, страхи, разрешения
@bot.message_handler(func=lambda m: m.text == "🔥 Трансформация")
def handle_transform(message):
    cards = load_cards("transformation.json")
    if not cards:
        bot.send_message(message.chat.id, "Список трансформаций пуст 🔥")
        return
    text = random.choice(cards).get("text", "")
    bot.send_message(message.chat.id, f"🔥 Необходимая трансформация:\n{text}")

@bot.message_handler(func=lambda m: m.text == "😱 Страхи")
def handle_fears(message):
    cards = load_cards("fears.json")
    if not cards:
        bot.send_message(message.chat.id, "Список страхов пуст 😱")
        return
    text = random.choice(cards).get("text", "")
    bot.send_message(message.chat.id, f"😱 Твой страх:\n{text}")

@bot.message_handler(func=lambda m: m.text == "💫 Разрешения")
def handle_blessings(message):
    cards = load_cards("blessings.json")
    if not cards:
        bot.send_message(message.chat.id, "Список разрешений пуст 💫")
        return
    text = random.choice(cards).get("text", "")
    bot.send_message(message.chat.id, f"💫 Твоё разрешение:\n{text}")

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

