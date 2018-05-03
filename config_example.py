"""
Config file

Заходим на https://my.telegram.org/auth, проходим авторизацию
Заходим в API development tools, регистрируемся там и получаем App api_id и api_hash

Вбиваем их ниже:
"""

API_ID = '12345123'
API_HASH = '12341awdlkmd1235130280421jnldaw'

# пишем номер телефона в формате +79261234567
PHONE = '+79261234567'

# если у аккаунта включена доп. защита в виде пароля - указываем его здесь
PW = 'twoStepAuthPassword'

# пишем название чата, который нужно почистить, например '@chatusername'
CHAT_TO_CLEAN = '@chatusername'

# настройки кол-ва сообщений
NUMBER_OF_CHUNKS = 30  # Сколько подходов делать
CHUNK_SIZE = 1000  # Сколько сообщений нужно просканировать за подход
