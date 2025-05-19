import time

import requests
from environs import Env, EnvError

from api_devman import get_devman_reviews
from send_telegram_message import (format_review_notification,
                                   send_telegram_greeting)


DEVMAN_LONGPOILING_URL = 'https://dvmn.org/api/long_polling/'


def main():
    env = Env()
    env.read_env()

    try:
        devman_token = env.str('DEVMAN_TOKEN')
        telegram_bot_token = env.str('TELEGRAM_TOKEN')
        telegram_chat_id = env.str('TELEGRAM_CHAT_ID')
    except EnvError as e:
        print(f'Ошибка конфигурации в main.py: Не удалось загрузить одну из переменных '
              f'(devman_token, telegram_bot_token, telegram_chat_id). Ошибка: {e}')
        return

    current_timestamp = None
    while True:
        print('--------------------------Начинаем постоянный опрос сервера ------------------------')
        try:
            devman_response = get_devman_reviews(DEVMAN_LONGPOILING_URL, devman_token, current_timestamp)
            status = devman_response.get('status')
            print(f'--- Ответ API получен, статус: {status} ---')

            if status == 'found':
                print('Обнаружены новые проверки')
                current_timestamp = devman_response.get('last_attempt_timestamp', 'ошибка получения current_timestamp')
                new_attempts = devman_response.get('new_attempts', [])

                for attempt in new_attempts:
                    result_check = format_review_notification(attempt)
                    print('---- Детали новых проверок ----')
                    success, telegram_dispatch_details = (
                        send_telegram_greeting(
                            message_text=result_check,
                            bot_token=telegram_bot_token,
                            chat_id=telegram_chat_id
                        )
                    )
                    if success:
                        print(telegram_dispatch_details)
                    else:
                        print(f'Ошибка отправки сообщения в Telegram: {telegram_dispatch_details}')
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
