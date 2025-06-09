pip install pyTelegramBotAPI

import telebot
import json

TOKEN = ""  
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Сохраняем сообщение в JSON-файл
    data = {"user": message.from_user.username, "message": message.text}
    with open("messages.json", "w", encoding="utf-8") as f:
        json.dump(data, f)

    bot.send_message(message.chat.id, "Ваше сообщение сохранено!")

bot.polling(none_stop=True)
