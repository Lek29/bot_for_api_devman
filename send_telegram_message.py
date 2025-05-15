import telegram


def send_telegram_greeting(message_text, bot_token, chat_id):
    print(f"send_telegram_greeting ПОЛУЧИЛ: bot_token='{bot_token}', chat_id='{chat_id}'")
    bot = telegram.Bot(token=bot_token)
    try:
        bot.send_message(chat_id=chat_id, text=message_text)
        return True, 'Сообщение удачно отправлено'
    except telegram.error.TelegramError as e:
        return False, e


def format_review_notification(attempt):
    lesson_tittle = attempt.get('lesson_title')
    lesson_url = attempt.get('lesson_url')
    is_negative = attempt.get('is_negative')
    notification_message = 'Работа проверена, есть ошибки' if is_negative else 'Работа принята'
    return f'{notification_message} \n \nУрок: "{lesson_tittle}" \n \nСсылка: {lesson_url}'
