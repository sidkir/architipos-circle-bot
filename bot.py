import telebot
import random
import json
import os
import requests
import base64
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = os.environ["TOKEN"]
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

user_sessions = {}

def load_cards(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("🔮 Карта дня"),
    KeyboardButton("💡 Совет"),
    KeyboardButton("📚 Колоды"),
    KeyboardButton("🧠 Анализ фото")
)

deck_menu = ReplyKeyboardMarkup(resize_keyboard=True)
deck_menu.add(
    KeyboardButton("🧿 Архетипы"),
    KeyboardButton("🪶 Мудрость"),
    KeyboardButton("🌀 Процессы"),
    KeyboardButton("🐾 Послания зверей"),
    KeyboardButton("🐅 Животные силы"),
    KeyboardButton("🧚 Сказочные герои"),
    KeyboardButton("🎯 Фокус внимания"),
    KeyboardButton("🧱 Причины"),
    KeyboardButton("⬅️ Назад")
)

reason_menu = ReplyKeyboardMarkup(resize_keyboard=True)
reason_menu.add(
    KeyboardButton("🔥 Трансформация"),
    KeyboardButton("😱 Страхи"),
    KeyboardButton("💫 Разрешения"),
    KeyboardButton("⬅️ Назад")
)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Выбери, с чего хочешь начать:",
        reply_markup=main_menu
    )

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

@bot.message_handler(func=lambda m: m.text == "🔮 Карта дня")
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
    send_card_with_analysis(message.chat.id, card)
    bot.send_message(message.chat.id, "Эта карта показывает то, что здесь и сейчас тебе важно увидеть, понять. Это послание тебе. Какое оно? Что говорит тебе эта карта?")

@bot.message_handler(func=lambda m: m.text == "💡 Совет")
def handle_advice(message):
    all_files = [
        "wise_cards.json", "processes.json", "focus_cards.json"
    ]
    all_cards = []
    for file in all_files:
        all_cards.extend(load_cards(file))
    if not all_cards:
        bot.send_message(message.chat.id, "Нет доступных карт для совета.")
        return
    card = random.choice(all_cards)
    send_card_with_analysis(message.chat.id, card)
    bot.send_message(
        message.chat.id,
        "Сделай глубокий вдох и задай себе вопрос:\n\n<b>Какой совет мне нужен прямо сейчас?</b>\n\nСохраняя это намерение, нажми на кнопку — ты получишь послание, которое поможет тебе в этой ситуации.",
        parse_mode="HTML"
    )

@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def go_back(message):
    bot.send_message(message.chat.id, "Возвращаюсь в главное меню:", reply_markup=main_menu)

@bot.message_handler(func=lambda m: m.text == "🧿 Архетипы")
def deck_archetypes(message):
    send_random_card_from_file(message, "cards.json")

@bot.message_handler(func=lambda m: m.text == "🪶 Мудрость")
def deck_wisdom(message):
    send_random_card_from_file(message, "wise_cards.json")

@bot.message_handler(func=lambda m: m.text == "🌀 Процессы")
def deck_processes(message):
    send_random_card_from_file(message, "processes.json")

@bot.message_handler(func=lambda m: m.text == "🐾 Послания зверей")
def deck_wise_animals(message):
    send_random_card_from_file(message, "wise_animales.json")

@bot.message_handler(func=lambda m: m.text == "🐅 Животные силы")
def deck_power_animals(message):
    send_random_card_from_file(message, "power_animals.json")

@bot.message_handler(func=lambda m: m.text == "🧚 Сказочные герои")
def deck_fairytale(message):
    send_random_card_from_file(message, "fairytale_heroes.json")

@bot.message_handler(func=lambda m: m.text == "🎯 Фокус внимания")
def deck_focus(message):
    send_random_card_from_file(message, "focus_cards.json")

@bot.message_handler(func=lambda m: m.text == "🔥 Трансформация")
def show_transformation(message):
    show_text_from_file(message, "transformation.json")

@bot.message_handler(func=lambda m: m.text == "😱 Страхи")
def show_fears(message):
    show_text_from_file(message, "fears.json")

@bot.message_handler(func=lambda m: m.text == "💫 Разрешения")
def show_blessings(message):
    show_text_from_file(message, "blessings.json")

def send_card_with_analysis(chat_id, card):
    if "file_ids" in card:
        for fid in card["file_ids"]:
            bot.send_photo(chat_id, fid)
    elif "file_id" in card:
        bot.send_photo(chat_id, card["file_id"])

def send_random_card_from_file(message, filename):
    cards = load_cards(filename)
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста или не найдена")
        return
    card = random.choice(cards)
    send_card_with_analysis(message.chat.id, card)

def show_text_from_file(message, filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            bot.send_message(message.chat.id, random.choice(data))
        else:
            bot.send_message(message.chat.id, "Файл не в ожидаемом формате")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка чтения файла: {e}")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
