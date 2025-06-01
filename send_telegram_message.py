import telegram
import logging


module_logger = logging.getLogger('devman_bot.sender')

def init_telegram_bot(bot_token):
    try:
        bot = telegram.Bot(token=bot_token)
        bot_info = bot.get_me()
        module_logger.info(f'Бот успешно активирован. {bot_info.username}')
        return bot
    except telegram.error.InvalidToken:
        module_logger.error('Ошибка: Неверный токен Telegram бота')
        return None
    except Exception as e:
        module_logger.error(f'Не удалось инициализировать Telegram бота: {e}", exc_info=True')
        return None


def send_telegram_message(bot: telegram.Bot, chat_id, message_text):
    if not bot:
        module_logger.error("Попытка отправить сообщение через неинициализированный бот.")
        return False, "Бот не инициализирован"

    try:
        bot.send_message(chat_id=chat_id, text=message_text)
        return True, 'Сообщение удачно отправлено'
    except telegram.error.TelegramError as e:
        module_logger.error(f"Ошибка Telegram при отправке сообщения в чат {chat_id}: {e}")
        return False, e


def format_review_notification(attempt):
    lesson_tittle = attempt.get('lesson_title')
    lesson_url = attempt.get('lesson_url')
    is_negative = attempt.get('is_negative')
    notification_message = 'Работа проверена, есть ошибки' if is_negative else 'Работа принята'
    return f'{notification_message} \n \nУрок: "{lesson_tittle}" \n \nСсылка: {lesson_url}'
