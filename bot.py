import telebot
import random
import json
import os
import requests
import base64
import time
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
last_cards = {}  # Хранилище для последней карты или текста

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
    KeyboardButton("🧠 Анализ фото"),
    KeyboardButton("🎲 Да/Нет")
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

# Deck-specific messages
DECK_SPECIFIC_MESSAGES = {
    "🧿 Архетипы": "Эта фигура прошла (или проживает) какой-то жизненный опыт и хочет поделиться с тобой чем-то важным…. Прислушайся. Какое послание она тебе несет? Что хочет сказать? На что обращает твое внимание?",
    "🧚 Сказочные герои": "Эта фигура прошла (или проживает) какой-то жизненный опыт и хочет поделиться с тобой чем-то важным…. Прислушайся. Какое послание она тебе несет? Что хочет сказать? На что обращает твое внимание?",
    "🎯 Фокус внимания": "Это послание говорит о том, чтобы ты сосредоточил свое внимание на этой теме. Это фокус внимания. Посмотри на это в своей жизни. Как оно представлено в ней? Как влияет? Каково послание этой карты?",
    "🌀 Процессы": "На этот процесс тебе стоит обратить внимание. Как он представлен в твоей жизни? Каково его влияние? Какое послание через эту карту ты получаешь?",
    "🐾 Послания зверей": "Какое ощущение у тебя возникает, когда ты смотришь на это животное, на текст карты? Как это отражается в твоей жизни? Какое послание тебе оно несет?",
    "🐅 Животные силы": "Какое ощущение у тебя возникает, когда ты смотришь на это животное, на текст карты? Как это отражается в твоей жизни? Какое послание тебе оно несет?",
    "🪶 Мудрость": "Какое послание для тебя несет эта притча? Как эта мудрость может повлиять на твою жизнь?",
    "🔥 Трансформация": "Это то, на что тебе надо обратить свое внимание. Как это связано с твоей жизнью, с ситуацией? Почему именно этот текст выпал тебе сегодня? Какое послание тебе он несет?",
    "😱 Страхи": "Это то, на что тебе надо обратить свое внимание. Как это связано с твоей жизнью, с ситуацией? Почему именно этот текст выпал тебе сегодня? Какое послание тебе он несет?",
    "💫 Разрешения": "Это то, на что тебе надо обратить свое внимание. Как это связано с твоей жизнью, с ситуацией? Почему именно этот текст выпал тебе сегодня? Какое послание тебе он несет?"
}

ADVICE_SPECIFIC_MESSAGES = {
    "🧿 Архетипы": "Эта фигура прошла (или проживает) какой-то жизненный опыт, имеет свой характер и историю и она хочет поделиться с тобой чем-то важным…. Прислушайся. Какой совет она тебе дает? В твоей ситуации что она тебе советует делать или не делать?",
    "🧚 Сказочные герои": "Эта фигура прошла (или проживает) какой-то жизненный опыт, имеет свой характер и история и она хочет поделиться с тобой чем-то важным…. Прислушайся. Какой совет она тебе дает? В твоей ситуации что она тебе советует делать или не делать?",
    "🎯 Фокус внимания": "Эта карта советует тебе обратить внимание на эту тему в контексте твоего запроса/ситуации. Как эта тема связана с тобой? Совет – взгляни на это.",
    "🐾 Послания зверей": "Это животное обладает своими уникальными чертами и силой. Что это за черты и характеристики? Какой совет оно тебе дает? Что делать или не делать? Что и как оно бы сделало?",
    "🐅 Животные силы": "Это животное обладает своими уникальными чертами и силой. Что это за черты и характеристики? Какой совет оно тебе дает? Что делать или не делать? Что и как оно бы сделало?"
}

