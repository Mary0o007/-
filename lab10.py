import ssl
import requests
from telebot import TeleBot, apihelper

TG_TOKEN = ''
bot = TeleBot(TG_TOKEN)


VK_TOKEN = ''
VK_USER_ID = 000
VK_API_URL = 'https://api.vk.com/method/'
VK_API_VERSION = '5.131'

class UnsafeHTTPSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        kwargs['ssl_context'] = ctx
        return super().init_poolmanager(*args, **kwargs)

unsafe_session = requests.Session()
unsafe_session.mount("https://", UnsafeHTTPSAdapter())
apihelper.session = unsafe_session

def get_last_post_id():
    response = requests.get(
        f'{VK_API_URL}wall.get',
        params={
            'access_token': VK_TOKEN,
            'owner_id': VK_USER_ID,
            'count': 1,
            'v': VK_API_VERSION
        },
        verify=False
    )
    data = response.json()
    if 'response' in data:
        return data['response']['items'][0]['id']
    else:
        print("Ошибка получения поста:", data)
        return None

def send_vk_comment(post_id, message):
    response = requests.post(
        f'{VK_API_URL}wall.createComment',
        params={
            'access_token': VK_TOKEN,
            'owner_id': VK_USER_ID,
            'post_id': post_id,
            'message': message,
            'v': VK_API_VERSION
        },
        verify=False
    )
    return response.json()

@bot.message_handler(content_types=['text'])
def forward_to_vk(message):
    post_id = get_last_post_id()
    if post_id:
        result = send_vk_comment(post_id, message.text)
        if 'response' in result:
            bot.send_message(message.chat.id, "Сообщение успешно отправлено в VK!")
        else:
            bot.send_message(message.chat.id, f"Ошибка при отправке: {result}")
    else:
        bot.send_message(message.chat.id, "Не удалось получить последний пост на стене.")

bot.polling(none_stop=True)
