import telebot
import random
import json
import os
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton

TOKEN = "7852344235:AAHy7AZrf2bJ7Zo0wvRHVi7QgNASgvbUvtI"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Загружаем колоды

def load_cards(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

cards = load_cards("cards.json")
wise_cards = load_cards("wise_cards.json")
process_cards = load_cards("processes.json")
wise_animals = load_cards("wise_animales.json")
power_animals = load_cards("power_animals.json")
fokus_cards = load_cards("focus_cards.json")
fairy_cards = load_cards("fairytale_heroes.json")
transform_cards = load_cards("transformation.json")
fear_cards = load_cards("fears.json")
blessing_cards = load_cards("blessings.json")

# Главное меню
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("🔮 Послание дня"),
    KeyboardButton("📚 Колоды"),
    KeyboardButton("🧭 Техники"),
    KeyboardButton("✨ Дополнения")
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

# Подменю техник
technique_menu = ReplyKeyboardMarkup(resize_keyboard=True)
technique_menu.add(
    KeyboardButton("🎯 Моя цель"),
    KeyboardButton("❤️ Отношения"),
    KeyboardButton("🧬 Симптом"),
    KeyboardButton("🪨 Корень проблемы"),
    KeyboardButton("🌿 Ресурс"),
    KeyboardButton("🔀 Выбор"),
    KeyboardButton("✅ Да или Нет"),
    KeyboardButton("🚶 Мои шаги"),
    KeyboardButton("⬅️ Назад")
)

# Подменю дополнений
extras_menu = ReplyKeyboardMarkup(resize_keyboard=True)
extras_menu.add(
    KeyboardButton("🔥 Трансформация"),
    KeyboardButton("😱 Страхи"),
    KeyboardButton("💫 Благословения"),
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

@bot.message_handler(func=lambda m: m.text == "🧭 Техники")
def show_techniques(message):
    bot.send_message(
        message.chat.id,
        "Выбери технику для работы с картами:",
        reply_markup=technique_menu
    )

@bot.message_handler(func=lambda m: m.text == "✨ Дополнения")
def show_extras(message):
    bot.send_message(
        message.chat.id,
        "Выбери дополнение:",
        reply_markup=extras_menu
    )

@bot.message_handler(func=lambda m: m.text == "🔮 Послание дня")
def daily_message(message):
    all_cards = cards + wise_cards + process_cards + wise_animals + power_animals + fokus_cards + fairy_cards
    card = random.choice(all_cards)
    if "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)
    elif "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    elif "text" in card:
        bot.send_message(message.chat.id, card["text"])
    bot.send_message(message.chat.id, "Эта карта показывает то, что здесь и сейчас тебе важно увидеть, понять. Это послание тебе. Какое оно? Что говорит тебе эта карта?")

# Назад в главное меню
@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def go_back(message):
    bot.send_message(message.chat.id, "Возвращаюсь в главное меню:", reply_markup=main_menu)

# Колода: Сказочные герои
@bot.message_handler(func=lambda m: m.text == "🧚 Сказочные герои")
def handle_fairy(message):
    if not fairy_cards:
        bot.send_message(message.chat.id, "Колода пуста 🧚")
        return
    card = random.choice(fairy_cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    else:
        bot.send_message(message.chat.id, card.get("text", "Нет изображения или текста"))

# Колода: Фокус внимания
@bot.message_handler(func=lambda m: m.text == "🎯 Фокус внимания")
def handle_focus(message):
    if not fokus_cards:
        bot.send_message(message.chat.id, "Колода пуста 🎯")
        return
    card = random.choice(fokus_cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    else:
        bot.send_message(message.chat.id, card.get("text", "Нет изображения или текста"))

# Колода: Мудрость
@bot.message_handler(func=lambda m: m.text == "🪶 Мудрость")
def handle_wisdom(message):
    if not wise_cards:
        bot.send_message(message.chat.id, "Колода пуста 🪶")
        return
    card = random.choice(wise_cards)
    if "text" in card:
        bot.send_message(message.chat.id, card["text"])
    else:
        bot.send_message(message.chat.id, "Карта без текста")

# Дополнения: трансформация, страхи, благословения
@bot.message_handler(func=lambda m: m.text == "🔥 Необходимая трансформация")
def handle_transform(message):
    if not transform_cards:
        bot.send_message(message.chat.id, "Список трансформаций пуст 🔥")
        return
    text = random.choice(transform_cards).get("text", "")
    bot.send_message(message.chat.id, f"🔥 Необходимая трансформация:
{text}")

@bot.message_handler(func=lambda m: m.text == "😱 Страхи")
def handle_fears(message):
    if not fear_cards:
        bot.send_message(message.chat.id, "Список страхов пуст 😱")
        return
    text = random.choice(fear_cards).get("text", "")
    bot.send_message(message.chat.id, f"😱 Твой страх:
{text}")

@bot.message_handler(func=lambda m: m.text == "💫 Благословения")
def handle_blessings(message):
    if not blessing_cards:
        bot.send_message(message.chat.id, "Список благословений пуст 💫")
        return
    text = random.choice(blessing_cards).get("text", "")
    bot.send_message(message.chat.id, f"💫 Благословение:
{text}")

# Колода: Процессы
@bot.message_handler(func=lambda m: m.text == "🌀 Процессы")
def handle_processes(message):
    if not process_cards:
        bot.send_message(message.chat.id, "Колода пуста 🌀")
        return
    card = random.choice(process_cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# Колода: Послания зверей
@bot.message_handler(func=lambda m: m.text == "🐾 Послания зверей")
def handle_animals(message):
    if not wise_animals:
        bot.send_message(message.chat.id, "Колода пуста 🐾")
        return
    card = random.choice(wise_animals)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# Колода: Животные силы
@bot.message_handler(func=lambda m: m.text == "🐅 Животные силы")
def handle_power_animals(message):
    if not power_animals:
        bot.send_message(message.chat.id, "Колода пуста 🐅")
        return
    card = random.choice(power_animals)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# Webhook
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

# Запуск
if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
