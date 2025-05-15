import time
from pprint import pprint

import requests
from environs import Env, EnvError

from api_devman import get_devman_review_with_polling
from send_telegram_message import (format_review_notification,
                                   send_telegram_greeting)

env = Env()
env.read_env()


devman_longpoiling_url = 'https://dvmn.org/api/long_polling/'
try:
    DEVMAN_TOKEN = env.str('DEVMAN_TOKEN')
    TELEGRAM_BOT_TOKEN = env.str('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = env.str('TELEGRAM_CHAT_ID')
except EnvError as e:
    print(f'Ошибка конфигурации в main.py: Не удалось загрузить одну из переменных '
          f'(DEVMAN_TOKEN, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID). Ошибка: {e}')


def main():
    print(f'токен: {DEVMAN_TOKEN[:4]}')
    print(f' Url: {devman_longpoiling_url}')

    current_timestump = None
    while True:
        print('--------------------------Начинаем постоянный опрос сервера ------------------------')
        try:
            review_data = get_devman_review_with_polling(devman_longpoiling_url, DEVMAN_TOKEN, current_timestump)
            status = review_data['status']
            print(f'--- Ответ API получен, статус: {status} ---')

            if status == 'found':
                print('Обнаружены новые проверки')
                current_timestump = review_data.get('last_attempt_timestamp', 'ошибка получения current_timestamp')
                new_attempts = review_data.get('new_attempts', 'ошибка получения new_attempts')

                if isinstance(new_attempts, list):
                    for attempt in new_attempts:
                        result_check = format_review_notification(attempt)
                        print('---- Детали новых проверок ----')
                        pprint(new_attempts)
                        success, tlg_response_info =(
                            send_telegram_greeting(
                            message_text=result_check,
                            bot_token=TELEGRAM_BOT_TOKEN,
                            chat_id=TELEGRAM_CHAT_ID
                            )
                        )
                        if success:
                            print(tlg_response_info)
                        else:
                            print(f'Ошибка отправки сообщения в Telegram: {tlg_response_info}')
                else:
                    print(f'new_attempts не является списком. Получено {type(new_attempts)}')
            elif status == 'timeout':
                print('Новых проверок нет. Делаем новый запрос.')
                current_timestump = review_data.get('timestump_to_requsts')
            pprint(review_data)

        except requests.exceptions.ReadTimeout as e:
            print(f'Ошибка. Сервер не ответил за необходимое время. Ошибка {e}')
        except requests.exceptions.ConnectionError as e:
            print(f'Сеть пропала. Ошибка {e}')
        time.sleep(5)


if __name__ == '__main__':
    main()
