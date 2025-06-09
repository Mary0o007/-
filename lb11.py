
import telebot
from telebot import types
import requests
import xml.dom.minidom
from datetime import datetime, timedelta
import matplotlib
matplotlib.use('Agg')  # Важно: до импорта pyplot
import matplotlib.pyplot as plt
import numpy as np
import os

TOKEN = ''
bot = telebot.TeleBot(TOKEN)

currency_codes = {
    "AMD": "🇦🇲Армянский драм",
    "USD": "💵Доллар США"
}

name_to_code = {v: k for k, v in currency_codes.items()}
user_data = {}
scatter_data = {}

def get_main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in currency_codes.values():
        markup.add(types.KeyboardButton(name))
    markup.add(types.KeyboardButton("🔄 Изменить валюту"))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Выберите валюту:",
        reply_markup=get_main_keyboard()
    )

@bot.message_handler(commands=['scatter'])
def scatter_dates_only(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введите начальную дату (ДД.ММ.ГГГГ):")
    bot.register_next_step_handler(message, get_scatter_start)

def get_scatter_start(message):
    chat_id = message.chat.id
    text = message.text.strip()
    if not is_valid_date(text):
        return bot.send_message(chat_id, "Неверный формат. Повторите ввод начальной даты.")
    scatter_data[chat_id] = {'start': datetime.strptime(text, "%d.%m.%Y").date()}
    bot.send_message(chat_id, "Введите конечную дату (ДД.ММ.ГГГГ):")
    bot.register_next_step_handler(message, get_scatter_end)

def get_scatter_end(message):
    chat_id = message.chat.id
    text = message.text.strip()
    if not is_valid_date(text):
        return bot.send_message(chat_id, "Неверный формат. Повторите ввод конечной даты.")
    
    scatter_data[chat_id]['end'] = datetime.strptime(text, "%d.%m.%Y").date()
    bot.send_message(chat_id, "⏳ Строю диаграмму рассеивания по валютам...")

    try:
        start = scatter_data[chat_id]['start']
        end = scatter_data[chat_id]['end']
        codes = list(currency_codes.keys())
        if len(codes) < 2:
            return bot.send_message(chat_id, "Нужно как минимум 2 валюты для анализа.")

        r1 = get_currency_series(codes[0], start, end)
        r2 = get_currency_series(codes[1], start, end)

        min_len = min(len(r1), len(r2))
        if min_len < 2:
            return bot.send_message(chat_id, "Недостаточно данных для построения графика.")

        r1, r2 = r1[:min_len], r2[:min_len]

        corr = np.corrcoef(r1, r2)[0][1]

        # Построение графика
        plt.figure(figsize=(7, 7))
        plt.scatter(r1, r2, alpha=0.7, color='mediumpurple', label='Данные')

        # Линия тренда
        z = np.polyfit(r1, r2, 1)
        p = np.poly1d(z)
        plt.plot(r1, p(r1), "r--", label='Линия тренда')

        # Подписи и оформление
        plt.title(f"Рассеяние: {currency_codes[codes[0]]} vs {currency_codes[codes[1]]}", fontsize=14)
        plt.xlabel(currency_codes[codes[0]])
        plt.ylabel(currency_codes[codes[1]])
        plt.grid(True)
        plt.legend()
        plt.text(min(r1), max(r2), f"Корреляция: {corr:.2f}", fontsize=12, color='darkgreen')

        filename = f"scatter_{chat_id}.png"
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()

        with open(filename, 'rb') as photo:
            bot.send_photo(chat_id, photo, caption=f"📈 Корреляция между валютами: {corr:.2f}")
        os.remove(filename)
    except Exception as e:
        bot.send_message(chat_id, f"⚠️ Ошибка при построении графика: {e}")
    finally:
        scatter_data.pop(chat_id, None)


@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    chat_id = message.chat.id
    text = message.text.strip()

    if chat_id in scatter_data:
        return

    if text in currency_codes.values():
        user_data[chat_id] = {'currency': name_to_code[text]}
        bot.send_message(chat_id, f"Вы выбрали валюту: {text}\nТеперь введите дату в формате ДД.ММ.ГГГГ:")
    
    elif text == "🔄 Изменить валюту":
        bot.send_message(chat_id, "Выберите новую валюту:", reply_markup=get_main_keyboard())
    
    elif is_valid_date(text):
        if chat_id not in user_data or 'currency' not in user_data[chat_id]:
            bot.send_message(chat_id, "Сначала выберите валюту.")
            return
        
        currency = user_data[chat_id]['currency']
        date = datetime.strptime(text, "%d.%m.%Y").date()
        date_str = date.strftime("%d/%m/%Y")

        url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"
        r = requests.get(url)
        dom = xml.dom.minidom.parseString(r.text)
        dom.normalize()

        elements = dom.getElementsByTagName("Valute")
        rate = None
        for node in elements:
            char_code = node.getElementsByTagName("CharCode")[0].childNodes[0].nodeValue
            if char_code == currency:
                value = node.getElementsByTagName("Value")[0].childNodes[0].nodeValue
                nominal = node.getElementsByTagName("Nominal")[0].childNodes[0].nodeValue
                rate = f"{nominal} {currency_codes[currency]} = {value} руб."
                break

        if rate:
            bot.send_message(chat_id, f"📅 Курс на {text}:\n{rate}", reply_markup=get_main_keyboard())
        else:
            bot.send_message(chat_id, "❌ Курс на указанную дату не найден.")
    else:
        bot.send_message(chat_id, "Пожалуйста, выберите валюту или введите дату в формате ДД.ММ.ГГГГ.")

def is_valid_date(date_text):
    try:
        datetime.strptime(date_text, "%d.%m.%Y")
        return True
    except ValueError:
        return False

def get_currency_series(currency_code, start_date, end_date):
    date = start_date
    rates = []
    while date <= end_date:
        url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date.strftime('%d/%m/%Y')}"
        try:
            r = requests.get(url)
            dom = xml.dom.minidom.parseString(r.text)
            dom.normalize()
            elements = dom.getElementsByTagName("Valute")
            rate = None
            for node in elements:
                char_code = node.getElementsByTagName("CharCode")[0].childNodes[0].nodeValue
                if char_code == currency_code:
                    value = node.getElementsByTagName("Value")[0].childNodes[0].nodeValue
                    nominal = int(node.getElementsByTagName("Nominal")[0].childNodes[0].nodeValue)
                    value = float(value.replace(',', '.')) / nominal
                    rate = value
                    break
            if rate:
                rates.append(rate)
        except:
            pass
        date += timedelta(days=1)
    return rates

bot.polling(none_stop=True)
