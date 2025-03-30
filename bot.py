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

# Списки слов
transformations = [
    "Принятие неизбежного", "Освобождение от прошлого", "Выход из иллюзий", "Расширение сознания",
    "Переход на новый уровень", "Отпускание контроля", "Обнуление и перерождение", "Прощение себя и других",
    "Трансформация страха в доверие", "Выход из жертвы", "Видение сути", "Возвращение к себе",
    "Переход к действию", "Осознание своей силы", "Исцеление внутреннего ребёнка", "Обретение внутренней опоры",
    "Переход от борьбы к принятию", "Смена сценария", "Обретение мудрости через опыт", "Доверие жизни",
    "Преодоление зависимости от мнения других", "Преображение гнева в силу", "Превращение страха в смелость",
    "Исцеление травмы покинутости", "Раскрытие своего потенциала", "Трансформация внутреннего критика",
    "Возвращение доверия к людям", "Обретение чувства принадлежности", "Преодоление синдрома самозванца",
    "Трансформация страха потери в любовь", "Переход от сравнения к принятию себя", "Перевод контроля в поток",
    "Исцеление отношений с матерью", "Исцеление отношений с отцом", "Обретение зрелой позиции взрослого",
    "Пробуждение силы рода", "Выход из состояния выживания", "Переход от 'надо' к 'хочу'",
    "Пробуждение радости жизни", "Принятие своей ценности", "Обретение ясности и фокуса",
    "Трансформация усталости в вдохновение", "Переход от внешнего поиска к внутренней опоре",
    "Принятие границ — своих и других", "Перестройка идентичности", "Возвращение себе разрешения жить своей жизнью",
    "Переход из роли спасателя в роль творца", "Пробуждение внутреннего света", "Отказ от самопожертвования",
    "Освобождение от наследованных программ", "Переход из чувства вины к чувствованию себя"
]

fears = [
    "Страх брошенности", "Страх поглощения", "Страх неуспеха", "Страх контроля", "Страх унижения", "Страх отвержения",
    "Страх одиночества", "Страх ненужности", "Страх беспомощности", "Страх бессилия", "Страх потери свободы",
    "Страх быть собой", "Страх ответственности", "Страх близости", "Страх разочаровать", "Страх не быть принятым",
    "Страх осуждения", "Страх критики", "Страх неидеальности", "Страх быть плохим", "Страх наказания",
    "Страх быть уязвимым", "Страх будущего", "Страх перемен", "Страх неизвестности", "Страх смерти",
    "Страх болезни", "Страх старости", "Страх потерять близких", "Страх потерять любовь", "Страх потери денег",
    "Страх бедности", "Страх быть использованным", "Страх быть слабым", "Страх быть обесцененным",
    "Страх сцены", "Страх скуки", "Страх рутины", "Страх потерять контроль", "Страх быть разоблачённым",
    "Страх сказать правду", "Страх действовать", "Страх успеха", "Страх одиночества в отношениях",
    "Страх ущербности", "Страх убогости", "Страх не знать что-то", "Страх оказаться в дураках",
    "Страх быть обманутым", "Страх предательства", "Страх нового", "Страх жизни", "Страх жить",
    "Страх проявляться", "Страх быть видимым", "Страх потерять связь с божественным"
]

blessings = [
    "Ты имеешь право на СВОЮ ЖИЗНЬ", "Ты имеешь право быть таким, какой ты есть", "Ты имеешь право быть счастливым",
    "Ты имеешь право быть собой и следовать своим путём", "Ты имеешь право чувствовать и выражать свои чувства",
    "Ты имеешь право на успех и процветание", "Ты имеешь право на любовь и близость",
    "Ты имеешь право на отдых и расслабление", "Ты имеешь право выбирать и ошибаться",
    "Ты имеешь право быть в безопасности", "Ты имеешь право быть слабым и просить о помощи",
    "Ты имеешь право на поддержку", "Ты имеешь право отказаться от чужих ожиданий",
    "Ты имеешь право на удовольствие и наслаждение жизнью", "Ты имеешь право быть ценным просто потому, что ты есть",
    "Ты имеешь право быть видимым", "Ты имеешь право говорить 'нет'", "Ты имеешь право на ошибки и путь роста"
]

# Клавиатура
menu = ReplyKeyboardMarkup(resize_keyboard=True)
menu.add(
    KeyboardButton("🧿 Архетипы"),
    KeyboardButton("🪶 Мудрая подсказка"),
    KeyboardButton("🌀 Процессы"),
    KeyboardButton("🐾 Послания зверей"),
    KeyboardButton("🐅 Животные силы"),
    KeyboardButton("✨ Трансформация"),
    KeyboardButton("😨 Страхи"),
    KeyboardButton("🙏 Благословения")
)

# Пользователи
users = set()
if os.path.exists("users.txt"):
    with open("users.txt", "r") as f:
        users = set(line.strip() for line in f)

# Временные состояния пользователей для добавления карт
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    users.add(str(message.chat.id))
    with open("users.txt", "w") as f:
        for uid in users:
            f.write(uid + "\n")

    bot.send_message(
        message.chat.id,
        "Сформулируйте свой запрос и выберите колоду или практику:",
        reply_markup=menu
    )

# Архетипы
@bot.message_handler(func=lambda msg: msg.text == "🧿 Архетипы")
def send_archetypes(message):
    if not cards:
        bot.send_message(message.chat.id, "Колода пуста")
        return
    card = random.choice(cards)
    if "file_ids" in card:
        for file_id in card["file_ids"]:
            bot.send_photo(message.chat.id, file_id)
    elif "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# Мудрая подсказка
@bot.message_handler(func=lambda msg: msg.text == "🪶 Мудрая подсказка")
def send_wise(message):
    if not wise_cards:
        bot.send_message(message.chat.id, "Колода пуста")
        return
    card = random.choice(wise_cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])
    else:
        bot.send_message(message.chat.id, "⚠️ Нет изображения")

# Процессы
@bot.message_handler(func=lambda msg: msg.text == "🌀 Процессы")
def send_process(message):
    if not process_cards:
        bot.send_message(message.chat.id, "Колода пуста")
        return
    card = random.choice(process_cards)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# Послания зверей
@bot.message_handler(func=lambda msg: msg.text == "🐾 Послания зверей")
def send_animals(message):
    if not wise_animals:
        bot.send_message(message.chat.id, "Колода пуста")
        return
    card = random.choice(wise_animals)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# Животные силы
@bot.message_handler(func=lambda msg: msg.text == "🐅 Животные силы")
def send_power_animals(message):
    if not power_animals:
        bot.send_message(message.chat.id, "Колода пуста")
        return
    card = random.choice(power_animals)
    if "file_id" in card:
        bot.send_photo(message.chat.id, card["file_id"])

# Трансформация
@bot.message_handler(func=lambda msg: msg.text == "✨ Необходимая трансформация")
def send_transformation(message):
    bot.send_message(message.chat.id, f"🔄 Ваша трансформация: {random.choice(transformations)}")

# Страхи
@bot.message_handler(func=lambda msg: msg.text == "😨 Страхи")
def send_fear(message):
    bot.send_message(message.chat.id, f"😱 Ваш страх: {random.choice(fears)}")

# Благословения
@bot.message_handler(func=lambda msg: msg.text == "🙏 Благословения")
def send_blessing(message):
    bot.send_message(message.chat.id, f"💫 Благословение: {random.choice(blessings)}")

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
