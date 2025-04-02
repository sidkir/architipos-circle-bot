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

def load_cards(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("🔮 Послание дня"),
    KeyboardButton("📚 Колоды"),
    KeyboardButton("🧱 Причины"),
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
    send_card_with_analysis(message.chat.id, card)
    bot.send_message(message.chat.id, "Эта карта показывает то, что здесь и сейчас тебе важно увидеть, понять. Это послание тебе. Какое оно? Что говорит тебе эта карта?")

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

def send_random_card_from_file(message, filename):
    cards = load_cards(filename)
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 😕")
        return
    send_card_with_analysis(message.chat.id, random.choice(cards))

last_images = {}

def send_card_with_analysis(chat_id, card):
    if "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(chat_id, file_id)
            last_images[chat_id] = file_id
    elif "file_id" in card:
        bot.send_photo(chat_id, card["file_id"])
        last_images[chat_id] = card["file_id"]
    elif "text" in card:
        bot.send_message(chat_id, card["text"])

    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Анализировать карту", callback_data="analyze_last"))
    bot.send_message(chat_id, "Хочешь я помогу тебе понять глубже значение этой карты?", reply_markup=markup)

@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    file_id = message.photo[-1].file_id
    last_images[message.chat.id] = file_id
    bot.send_photo(message.chat.id, file_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Анализировать карту", callback_data="analyze_last"))
    bot.send_message(message.chat.id, "Хочешь я помогу тебе понять глубже значение этой карты?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "analyze_last")
def analyze_last_card(call):
    chat_id = call.message.chat.id
    file_id = last_images.get(chat_id)
    if not file_id:
        bot.send_message(chat_id, "⚠️ Нет изображения для анализа")
        return
    file_info = bot.get_file(file_id)
    file = bot.download_file(file_info.file_path)
    analysis = call_gpt_for_image(file)
    bot.send_message(chat_id, analysis)

@bot.message_handler(func=lambda m: m.text == "🧠 Анализ фото")
def prompt_for_photo(message):
    bot.send_message(message.chat.id, "Отправь изображение карты, которую хочешь проанализировать.")

def call_gpt_for_image(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "Ты психолог, коуч и наставник, который интерпретирует изображения карт глубоко, метафорично и символически. Не давай прямых указаний, помогай клиенту осознать, что ему важно. Можешь задавать наводящие вопросы, если нужно прояснить смысл."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Проанализируй это изображение карты и скажи, что оно может символизировать. Какое послание в ней скрыто?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                ]
            }
        ],
        "max_tokens": 700
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"]
    else:
        return f"⚠️ Ошибка: {response.status_code} — {response.text}"

@bot.message_handler(func=lambda m: m.text == "🔥 Трансформация")
def handle_transform(message):
    send_random_text(message, "transformation.json", "🔥 Необходимая трансформация")

@bot.message_handler(func=lambda m: m.text == "😱 Страхи")
def handle_fears(message):
    send_random_text(message, "fears.json", "😱 Твой страх")

@bot.message_handler(func=lambda m: m.text == "💫 Разрешения")
def handle_blessings(message):
    send_random_text(message, "blessings.json", "💫 Твоё разрешение")

def send_random_text(message, filename, label):
    cards = load_cards(filename)
    if not cards:
        bot.send_message(message.chat.id, f"Список пуст — {label}")
        return
    text = random.choice(cards).get("text", "")
    bot.send_message(message.chat.id, f"{label}:
{text}")

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
