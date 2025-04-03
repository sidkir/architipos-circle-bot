import telebot
import random
import json
import os
import requests
import base64
from flask import Flask, request
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Инициализация
TOKEN = os.environ["TOKEN"]
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Хранилища
user_sessions = {}
last_images = {}

# Загрузка карт из JSON
def load_cards(filename):
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# Меню
main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.add(
    KeyboardButton("🔮 Послание дня"),
    KeyboardButton("🔔 Совет"),
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

# Конфигурация колод
DECKS = {
    "🧿 Архетипы": "cards.json",
    "🪶 Мудрость": "wise_cards.json",
    "🌀 Процессы": "processes.json",
    "🐾 Послания зверей": "wise_animales.json",
    "🐅 Животные силы": "power_animals.json",
    "🧚 Сказочные герои": "fairytale_heroes.json",
    "🎯 Фокус внимания": "focus_cards.json"
}

REASONS = {
    "🔥 Трансформация": ("transformation.json", "🔥 Необходимая трансформация"),
    "😱 Страхи": ("fears.json", "😱 Твой страх"),
    "💫 Разрешения": ("blessings.json", "💫 Твоё разрешение")
}

TEXT_DECKS = ["transformation.json", "fears.json", "blessings.json"]

# Общие функции
def send_card_with_analysis(chat_id, card, is_text_deck=False, message_suffix=""):
    if is_text_deck:
        text = card.get("text", "")
        label = next((lbl for key, (file, lbl) in REASONS.items() if file in TEXT_DECKS), "")
        bot.send_message(chat_id, f"{label}: {text}")
    elif "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(chat_id, file_id)
            last_images[chat_id] = file_id
    elif "file_id" in card:
        bot.send_photo(chat_id, card["file_id"])
        last_images[chat_id] = file_id
    elif "text" in card:
        bot.send_message(chat_id, card["text"])
        last_images[chat_id] = None  # Для текстовых карт без изображения

    markup = InlineKeyboardMarkup()
    if not is_text_deck and last_images.get(chat_id):  # Проверяем, есть ли изображение
        markup.add(InlineKeyboardButton("Анализировать карту", callback_data="analyze_last"))
    markup.add(InlineKeyboardButton("🗣 Обсудить это", callback_data="start_chat"))
    question = "Хочешь я помогу тебе понять глубже значение этой карты?" if not is_text_deck else "Хочешь поговорить об этом?"
    bot.send_message(chat_id, question, reply_markup=markup)
    if message_suffix:
        bot.send_message(chat_id, message_suffix)

def send_random_card(chat_id, filename, message_suffix=""):
    cards = load_cards(filename)
    if not cards:
        bot.send_message(chat_id, "Колода пуста 😕")
        return
    is_text_deck = filename in TEXT_DECKS
    card = random.choice(cards)
    send_card_with_analysis(chat_id, card, is_text_deck, message_suffix)

# Обработчики команд и меню
@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Выбери, с чего хочешь начать:", reply_markup=main_menu)

@bot.message_handler(func=lambda m: m.text == "📚 Колоды")
def show_decks(message):
    bot.send_message(
        message.chat.id,
        "Задумайся над своим запросом. Выбери колоду и нажми на нее, держа в голове свой вопрос.",
        reply_markup=deck_menu
    )

@bot.message_handler(func=lambda m: m.text == "🧱 Причины")
def show_reasons(message):
    bot.send_message(message.chat.id, "Выбери, с чем хочешь поработать:", reply_markup=reason_menu)

@bot.message_handler(func=lambda m: m.text == "🔮 Послание дня")
def daily_message(message):
    all_files = list(DECKS.values())
    all_cards = [card for file in all_files for card in load_cards(file)]
    if not all_cards:
        bot.send_message(message.chat.id, "Нет доступных карт 😕")
        return
    card = random.choice(all_cards)
    send_card_with_analysis(message.chat.id, card, is_text_deck=False, message_suffix="Эта карта — твое послание на сегодня. Что она тебе говорит?")

@bot.message_handler(func=lambda m: m.text == "🔔 Совет")
def advice(message):
    all_files = list(DECKS.values())
    all_cards = [card for file in all_files for card in load_cards(file)]
    if not all_cards:
        bot.send_message(message.chat.id, "Нет доступных карт 😕")
        return
    card = random.choice(all_cards)
    send_card_with_analysis(message.chat.id, card, is_text_deck=False, message_suffix="Что эта карта тебе советует?")

@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def go_back(message):
    current_menu = deck_menu if message.text in DECKS or message.text == "🧱 Причины" else main_menu
    bot.send_message(message.chat.id, "Возвращаюсь назад:", reply_markup=current_menu)

@bot.message_handler(func=lambda m: m.text in DECKS)
def handle_deck_selection(message):
    send_random_card(message.chat.id, DECKS[message.text])

@bot.message_handler(func=lambda m: m.text in REASONS)
def handle_reason_selection(message):
    filename, _ = REASONS[message.text]
    send_random_card(message.chat.id, filename)

# Чат и анализ
@bot.callback_query_handler(func=lambda call: call.data == "start_chat")
def start_chat_session(call):
    chat_id = call.message.chat.id
    user_sessions[chat_id] = []
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Закончить чат", callback_data="end_chat"))
    bot.send_message(chat_id, "Давай обсудим. Расскажи, что вызвало у тебя эта карта или текст?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "end_chat")
def end_chat_session(call):
    chat_id = call.message.chat.id
    if chat_id in user_sessions:
        del user_sessions[chat_id]
    bot.send_message(chat_id, "Чат завершен. Возвращаюсь в меню:", reply_markup=main_menu)

@bot.message_handler(func=lambda m: m.chat.id in user_sessions)
def handle_user_chat(message):
    chat_id = message.chat.id
    user_sessions[chat_id].append({"role": "user", "content": message.text})
    response = call_gpt35(user_sessions[chat_id])
    user_sessions[chat_id].append({"role": "assistant", "content": response})
    bot.send_message(chat_id, response)

def call_gpt35(history):
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "gpt-3.5-turbo", "messages": history, "max_tokens": 500}
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else f"⚠️ Ошибка: {response.text}"

@bot.message_handler(content_types=['photo'])
def receive_photo(message):
    file_id = message.photo[-1].file_id
    last_images[message.chat.id] = file_id
    bot.send_photo(message.chat.id, file_id)
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Анализировать карту", callback_data="analyze_last"))
    markup.add(InlineKeyboardButton("🗣 Обсудить это", callback_data="start_chat"))
    bot.send_message(message.chat.id, "Хочешь я помогу тебе понять эту карту?", reply_markup=markup)

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

def call_gpt_for_image(image_bytes):
    base64_image = base64.b64encode(image_bytes).decode('utf-8')
    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-4o",
        "messages": [
            {"role": "system", "content": "Ты психолог, интерпретирующий карты метафорично и символически. Задавай вопросы, если нужно."},
            {"role": "user", "content": [
                {"type": "text", "text": "Проанализируй эту карту. Что она может символизировать?"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        "max_tokens": 700
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else f"⚠️ Ошибка: {response.text}"

@bot.message_handler(func=lambda m: m.text == "🧠 Анализ фото")
def prompt_for_photo(message):
    bot.send_message(message.chat.id, "Отправь изображение карты для анализа.")

@bot.message_handler(func=lambda m: m.text not in {btn.text for menu in [main_menu, deck_menu, reason_menu] for btn in menu.keyboard[0]})
def handle_fallback_text(message):
    bot.send_message(message.chat.id, "Я понимаю только команды и изображения. Выбери действие из меню.")

# Вебхук
@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode("utf-8"))
    bot.process_new_updates([update])
    return "OK", 200

if __name__ == "__main__":
    bot.remove_webhook()
    bot.set_webhook(url=f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/{TOKEN}")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
