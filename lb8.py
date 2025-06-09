import telebot
from telebot import types
import json

TOKEN = ""
bot = telebot.TeleBot(TOKEN)

CLICK_FILE = "click_count.json"


try:
    with open(CLICK_FILE, "r", encoding="utf-8") as f:
        click_count = json.load(f)
except FileNotFoundError:
    click_count = {}

def update_click_count(button):
    if button in click_count:
        click_count[button] += 1
    else:
        click_count[button] = 1
    with open(CLICK_FILE, "w", encoding="utf-8") as f:
        json.dump(click_count, f, ensure_ascii=False, indent=4)

@bot.message_handler(commands=['start'])
def start(m):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['🎬Фильмы', '📺Сериалы', 'Популярное', 'Помощь']
    keyboard.add(*[types.KeyboardButton(name) for name in buttons])
    bot.send_message(m.chat.id, 'Выберите категорию:', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text in ['🎬Фильмы', '📺Сериалы', 'Популярное', 'Помощь'])
def main_menu(m):
    update_click_count(m.text)
    if m.text == '🎬Фильмы':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ['Боевики', 'Комедии', 'Драмы', 'Назад']
        keyboard.add(*[types.KeyboardButton(name) for name in buttons])
        bot.send_message(m.chat.id, 'Выберите жанр фильмов:', reply_markup=keyboard)
    elif m.text == '📺Сериалы':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ['Фэнтези', 'Детективы', 'Триллеры', 'Назад']
        keyboard.add(*[types.KeyboardButton(name) for name in buttons])
        bot.send_message(m.chat.id, 'Выберите жанр сериалов:', reply_markup=keyboard)
    elif m.text == 'Популярное':
        bot.send_message(m.chat.id, 'Сейчас популярны: "Дюна 2", "Ведьмак", "Локи"')
    elif m.text == 'Помощь':
        bot.send_message(m.chat.id, 'Напишите /start для перезапуска.')

@bot.message_handler(func=lambda message: message.text in ['Боевики', 'Комедии', 'Драмы', 'Фэнтези', 'Детективы', 'Триллеры', 'Назад'])
def submenu(m):
    update_click_count(m.text)
    if m.text == 'Боевики':
        bot.send_message(m.chat.id, 'Рекомендуем: "Джон Уик", "Безумный Макс"')
    elif m.text == 'Комедии':
        bot.send_message(m.chat.id, 'Рекомендуем: "Клик", "Маска"')
    elif m.text == 'Драмы':
        bot.send_message(m.chat.id, 'Рекомендуем: "Зеленая миля", "1+1"')
    elif m.text == 'Фэнтези':
        bot.send_message(m.chat.id, 'Рекомендуем: "Властелин колец", "Гарри Поттер"')
    elif m.text == 'Детективы':
        bot.send_message(m.chat.id, 'Рекомендуем: "Шерлок", "Настоящий детектив"')
    elif m.text == 'Триллеры':
        bot.send_message(m.chat.id, 'Рекомендуем: "Семь", "Остров проклятых"')
    elif m.text == 'Назад':
        start(m)

@bot.message_handler(commands=['stats'])
def stats(m):
    stats_message = '\n'.join([f'{key}: {value}' for key, value in click_count.items()])
    bot.send_message(m.chat.id, f'Статистика нажатий:\n{stats_message}')

bot.polling(none_stop=True)
