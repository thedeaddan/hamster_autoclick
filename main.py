import requests
import time
import threading
import random
import traceback
from config import tokens

# Константы для URL
BASE_URL = 'https://api.hamsterkombat.io/clicker'
TAP_URL = f'{BASE_URL}/tap'
SYNC_URL = f'{BASE_URL}/sync'
BUY_BOOST_URL = f'{BASE_URL}/buy-boost'
CHECK_TASK_URL = f'{BASE_URL}/check-task'
#Чем выше процент, тем менее выгодные карточки будет покупать бот, рекомендованное значение: 100-150
profit_percent_global = 200

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
        try:
            headers = generate_headers(token)
            response = requests.post(SYNC_URL, headers=headers)
            if response.status_code in [200,400]:
                info = response.json()
                user_id = info.get("clickerUser").get("id")
                buy_boost("BoostFullAvailableTaps", headers, user_id)
                daily_check(headers, user_id)
                time.sleep(3600)  # Спим 3600 секунд (1 час)
        except:
            print(response.text)


def calc_profit(price,profit_per_hour):
    if price != 0 and profit_per_hour != 0:
        profit_percent = price/10/profit_per_hour*100
        if profit_percent <= profit_percent_global:
            return True
        else:
            return False
    else:
        return False

def check_maxlevel(upgrade):
    try:
        level = upgrade.get("condition").get("level")
        if upgrade.get("maxLevel") == level:
            return True
        else:
            False
    except:
        return False
    
def check_cooldown(upgrade):
    if upgrade.get("totalCooldownSeconds") != None:
        return False
    else:
        return True

def get_profit_upgrades(token):
    while True:
        try:
            headers = generate_headers(token)
            response = requests.post("https://api.hamsterkombat.io/clicker/upgrades-for-buy", headers=headers)
            info = requests.post(SYNC_URL, headers=headers).json()
            user = info.get("clickerUser")
            user_id = user.get("id")
            upgrades = response.json().get("upgradesForBuy")
            for upgrade in upgrades:
                profit = int(upgrade.get("profitPerHourDelta"))
                price = int(upgrade.get("price"))
                name = upgrade.get("name")
                upgrade_id = upgrade.get("id")
                unlocked = upgrade.get("isAvailable")
                expired = upgrade.get("isExpired")
                if calc_profit(price,profit) and not expired and not check_maxlevel(upgrade) and check_cooldown(upgrade):
                    if unlocked:
                        payload = {
                            "upgradeId": upgrade_id,
                            "timestamp": int(time.time())
                        }
                        response = requests.post("https://api.hamsterkombat.io/clicker/buy-upgrade", json = payload, headers=headers)
                        if response.status_code == 200:
                            print(f"[{user_id}][{name}] Куплено!")
                        else:
                            print(f"[{user_id}][{name}] Ошибка, код: {response.status_code}")
                        time.sleep(2)
            time.sleep(3)
        except:
            print(traceback.format_exc())
            pass
            


# Создание потока для выполнения запросов
def create_thread(token):
    while True:
        try:
            headers = generate_headers(token)
            response = requests.post(SYNC_URL, headers=headers)
            if response.status_code == 200:
                info = response.json()
                user = info.get("clickerUser")
                available_taps = int(user.get("availableTaps"))
                passive_sec = user.get("earnPassivePerSec")
                passive_hour = user.get("earnPassivePerHour")
                user_id = user.get("id")

                if available_taps > 500:
                    available_taps = random.randint(500, 3000)

                payload = {
                    "count": available_taps,
                    "availableTaps": 0,
                    "timestamp": int(time.time())
                }
                response = requests.post(TAP_URL, headers=headers, json=payload)
                if response.status_code == 200:
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
        except:
            print(response.text)

# Запуск потоков для каждого токена
for token in tokens:
    threading.Thread(target=create_thread, args=(token,)).start()
    threading.Thread(target=get_boosts, args=(token,)).start()
    #threading.Thread(target=get_profit_upgrades, args=(token,)).start()
