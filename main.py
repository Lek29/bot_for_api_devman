import time
import logging
import requests
from environs import Env, EnvError

from api_devman import get_devman_reviews
from send_telegram_message import (format_review_notification,
                                   send_telegram_message, init_telegram_bot)
from telegram_logging_handler import TelegramLogsHandler


DEVMAN_LONGPOILING_URL = 'https://dvmn.org/api/long_polling/'

logger = logging.getLogger('devman_bot')
logger.setLevel(logging.DEBUG)


console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

formater = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formater)

logger.addHandler(console_handler)

file_handler = logging.FileHandler('bot.log', mode='a', encoding='utf-8')
file_handler.setLevel(logging.DEBUG)
file_formater = logging.Formatter('%(asctime)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
file_handler.setFormatter(file_formater)
logger.addHandler(file_handler)


def main():
    env = Env()
    env.read_env()

    try:
        devman_token = env.str('DEVMAN_TOKEN')
        telegram_bot_token = env.str('TELEGRAM_TOKEN')
        telegram_chat_id = env.str('TELEGRAM_CHAT_ID')
    except EnvError as e:
        logger.error(f'Ошибка конфигурации: {e}', exc_info=True)
        return

    tg_bot = init_telegram_bot(telegram_bot_token)

    if tg_bot:
        telegram_log_handler = TelegramLogsHandler(bot_instance=tg_bot, chat_id=telegram_chat_id)
        telegram_log_handler.setLevel(logging.ERROR)
        telegram_formatter = logging.Formatter('%(levelname)s - %(name)s: %(message)s')
        telegram_log_handler.setFormatter(telegram_formatter)
        logger.addHandler(telegram_log_handler)
        logger.info("Telegram-хэндлер для логов успешно добавлен.")

    else:
        logger.critical("Не удалось инициализировать Telegram бота...")


    current_timestamp = None
    while True:
        logger.info('--------------------------Начинаем постоянный опрос сервера ------------------------')
        try:
            devman_response = get_devman_reviews(DEVMAN_LONGPOILING_URL, devman_token, current_timestamp)
            status = devman_response.get('status')
            logger.debug(f'--- Ответ API получен, статус: {status} ---')

            if status == 'found':
                logger.info('Обнаружены новые проверки')
                current_timestamp = devman_response.get('last_attempt_timestamp', 'ошибка получения current_timestamp')
                new_attempts = devman_response.get('new_attempts', [])

                for attempt in new_attempts:
                    result_check = format_review_notification(attempt)
                    success, telegram_dispatch_details = (
                        send_telegram_message(
                            message_text=result_check,
                            bot_token=telegram_bot_token,
                            chat_id=telegram_chat_id
                        )
                    )
                    if success:
                        logger.info(telegram_dispatch_details)
                    else:
                        logger.error('Ошибка отправки сообщения в Telegram: {telegram_dispatch_details}')
            elif status == 'timeout':
                logger.info('Новых проверок нет. Делаем новый запрос.')
                current_timestamp = devman_response.get('timestamp_to_request')

        except requests.exceptions.ReadTimeout:
            logger.warning("Тайм-аут при запросе к Devman API. Повторяем...")
            pass
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Ошибка соединения с Devman API: {e}", exc_info=True)
            time.sleep(5)


if __name__ == '__main__':
    main()
