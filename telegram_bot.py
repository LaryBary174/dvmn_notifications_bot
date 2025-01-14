import time

import telegram
import requests
from environs import Env


def get_notifications(url, headers):
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    notifications = response.json()
    if notifications['status'] == 'timeout':
        params = {
            'timestamp': notifications['timestamp_to_request'],
        }
        repeated_response = requests.get(url, headers=headers, params=params)
        repeated_response.raise_for_status()
        return repeated_response.json()
    else:
        return response.json()


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
                    message = 'НЕ ПРИНЯТ' if notification['is_negative'] else 'ПРИНЯТ'
                    bot.send_message(chat_id=chat_id,
                                     text=f'<a href="{notification["lesson_url"]}">Урок {notification["lesson_title"]} </a> {message}.',
                                     parse_mode=telegram.ParseMode.HTML)


        except requests.exceptions.ReadTimeout:
            print('Повтор запроса')
            continue
        except ConnectionError:
            print('Сбой соединения!')
        except telegram.error.TelegramError:
            print('Ошибка!')
            time.sleep(10)
        except telegram.error.NetworkError:
            print('Ошибка подключения')
            time.sleep(10)


if __name__ == '__main__':
    main()
