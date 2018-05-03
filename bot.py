from datetime import datetime
from time import sleep

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import DeleteMessagesRequest
from telethon.tl.functions.messages import GetHistoryRequest

import config

db = {}


def chunks(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def print_header(text):
    print('====================')
    print('= {} ='.format(text))
    print('====================')


class DeleterClient(TelegramClient):
    def __init__(self, session_user_id, user_phone, api_id, api_hash):
        super().__init__(session_user_id, api_id, api_hash)

        self.messages_to_delete = set()
        self.chunk_size = config.CHUNK_SIZE

        # Проверка соеденения с сервером. Проверка данных приложения
        print('Connecting to Telegram servers...')
        if not self.connect():
            print('Initial connection failed. Retrying...')
            if not self.connect():
                print('Could not connect to Telegram servers.')
                return

        # Проверка авторизирован ли юзер под сессией
        if not self.is_user_authorized():
            print('First run. Sending code request...')
            self.send_code_request(user_phone)

            self_user = None
            while self_user is None:
                code = input('Enter the code you just received: ')
                try:
                    self_user = self.sign_in(user_phone, code, password=config.PW)

                # Two-step verification may be enabled
                except SessionPasswordNeededError:
                    # pw = input('Two step verification is enabled. Please enter your password: ')
                    self_user = self.sign_in(password=config.PW)

        entity = self.get_entity(config.CHAT_TO_CLEAN)
        db[entity.id] = 0

    def run(self):
        peer = self.get_entity(config.CHAT_TO_CLEAN)
        self.filter_messages_from_chunk(peer)
        result = self.delete_messages_from_peer(peer)
        return result

    def delete_messages_from_peer(self, peer):
        messages_to_delete = list(self.messages_to_delete)
        print_header('УДАЛЕНИЕ {} СООБЩЕНИЙ В ЧАТЕ {}'.format(len(messages_to_delete), peer.title))
        for chunk_data in chunks(messages_to_delete, 100):
            # Поскольку удалить больше чем 100 сообщеий мы не можем - разделяем на маленькие кусочки
            r = self(DeleteMessagesRequest(peer, chunk_data))
            if r.pts_count:
                print('{} Удалено сообщений: {}'.format(datetime.now(), r.pts_count))
            sleep(1)
        return True

    def filter_messages_from_chunk(self, peer):
        messages = []

        for n in range(config.NUMBER_OF_CHUNKS):
            msgs, status = self.get_chunk(peer, n)
            messages.extend(msgs)
            if not status:
                break

        # Генератор который фильтрует сообщения (можно накинуть доп. условий)
        filter_generator = (msg.id for msg in messages)
        self.messages_to_delete.update(filter_generator)

    def get_chunk(self, peer, chunk_number, limit=100, offset_date=None, offset_id=0, max_id=0, min_id=0):
        add_offset = db.get(peer.id)
        print_header('ВЫКАЧКА ЧАНКА #{}'.format(chunk_number))
        local_offset = 0
        messages = []

        while local_offset < self.chunk_size:
            # По скольку лимит на выкачку сообщений 100 - выкачиваем по 100 и делаем шаг равный выкачанному ранее
            result = self(GetHistoryRequest(
                peer,
                limit=limit,
                offset_date=offset_date,
                offset_id=offset_id,
                max_id=max_id,
                min_id=min_id,
                add_offset=add_offset,
                hash=0
            ))

            if result.messages:
                print('Скачано сообщений: {}. Сдвиг: {}.'.format(len(result.messages), add_offset))
                messages.extend(result.messages)
                add_offset += len(result.messages)
                local_offset += len(result.messages)
                # Записываем значение смещения для данной группы
                db[peer.id] = add_offset

            else:
                print_header('ПОЛУЧЕНО 0 СООБЩЕНИЙ. ВЫКАЧКА ЧАНКА #{} ОСТАНОВЛЕНА, '
                             'СКОРЕЕ ВСЕГО ДОШЛО ДО КОНЦА ЧАТА'.format(chunk_number))
                return messages, False

        return messages, True


client = DeleterClient('Deleter', config.PHONE, config.API_ID, config.API_HASH)
client.run()