# Общие функции
def send_card_with_analysis(chat_id, card, filename, message_suffix="", deck_specific_text=""):
    is_text_deck = filename in TEXT_DECKS
    has_image = False

    if is_text_deck:
        text = card.get("text", "")
        label = next((lbl for key, (file, lbl) in REASONS.items() if file == filename), "")
        bot.send_message(chat_id, f"{label}: {text}")
        last_cards[chat_id] = {"type": "text", "content": f"{label}: {text}"}
    elif "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(chat_id, file_id)
            last_images[chat_id] = file_id
            has_image = True
        last_cards[chat_id] = {"type": "image", "file_id": card.get("file_ids")[-1]}
    elif "file_id" in card:
        bot.send_photo(chat_id, card["file_id"])
        last_images[chat_id] = card["file_id"]
        has_image = True
        last_cards[chat_id] = {"type": "image", "file_id": card["file_id"]}
    elif "text" in card:
        bot.send_message(chat_id, card["text"])
        last_images[chat_id] = None
        last_cards[chat_id] = {"type": "text", "content": card["text"]}

    # Send deck-specific text if provided
    if deck_specific_text:
        bot.send_message(chat_id, deck_specific_text)

    markup = InlineKeyboardMarkup()
    if has_image and not is_text_deck:
        markup.add(InlineKeyboardButton("Анализировать карту", callback_data="analyze_last"))
    markup.add(InlineKeyboardButton("🗣 Обсудить это", callback_data="start_chat"))
    question = "Хочешь я помогу тебе понять глубже значение этой карты?" if not is_text_deck else "Хочешь поговорить об этом?"
    bot.send_message(chat_id, question, reply_markup=markup)
    if message_suffix:
        bot.send_message(chat_id, message_suffix)

def send_random_card(chat_id, filename, message_suffix="", deck_key=""):
    cards = load_cards(filename)
    if not cards:
        bot.send_message(chat_id, "Колода пуста 😕")
        return
    card = random.choice(cards)
    deck_specific_text = DECK_SPECIFIC_MESSAGES.get(deck_key, "") if deck_key else ""
    send_card_with_analysis(chat_id, card, filename, message_suffix, deck_specific_text)

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
    all_files = list(DECKS.values()) + [v[0] for v in REASONS.values()]
    all_cards = [card for file in all_files for card in load_cards(file)]
    if not all_cards:
        bot.send_message(message.chat.id, "Нет доступных карт 😕")
        return
    card = random.choice(all_cards)
    filename = next((f for f in all_files if card in load_cards(f)), all_files[0])
    deck_key = next((k for k, v in DECKS.items() if v == filename), None)
    if not deck_key:
        deck_key = next((k for k, (f, _) in REASONS.items() if f == filename), "")
    deck_specific_text = DECK_SPECIFIC_MESSAGES.get(deck_key, "")
    send_card_with_analysis(
        message.chat.id,
        card,
        filename,
        "",
        deck_specific_text
    )

@bot.message_handler(func=lambda m: m.text == "🔔 Совет")
def advice(message):
    allowed_decks = {k: v for k, v in DECKS.items() if k not in ["🪶 Мудрость", "🌀 Процессы"]}
    all_files = list(allowed_decks.values())
    all_cards = [card for file in all_files for card in load_cards(file)]
    if not all_cards:
        bot.send_message(message.chat.id, "Нет доступных карт 😕")
        return
    card = random.choice(all_cards)
    filename = next((f for f in all_files if card in load_cards(f)), all_files[0])
    deck_key = next((k for k, v in allowed_decks.items() if v == filename), "")
    deck_specific_text = ADVICE_SPECIFIC_MESSAGES.get(deck_key, "")
    send_card_with_analysis(
        message.chat.id,
        card,
        filename,
        "",
        deck_specific_text
    )

@bot.message_handler(func=lambda m: m.text == "🎲 Да/Нет")
def yes_no_dice(message):
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "💡 Задумайтесь над своим вопросом...")
    time.sleep(1)
    bot.edit_message_text("🎲 Бросаю кубик...", chat_id, msg.message_id)
    time.sleep(1)
    bot.edit_message_text("🔄 Он крутится...", chat_id, msg.message_id)
    time.sleep(1)
    roll = random.randint(1, 12)
    result = "✅ Да" if roll >= 7 else "❌ Нет"
    bot.edit_message_text(f"✨ Выпало: {roll} — {result}", chat_id, msg.message_id)

