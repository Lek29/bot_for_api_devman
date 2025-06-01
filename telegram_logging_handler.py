import logging
import telegram


class TelegramLogsHandler(logging.Handler):
    def __init__(self, bot_instance, chat_id):
        super().__init__()
        self.bot = bot_instance
        self.chat_id = chat_id


    def emit(self, record):
        if not self.bot:
            return

        log_entry = record.message

        TELEGRAM_MSG_MAX_LENGTH = 4000

        if len(log_entry) > TELEGRAM_MSG_MAX_LENGTH:
            log_entry = log_entry[:TELEGRAM_MSG_MAX_LENGTH - 3] + "..."

        try:
            self.bot.send_message(chat_id=self.chat_id, text=log_entry)
        except telegram.error.TelegramError as e:
            print(f"Ошибка при отправке лога в Telegram: {e}")