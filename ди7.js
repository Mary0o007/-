const TelegramBot = require("node-telegram-bot-api");
const fs = require("fs");

const TOKEN = "ВАШ_ТОКЕН_ОТ_BOTFATHER";
const bot = new TelegramBot(TOKEN, { polling: true });

bot.on("message", (msg) => {
    const chatId = msg.chat.id;
    const userMessage = msg.text;
    const userName = msg.from.username || "Аноним";

    // Сохраняем сообщение в JSON
    const data = { user: userName, message: userMessage };
    fs.writeFileSync("messages.json", JSON.stringify(data, null, 2));

    bot.sendMessage(chatId, "Ваше сообщение сохранено!");
});

console.log("Бот запущен!");
