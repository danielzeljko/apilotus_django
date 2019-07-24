import requests
from lotus_auth.models import LotusUser


class TelegramBot(object):
    def __init__(self):
        self.base_url = 'https://api.telegram.org/bot' + '675022460:AAHB6q5tqZdPd0cyXxVzE-XBm_IolohXYm0'

    def send_message_by_id(self, msg, chat_id):
        url = self.base_url + '/sendMessage?chat_id={}&text={}'.format(chat_id, msg)
        requests.get(url)

    def send_message(self, msg):
        users = LotusUser.objects.all()
        for user in users:
            if user.bot_enable:
                self.send_message_by_id(msg, user.bot)


# telegram_bot = TelegramBot()
# telegram_bot.send_message_by_id('test message', '558667560')
