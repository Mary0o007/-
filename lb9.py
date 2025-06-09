import telebot
from telebot import types

TOKEN = ""
bot = telebot.TeleBot(TOKEN)

# Счетчик голосов
votes = {'like': 0, 'dislike': 0, 'option1': 0, 'option2': 0, 'option3': 0, 'option4': 0, 'option5': 0}

def get_vote_results():
    return "\n".join([f"{key}: {value}" for key, value in votes.items()])

@bot.message_handler(commands=['start'])
def start(m):
    # Инлайн меню при запуске
    keyboard = types.InlineKeyboardMarkup()
    buttons = [
        types.InlineKeyboardButton('🎬 Фильмы', callback_data='films'),
        types.InlineKeyboardButton('📺 Сериалы', callback_data='series'),
        types.InlineKeyboardButton('📊 Голосование', callback_data='vote'),
        types.InlineKeyboardButton('👍 Оценка', callback_data='rating')
    ]
    keyboard.add(*buttons)
    bot.send_message(m.chat.id, 'Добро пожаловать! Выберите категорию:', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == 'films':
        send_inline_menu(call.message.chat.id, 'Выберите жанр фильмов:', ['Боевики', 'Комедии', 'Драмы'])
    elif call.data == 'series':
        send_inline_menu(call.message.chat.id, 'Выберите жанр сериалов:', ['Фэнтези', 'Детективы', 'Триллеры'])
    elif call.data == 'vote':
        send_vote_menu(call.message.chat.id)
    elif call.data == 'rating':
        send_like_menu(call.message.chat.id)
    elif call.data == 'back':
        # Возвращаем пользователя в основное меню
        start(call.message)
    elif call.data in votes:
        # Обрабатываем голосование
        votes[call.data] += 1
        bot.answer_callback_query(call.id, text='Ваш голос учтен!')
        bot.edit_message_text(f'📊 Результаты голосования:\n{get_vote_results()}',
                              call.message.chat.id, call.message.message_id)
        send_vote_menu(call.message.chat.id)  # Обновляем меню
    else:
        # Рекомендации по категориям
        recommendations = {
            'Боевики': 'Рекомендуем: "Джон Уик", "Безумный Макс"',
            'Комедии': 'Рекомендуем: "Маска", "Клик"',
            'Драмы': 'Рекомендуем: "Зеленая миля", "1+1"',
            'Фэнтези': 'Рекомендуем: "Властелин колец", "Гарри Поттер"',
            'Детективы': 'Рекомендуем: "Шерлок", "Настоящий детектив"',
            'Триллеры': 'Рекомендуем: "Семь", "Остров проклятых"'
        }
        bot.send_message(call.message.chat.id, recommendations.get(call.data, 'Неизвестная категория'))
        # После вывода рекомендации, отправляем меню снова
        send_inline_menu(call.message.chat.id, 'Выберите жанр:', ['Боевики', 'Комедии', 'Драмы', 'Фэнтези', 'Детективы', 'Триллеры'])

def send_inline_menu(chat_id, text, options):
    keyboard = types.InlineKeyboardMarkup()
    for option in options:
        keyboard.add(types.InlineKeyboardButton(text=option, callback_data=option))
    keyboard.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
    bot.send_message(chat_id, text, reply_markup=keyboard)

def send_vote_menu(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    for i in range(1, 6):
        keyboard.add(types.InlineKeyboardButton(text=f'Вариант {i}', callback_data=f'option{i}'))
    keyboard.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
    bot.send_message(chat_id, 'Выберите вариант:', reply_markup=keyboard)

def send_like_menu(chat_id):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='👍 Мне нравится', callback_data='like'))
    keyboard.add(types.InlineKeyboardButton(text='👎 Мне не нравится', callback_data='dislike'))
    keyboard.add(types.InlineKeyboardButton(text="🔙 Назад", callback_data="back"))
    bot.send_message(chat_id, 'Оцените:', reply_markup=keyboard)

bot.polling(none_stop=True)
