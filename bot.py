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

# Клавиатура
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("🧿 Архетипы"),
    KeyboardButton("🪶 Мудрая подсказка"),
    KeyboardButton("🌀 Процессы"),
    KeyboardButton("🐾 Послания зверей"),
    KeyboardButton("🐅 Животные силы")
)

# Пользователи
users = set()
if os.path.exists("users.txt"):
    with open("users.txt", "r") as f:
        users = set(line.strip() for line in f)

# Временные состояния пользователей для добавления карт
user_states = {}

# /start
@bot.message_handler(commands=['start'])
def start(message):
    users.add(str(message.chat.id))
    with open("users.txt", "w") as f:
        for uid in users:
            f.write(uid + "\n")

    bot.send_message(
        message.chat.id,
        "Сформулируйте свой запрос и выберите колоду:",
        reply_markup=menu
    )

# Показываем картинку по file_id
@bot.message_handler(commands=['show_file'])
def show_file_command(message):
    bot.send_message(message.chat.id, "📎 Вставь file_id, и я покажу изображение.")
    user_states[message.chat.id] = {"step": "show_file"}

@bot.message_handler(func=lambda msg: user_states.get(msg.chat.id, {}).get("step") == "show_file")
def handle_show_file(msg):
    file_id = msg.text.strip()
    try:
        bot.send_photo(msg.chat.id, file_id)
        user_states.pop(msg.chat.id)
    except Exception as e:
        bot.send_message(msg.chat.id, f"⚠️ Не получилось показать изображение: {e}")

# Архетипы
@bot.message_handler(func=lambda msg: msg.text == "🧿 Архетипы")
def send_archetype_card(message):
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста 😕")
        return
    card = random.choice(cards)
    if "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)
    elif "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# Мудрая подсказка
@bot.message_handler(func=lambda msg: msg.text == "🪶 Мудрая подсказка")
def send_wise_card(message):
    if not wise_cards:
        bot.send_message(message.chat.id, "Колода пуста 😕")
        return
    card = random.choice(wise_cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    else:
        bot.send_message(message.chat.id, "⚠️ Карта без изображения")

# Процессы
@bot.message_handler(func=lambda msg: msg.text == "🌀 Процессы")
def send_process_card(message):
    if not process_cards:
        bot.send_message(message.chat.id, "Колода пуста 😕")
        return
    card = random.choice(process_cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    elif "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)

# Мудрые животные
@bot.message_handler(func=lambda msg: msg.text == "🐾 Послания зверей")
def send_wise_animal_card(message):
    if not wise_animals:
        bot.send_message(message.chat.id, "Колода пуста 🐾")
        return
    card = random.choice(wise_animals)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    elif "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)

# Животные силы
@bot.message_handler(func=lambda msg: msg.text == "🐅 Животные силы")
def send_power_animal_card(message):
    if not power_animals:
        bot.send_message(message.chat.id, "Колода пуста 🐅")
        return
    card = random.choice(power_animals)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    elif "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)

# Экспорт
@bot.message_handler(commands=['export'])
def export_cards(message):
    for filename in ["cards.json", "wise_cards.json", "processes.json", "wise_animales.json", "power_animals.json"]:
        if os.path.exists(filename):
            with open(filename, "rb") as f:
                bot.send_document(message.chat.id, f, visible_file_name=filename)

# Команда /add
@bot.message_handler(commands=['add'])
def start_add(message):
    user_states[message.chat.id] = {"step": "count"}
    bot.send_message(message.chat.id, "Сколько изображений будет у каждой карты? Введи 1 или 2.")

# Добавление карты — шаги
@bot.message_handler(func=lambda msg: msg.chat.id in user_states)
def handle_state(msg):
    state = user_states[msg.chat.id]

    if state["step"] == "count":
        if msg.text.strip() not in ["1", "2"]:
            bot.send_message(msg.chat.id, "Пожалуйста, введи 1 или 2.")
            return
        state["count"] = int(msg.text.strip())
        state["step"] = "filename"
        bot.send_message(msg.chat.id, "Как назвать файл для сохранения карт? Например: cards.json или wise_cards.json")

    elif state["step"] == "filename":
        state["filename"] = msg.text.strip()
        state["step"] = "waiting_photos"
        state["photos"] = []
        bot.send_message(msg.chat.id, f"Отправляй изображения. Ввод считается завершённым при команде /export")

# Сбор изображений
@bot.message_handler(content_types=['photo'])
def collect_photo(message):
    state = user_states.get(message.chat.id)
    if not state or state.get("step") != "waiting_photos":
        return

    file_id = message.photo[-1].file_id
    state["photos"].append(file_id)

    # Сохраняем по одному или по паре
    if state["count"] == 1:
        entry = {"file_id": file_id}
        try:
            data = load_cards(state["filename"])
            data.append(entry)
            with open(state["filename"], "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            bot.send_message(message.chat.id, f"✅ Карта сохранена в {state['filename']}")
        except Exception as e:
            bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")
    else:
        photos = state["photos"]
        if len(photos) % 2 == 0:
            pair = {"file_ids": [photos[-2], photos[-1]]}
            try:
                data = load_cards(state["filename"])
                data.append(pair)
                with open(state["filename"], "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                bot.send_message(message.chat.id, f"✅ Пара сохранена в {state['filename']}")
            except Exception as e:
                bot.send_message(message.chat.id, f"⚠️ Ошибка: {e}")

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

