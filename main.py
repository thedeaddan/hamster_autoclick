import requests
import time
import threading
import random
from config import tokens

# Константы для URL
BASE_URL = 'https://api.hamsterkombat.io/clicker'
TAP_URL = f'{BASE_URL}/tap'
SYNC_URL = f'{BASE_URL}/sync'
BUY_BOOST_URL = f'{BASE_URL}/buy-boost'
CHECK_TASK_URL = f'{BASE_URL}/check-task'

# Генерация заголовков для запроса
def generate_headers(token):
    return {
        'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'api.hamsterkombat.io',
        'Origin': 'https://hamsterkombat.io',
        'Referer': 'https://hamsterkombat.io/',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-site',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
        'accept': 'application/json',
        'authorization': f'Bearer {token}',
        'content-type': 'application/json',
        'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

# Покупка буста
def buy_boost(boost_id, headers, user_id):
    payload = {
        "boostId": boost_id,
        "timestamp": int(time.time())
    }
    response = requests.post(BUY_BOOST_URL, headers=headers, json=payload)
    print(f'[{user_id}] Отправлен запрос на покупку буста: {boost_id}, ответ: {response.status_code}')

# Проверка ежедневной задачи
def daily_check(headers, user_id):
    payload = {
        "taskId": "streak_days",
    }
    response = requests.post(CHECK_TASK_URL, headers=headers, json=payload)
    print(f'[{user_id}] Отправлен запрос на ежедневную награду, ответ: {response.status_code}')

# Получение бустов
def get_boosts(token):
    while True:
        headers = generate_headers(token)
        response = requests.post(SYNC_URL, headers=headers)
        info = response.json()
        user_id = info.get("clickerUser").get("id")
        buy_boost("BoostFullAvailableTaps", headers, user_id)
        daily_check(headers, user_id)
        time.sleep(3600)  # Спим 3600 секунд (1 час)

# Создание потока для выполнения запросов
def create_thread(token):
    while True:
        headers = generate_headers(token)
        response = requests.post(SYNC_URL, headers=headers)
        info = response.json()
        user = info.get("clickerUser")
        available_taps = int(user.get("availableTaps"))
        passive_sec = user.get("earnPassivePerSec")
        passive_hour = user.get("earnPassivePerHour")
        user_id = user.get("id")

        if available_taps > 500:
            available_taps = random.randint(10, 100)

        payload = {
            "count": available_taps,
            "availableTaps": 0,
            "timestamp": int(time.time())
        }
        response = requests.post(TAP_URL, headers=headers, json=payload)
        json_data = response.json()
        balance = int(json_data.get('clickerUser').get('balanceCoins'))

        # Вывод результата
        print("=" * 5, f"Юзер {user_id}", "=" * 5)
        print(f"Баланс: {balance} мон. | Заработок в сек/час: {int(passive_sec)}/{int(passive_hour)} мон.")
        print(f"Кликов отправлено: {available_taps}")

        if response.status_code == 200:
            wait = random.randint(7, 20)
        else:
            print(f"Внимание! Статус-код: {response.status_code}! Ожидание повышено.")
            wait = random.randint(300, 600)
        print(f"Ожидание: {wait} сек.")
        time.sleep(wait)

# Запуск потоков для каждого токена
for token in tokens:
    threading.Thread(target=create_thread, args=(token,)).start()
    threading.Thread(target=get_boosts, args=(token,)).start()
