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
    "🧿 Архет
