import telegram
import requests
from environs import Env


def get_notifications(url, headers):
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        if response.json().get('status') == 'timeout':
            params = {
                'timestamp': response.json().get('timestamp_to_request'),
            }
            new_response = requests.get(url, headers=headers, params=params)
            return new_response.json()
        else:
            return response.json()
    except requests.exceptions.ReadTimeout:
        print('Ошибка времени ожидания')
    except ConnectionError:
        print('Сбой соединения!')


def main():
    env = Env()
    env.read_env()
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'{env.str('AUTHORIZATION_TOKEN')}'
    }
    bot_token = env.str('TELEGRAM_TOKEN')
    chat_id = env.str('TELEGRAM_CHAT_ID')
    bot = telegram.Bot(token=bot_token)
    while True:
        try:
            notifications = get_notifications(url, headers)
            if notifications['status'] == 'found':
                for notification in notifications['new_attempts']:
                    if notification['is_negative']:

                        bot.send_message(chat_id=chat_id,
                                         text=f'<a href="{notification["lesson_url"]}">Урок {notification["lesson_title"]} </a> НЕ ПРИНЯТ.',
                                         parse_mode=telegram.ParseMode.HTML)

                    else:
                        bot.send_message(chat_id=chat_id,
                                         text=f'<a href="{notification["lesson_url"]}">Урок {notification["lesson_title"]}</a> ПРИНЯТ.',
                                         parse_mode=telegram.ParseMode.HTML)
        except telegram.error.TelegramError:
            print('Ошибка!')
        except telegram.error.NetworkError:
            print('Ошибка подключения')

if __name__ == '__main__':
    main()