@bot.message_handler(func=lambda m: m.text == "⬅️ Назад")
def go_back(message):
    if message.text in REASONS:
        bot.send_message(message.chat.id, "Возвращаюсь назад:", reply_markup=reason_menu)
    elif message.text in DECKS or message.text == "🧱 Причины":
        bot.send_message(message.chat.id, "Возвращаюсь назад:", reply_markup=deck_menu)
    else:
        bot.send_message(message.chat.id, "Возвращаюсь назад:", reply_markup=main_menu)

@bot.message_handler(func=lambda m: m.text in DECKS)
def handle_deck_selection(message):
    deck_key = message.text
    filename = DECKS[deck_key]
    send_random_card(message.chat.id, filename, deck_key=deck_key)

@bot.message_handler(func=lambda m: m.text in REASONS)
def handle_reason_selection(message):
    deck_key = message.text
    filename, _ = REASONS[deck_key]
    send_random_card(message.chat.id, filename, deck_key=deck_key)

# Чат и анализ
@bot.callback_query_handler(func=lambda call: call.data == "start_chat")
def start_chat_session(call):
    chat_id = call.message.chat.id
    user_sessions[chat_id] = []
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Закончить чат", callback_data="end_chat"))
    bot.send_message(chat_id, "Давай заглянем в глубины твоего внутреннего мира. Что шепчет тебе эта карта или текст?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "end_chat")
def end_chat_session(call):
    chat_id = call.message.chat.id
    if chat_id in user_sessions:
        del user_sessions[chat_id]
    if chat_id in last_cards:
        del last_cards[chat_id]
    bot.send_message(chat_id, "Путешествие завершено. Возвращаюсь в главное меню:", reply_markup=main_menu)

@bot.message_handler(func=lambda m: m.chat.id in user_sessions)
def handle_user_chat(message):
    chat_id = message.chat.id
    user_sessions[chat_id].append({"role": "user", "content": message.text})
    response = call_gpt35(chat_id, user_sessions[chat_id])
    user_sessions[chat_id].append({"role": "assistant", "content": response})
    bot.send_message(chat_id, response)

def call_gpt35(chat_id, history):
    system_message = {
        "role": "system",
        "content": (
            "Ты проводник в мир бессознательного, работающий с метафорическими картами и текстами. "
            "Твоя роль — раскрывать образы и символы, чтобы пользователь мог заглянуть в глубины своей души. "
            "Говори метафорично, поэтично, задавай вопросы, которые пробуждают осознание. "
            "Не давай прямых ответов, а веди к пониманию через ассоциации и образы. "
            "Каждая карта или текст — это зеркало, отражающее внутренний мир. Помогай пользователю увидеть это отражение и найти ответы на свои вопросы."
        )
    }

    messages = [system_message]
    if chat_id in last_cards:
        last_card = last_cards[chat_id]
        if last_card["type"] == "image":
            messages.append({
                "role": "user",
                "content": "Передо мной карта-образ, как врата в бессознательное. Мы исследуем её символы."
            })
        elif last_card["type"] == "text":
            messages.append({
                "role": "user",
                "content": f"Передо мной слова, как эхо из глубин: '{last_card['content']}'. Что они пробуждают?"
            })

    messages.extend(history)

    headers = {"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"}
    data = {"model": "gpt-3.5-turbo", "messages": messages, "max_tokens": 500}
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
            {"role": "system", "content": "Ты проводник в мир бессознательного, интерпретирующий образы карт. Говори метафорично, раскрывай символы, задавай вопросы для осознания."},
            {"role": "user", "content": [
                {"type": "text", "text": "Взгляни на эту карту. Какие тени и свет она открывает? Что она шепчет о внутреннем мире?"},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
            ]}
        ],
        "max_tokens": 700
    }
    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=data)
    return response.json()["choices"][0]["message"]["content"] if response.status_code == 200 else f"⚠️ Ошибка: {response.text}"

@bot.message_handler(func=lambda m: m.text == "🧠 Анализ фото")
def prompt_for_photo(message):
    bot.send_message(message.chat.id, "Отправь изображение карты, чтобы заглянуть в её тайны.")

@bot.message_handler(func=lambda m: m.text not in {btn.text for menu in [main_menu, deck_menu, reason_menu] for btn in menu.keyboard[0]})
def handle_fallback_text(message):
    bot.send_message(message.chat.id, "Я слышу только шепот карт и твои вопросы. Выбери путь из меню.")

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
