import time

import telegram
import requests
from environs import Env
from bot_for_logging import get_logger


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
        return notifications


def main():
    env = Env()
    env.read_env()
    url = 'https://dvmn.org/api/long_polling/'
    headers = {
        'Authorization': f'{env.str('AUTHORIZATION_TOKEN')}'
    }
    bot_token = env.str('TELEGRAM_TOKEN')
    bot_log_token = env.str('TG_LOG_TOKEN')
    chat_id = env.str('TELEGRAM_CHAT_ID')
    bot = telegram.Bot(token=bot_token)
    logger_bot = telegram.Bot(token=bot_log_token)
    logger = get_logger(logger_bot, chat_id)
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
            logger.warning('Повтор запроса')

            continue
        except requests.exceptions.ConnectionError:
            logger.error('Ошибка соединения, повторная попытка через 10 секунд')

            time.sleep(10)
        except telegram.error.TelegramError:
            logger.error('Ошибка Телеграмм, повторная попытка через 10 секунд')

            time.sleep(10)
        except telegram.error.NetworkError:
            logger.error('Ошибка подключения, повторная попытка через 10 сек')

            time.sleep(10)


if __name__ == '__main__':
    main()
