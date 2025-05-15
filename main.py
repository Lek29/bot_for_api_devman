import time

import requests
from environs import Env, EnvError

from api_devman import get_devman_reviews
from send_telegram_message import (format_review_notification,
                                   send_telegram_greeting)

devman_longpoiling_url = 'https://dvmn.org/api/long_polling/'


def main():
    env = Env()
    env.read_env()

    try:
        DEVMAN_TOKEN = env.str('DEVMAN_TOKEN')
        TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_TOKEN')
        TELEGRAM_CHAT_ID = env.str('TELEGRAM_CHAT_ID')
    except EnvError as e:
        print(f'Ошибка конфигурации в main.py: Не удалось загрузить одну из переменных '
              f'(DEVMAN_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID). Ошибка: {e}')
        return

    current_timestamp = None
    while True:
        print('--------------------------Начинаем постоянный опрос сервера ------------------------')
        try:
            devman_response = get_devman_reviews(devman_longpoiling_url, DEVMAN_TOKEN, current_timestamp)
            status = devman_response.get('status')
            print(f'--- Ответ API получен, статус: {status} ---')

            if status == 'found':
                print('Обнаружены новые проверки')
                current_timestamp = devman_response.get('last_attempt_timestamp', 'ошибка получения current_timestamp')
                new_attempts = devman_response.get('new_attempts', [])

                if isinstance(new_attempts, list):
                    for attempt in new_attempts:
                        result_check = format_review_notification(attempt)
                        print('---- Детали новых проверок ----')
                        success, telegram_dispatch_details = (
                            send_telegram_greeting(
                                message_text=result_check,
                                bot_token=TELEGRAM_BOT_TOKEN,
                                chat_id=TELEGRAM_CHAT_ID
                            )
                        )
                        if success:
                            print(telegram_dispatch_details)
                        else:
                            print(f'Ошибка отправки сообщения в Telegram: {telegram_dispatch_details}')
                else:
                    print(f'new_attempts не является списком. Получено {type(new_attempts)}')
            elif status == 'timeout':
                print('Новых проверок нет. Делаем новый запрос.')
                current_timestamp = devman_response.get('timestamp_to_request')


        except requests.exceptions.ReadTimeout:
            pass
        except requests.exceptions.ConnectionError as e:
            print(f'Сеть пропала. Ошибка {e}')
            time.sleep(5)


if __name__ == '__main__':
    main()
